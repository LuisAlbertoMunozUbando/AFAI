"""Public, bounded diagnostic queue; run one worker on loopback :8016.
Keep the existing :8015 token gateway untouched. Route /diagnostics paths here.
"""
import asyncio, hashlib, json, os, secrets, sqlite3, time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from diagnostic.models import Intake
from diagnostic.pipeline import analyze, model_id
from diagnostic.pdf_report import render, filename
from diagnostic import archive

STATE=Path(os.getenv('AFAI_DIAGNOSTIC_STATE',str(Path.home()/'.local/share/afai-diagnostics')))
ORIGINS=os.getenv('AFAI_ALLOWED_ORIGINS','https://luisalbertomunozubando.github.io').split(',')
ENABLED=os.getenv('AFAI_DIAGNOSTICS_ENABLED','0')=='1'
LIMIT=int(os.getenv('AFAI_DIAGNOSTIC_DAILY_LIMIT','20'))
IP_LIMIT=int(os.getenv('AFAI_DIAGNOSTIC_IP_DAILY_LIMIT','3'))
TTL=86400

def db():
    conn=sqlite3.connect(STATE/'jobs.sqlite3',timeout=10)
    conn.row_factory=sqlite3.Row
    return conn

def init():
    STATE.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(STATE,0o700)
    with db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, secret TEXT, ip TEXT, created REAL, status TEXT, stage TEXT, payload TEXT, name TEXT, saved INTEGER DEFAULT 0, attempts INTEGER DEFAULT 0)')
        conn.execute("UPDATE jobs SET status='queued',stage='Retomando solicitud' WHERE status='running'")

def update(job,**values):
    with db() as conn:
        conn.execute('UPDATE jobs SET '+','.join(k+'=?' for k in values)+' WHERE id=?',[*values.values(),job])

def cleanup():
    with db() as conn:
        rows=conn.execute('SELECT id FROM jobs WHERE created<?',(time.time()-TTL,)).fetchall()
        for row in rows: (STATE/(row['id']+'.pdf')).unlink(missing_ok=True)
        conn.execute('DELETE FROM jobs WHERE created<?',(time.time()-TTL,))

async def worker():
    while True:
        cleanup()
        with db() as conn:
            row=conn.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY created LIMIT 1").fetchone()
            if row: conn.execute("UPDATE jobs SET status='running',attempts=attempts+1 WHERE id=?",(row['id'],))
        if not row:
            await asyncio.sleep(1);continue
        job=row['id']
        if row['attempts']>=2:
            update(job,status='failed',stage='El proceso fue interrumpido; vuelve a intentarlo.',payload='')
            continue
        try:
            payload=Intake.model_validate_json(row['payload'])
            async def progress(stage): update(job,stage=stage)
            report,review,model=await analyze(payload,progress)
            name=filename(payload,job)
            path=STATE/(job+'.pdf')
            await asyncio.to_thread(render,path,payload,report,review,model,job)
            update(job,name=name,stage='Guardando copia privada en Google Drive')
            saved=False
            for attempt in range(3):
                try:
                    await asyncio.to_thread(archive.upload,path,name);saved=True;break
                except Exception:
                    if attempt<2: await asyncio.sleep(2*(attempt+1))
            update(job,status='ready',stage='PDF listo' if saved else 'PDF listo; la copia en Drive no pudo confirmarse',saved=int(saved),payload='')
        except asyncio.CancelledError: raise
        except Exception:
            update(job,status='failed',stage='No se pudo completar el diagnóstico. Intenta nuevamente más tarde.',payload='')

@asynccontextmanager
async def lifespan(app):
    init()
    task=asyncio.create_task(worker())
    yield
    task.cancel()
    try: await task
    except asyncio.CancelledError: pass

app=FastAPI(title='AFAI Automation Diagnostics',lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)
app.add_middleware(CORSMiddleware,allow_origins=ORIGINS,allow_methods=['GET','POST'],allow_headers=['Content-Type','Authorization','Idempotency-Key'])

