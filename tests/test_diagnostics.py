import asyncio, importlib, json, sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'spark-gateway'))
import diagnostic_service as service
from diagnostic.models import Intake,Report
from diagnostic.pdf_report import filename,render
from diagnostic import archive

PAYLOAD=dict(company='Planta de prueba',industry='Manufactura',process='Dos operadores inspeccionan manualmente etiquetas en cajas al final de una línea.',goal='Detectar etiquetas incorrectas y medir la tasa de error.',pitch='Queremos detectar etiquetas incorrectas usando las cámaras de la línea y revisar los casos dudosos con un operador antes de rechazar una caja.',constraints='No detener la línea. No tenemos aún una tasa de error medida.',email='',consent=True)
REPORT=dict(summary='La inspección de etiquetas es candidata a una prueba de visión con supervisión humana.',improved_pitch='Evaluar un sistema de inspección visual de etiquetas que derive los casos dudosos a un operador y permita medir errores antes de automatizar rechazos.',corrections=['Separar detección visual y rechazo físico; no prometer una mejora antes de medir.'],missing_information=['Medir iluminación, velocidad de la línea y tasa de errores actual.'],architecture='Cámara y captura de imagen, análisis visual, registro de resultados y revisión humana. Comparar primero reglas de visión simples frente a modelos entrenados.',tools=[dict(id='deepstream',why='Puede organizar la captura y el análisis de video si se requiere un pipeline continuo.',validation='Probar la compatibilidad de cámaras y medir latencia en el hardware seleccionado.')],pilot_plan=['Recolectar ejemplos representativos con autorización y etiquetarlos.','Comparar una línea base sencilla y un modelo sobre datos separados de prueba.','Realizar una prueba supervisada sin activar el rechazo físico.'],metrics=['Falsos positivos y falsos negativos por turno.','Latencia por imagen y porcentaje de revisión humana.'],risks=['Los cambios de iluminación y etiquetas pueden reducir la precisión.'])

def test_validation_and_naming():
    p=Intake(**PAYLOAD);assert filename(p,'abcd1234').startswith('Planta_de_prueba_')
    p=Intake(**{**PAYLOAD,'email':'cliente@example.com'})
    assert filename(p,'abcd1234').startswith('cliente@example.com_')
    for change in ({'email':'bad'}, {'consent':False},{'pitch':'short'},{'website':'bot'},{'company':'   '}):
        with pytest.raises(ValueError): Intake(**{**PAYLOAD,**change})

def test_pdf(tmp_path):
    from pypdf import PdfReader
    p=Intake(**{**PAYLOAD,'company':'Compañía <script> & Muñoz'})
    out=tmp_path/'sample.pdf'
    render(out,p,Report(**REPORT),'Revisión de ejemplo: falta medir los errores antes de elegir hardware.','mock-model','a'*32)
    pages=PdfReader(out).pages;text='\n'.join(p.extract_text() for p in pages)
    assert len(pages)>=3
    assert 'Compañía <script> & Muñoz' in text
    assert 'NVIDIA DeepStream' in text and 'Pitch original' in text
    assert 'mock-model' in text

def test_api_boundaries_and_end_to_end(tmp_path,monkeypatch):
    monkeypatch.setattr(service,'STATE',tmp_path)
    async def ready(): return True
    async def fake_analyze(payload,progress):
        await progress('Analizando');return Report(**REPORT),'Auditoría de prueba.','mock'
    monkeypatch.setattr(service,'readiness',ready)
    monkeypatch.setattr(service,'analyze',fake_analyze)
    monkeypatch.setattr(archive,'upload',lambda *a:'drive-test-id')
    headers={'Origin':service.ORIGINS[0],'Idempotency-Key':'a'*64}
    with TestClient(service.app) as client:
        assert client.post('/diagnostics',json=PAYLOAD).status_code==403
        assert client.post('/diagnostics',content='x'*25000,headers=headers).status_code==413
        assert client.post('/diagnostics',json={**PAYLOAD,'consent':False},headers=headers).status_code==422
        response=client.post('/diagnostics',json=PAYLOAD,headers=headers)
        assert response.status_code==202;job=response.json()['id']
        assert client.post('/diagnostics',json=PAYLOAD,headers=headers).json()['id']==job
        assert client.get('/diagnostics/'+job).status_code==404
        auth={'Authorization':'Bearer '+'a'*64}
        assert client.get('/diagnostics/'+job+'/pdf',headers=auth).status_code==409
        import time
        for _ in range(60):
            result=client.get('/diagnostics/'+job,headers=auth).json()
            if result['status']=='ready':break
            time.sleep(.1)
        assert result['status']=='ready' and result['saved'] is True
        pdf=client.get('/diagnostics/'+job+'/pdf',headers=auth)
        assert pdf.content.startswith(b'%PDF') and pdf.headers['cache-control']=='no-store'
        with service.db() as conn:
            assert conn.execute('SELECT payload FROM jobs WHERE id=?',(job,)).fetchone()[0]==''
            conn.execute('UPDATE jobs SET created=0 WHERE id=?',(job,))
        service.cleanup()
        assert client.get('/diagnostics/'+job,headers=auth).status_code==404
        assert not (tmp_path/(job+'.pdf')).exists()

def test_rate_limit(tmp_path,monkeypatch):
    monkeypatch.setattr(service,'STATE',tmp_path);service.init()
    monkeypatch.setattr(service,'LIMIT',1)
    async def ready():return True
    monkeypatch.setattr(service,'readiness',ready)
    # No lifespan: keep jobs queued deterministically for admission tests.
    client=TestClient(service.app)
    headers={'Origin':service.ORIGINS[0],'Idempotency-Key':'b'*64}
    assert client.post('/diagnostics',json=PAYLOAD,headers=headers).status_code==202
    headers['Idempotency-Key']='c'*64
    assert client.post('/diagnostics',json=PAYLOAD,headers=headers).status_code==429

def test_archive_does_not_claim_success_on_mismatch(tmp_path,monkeypatch):
    p=tmp_path/'file.pdf';p.write_bytes(b'%PDF test')
    monkeypatch.setattr(archive,'command',lambda *args:json.dumps({'Size':1,'Hashes':{'md5':'wrong'}}))
    with pytest.raises(RuntimeError):archive.upload(p,'file.pdf')

def test_failed_drive_retains_download(tmp_path,monkeypatch):
    monkeypatch.setattr(service,'STATE',tmp_path);service.init()
    async def fake_analyze(*args):return Report(**REPORT),'Revisión','mock'
    monkeypatch.setattr(service,'analyze',fake_analyze)
    def fail(*args):raise RuntimeError('Drive offline')
    monkeypatch.setattr(archive,'upload',fail)
    with service.db() as conn:
        conn.execute("INSERT INTO jobs(id,secret,ip,created,status,stage,payload) VALUES(?,?,?,?,?,?,?)",('test','x','ip',__import__('time').time(),'queued','',Intake(**PAYLOAD).model_dump_json()))
    async def run():
        task=asyncio.create_task(service.worker())
        for _ in range(100):
            await asyncio.sleep(.1)
            with service.db() as conn:row=conn.execute("SELECT * FROM jobs WHERE id='test'").fetchone()
            if row['status']=='ready':break
        task.cancel()
        try:await task
        except asyncio.CancelledError:pass
        assert row['status']=='ready' and row['saved']==0
    asyncio.run(run())