@app.middleware('http')
async def boundaries(request,call_next):
    if request.method=='POST':
        if request.headers.get('origin') not in ORIGINS:
            return __import__('fastapi').responses.JSONResponse({'detail':'Origen no permitido'},status_code=403)
        size=0;chunks=[]
        async for chunk in request.stream():
            size+=len(chunk)
            if size>24000:
                return __import__('fastapi').responses.JSONResponse({'detail':'Solicitud demasiado grande'},status_code=413)
            chunks.append(chunk)
        request._body=b''.join(chunks)
    response=await call_next(request)
    response.headers['Cache-Control']='no-store'
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    return response

_ready=(0,False)
_ready_lock=asyncio.Lock()
async def readiness():
    global _ready
    if not ENABLED: return False
    if time.time()-_ready[0]<60: return _ready[1]
    async with _ready_lock:
        if time.time()-_ready[0]<60: return _ready[1]
        try:
            await model_id()
            await asyncio.to_thread(archive.check)
            good=True
        except Exception: good=False
        _ready=(time.time(),good)
        return good


@app.get('/diagnostics/health')
async def health():
    return {'ready':await readiness(),'download_ttl_hours':24}

@app.post('/diagnostics',status_code=202)
async def submit(payload:Intake,request:Request):
    if not await readiness(): raise HTTPException(503,'Servicio temporalmente no disponible')
    # Unpredictable key supports retries without generating duplicate jobs. Also acts as capability secret.
    key=request.headers.get('idempotency-key','')
    if not __import__('re').fullmatch(r'[A-Za-z0-9_-]{32,128}',key): raise HTTPException(400,'Identificador de solicitud no válido')
    digest=hashlib.sha256(key.encode()).hexdigest()
    # Only trust Cloudflare IP when requests arrive from the local tunnel, explicitly configured.
    host=request.client.host if request.client else 'unknown'
    if host in ('127.0.0.1','::1') and os.getenv('AFAI_TRUST_CLOUDFLARE','0')=='1':
        host=request.headers.get('cf-connecting-ip',host)
    ip=hashlib.sha256((host+time.strftime('%Y-%m-%d',time.gmtime())).encode()).hexdigest()
    now=time.time()
    with db() as conn:
        conn.execute('BEGIN IMMEDIATE')
        old=conn.execute('SELECT id FROM jobs WHERE secret=? AND created>?',(digest,now-TTL)).fetchone()
        if old: return {'id':old['id']}
        total=conn.execute('SELECT count(*) FROM jobs WHERE created>?',(now-TTL,)).fetchone()[0]
        per_ip=conn.execute('SELECT count(*) FROM jobs WHERE ip=? AND created>?',(ip,now-TTL)).fetchone()[0]
        pending=conn.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','running')").fetchone()[0]
        if total>=LIMIT or per_ip>=IP_LIMIT: raise HTTPException(429,'Límite de diagnósticos alcanzado. Vuelve mañana.')
        if pending>=5: raise HTTPException(429,'Estamos procesando otras solicitudes. Intenta más tarde.')
        job=uuid4().hex
        conn.execute('INSERT INTO jobs(id,secret,ip,created,status,stage,payload) VALUES (?,?,?,?,?,?,?)',
            (job,digest,ip,now,'queued','En cola para análisis',payload.model_dump_json()))
    return {'id':job}

def authorized(job,request):
    auth=request.headers.get('authorization','')
    key=auth[7:] if auth.startswith('Bearer ') else ''
    with db() as conn: row=conn.execute('SELECT * FROM jobs WHERE id=? AND created>?',(job,time.time()-TTL)).fetchone()
    if not row or not secrets.compare_digest(row['secret'],hashlib.sha256(key.encode()).hexdigest()):
        raise HTTPException(404,'Solicitud no encontrada o expirada')
    return row

@app.get('/diagnostics/{job}')
async def status(job:str,request:Request):
    row=authorized(job,request)
    return {'status':row['status'],'stage':row['stage'],'saved':bool(row['saved']),
            'filename':row['name'] if row['status']=='ready' else None}

@app.get('/diagnostics/{job}/pdf')
async def download(job:str,request:Request):
    row=authorized(job,request)
    path=STATE/(row['id']+'.pdf')
    if row['status']!='ready' or not path.exists(): raise HTTPException(409,'PDF aún no disponible')
    return FileResponse(path,media_type='application/pdf',filename=row['name'])
