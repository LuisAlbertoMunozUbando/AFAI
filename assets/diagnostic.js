'use strict';
(()=>{
const BASE='https://afai-api.albertomunoz.ai';
const $=id=>document.getElementById(id), form=$('diagnostic-form');
let key='',job='',filename='',busy=false,ready=false,submitted='';
async function call(path,options={}){
  const response=await fetch(BASE+path,{...options,signal:AbortSignal.timeout(20000),cache:'no-store'});
  if(!response.ok){
    const data=await response.json().catch(()=>({}));
    throw Error(typeof data.detail==='string'?data.detail:'No se pudo completar la solicitud. Revisa los datos o intenta más tarde.');
  }
  return response;
}
async function availability(){
  $('availability').textContent='Comprobando disponibilidad del servicio…';
  try{ready=(await (await call('/diagnostics/health')).json()).ready===true;}catch{ready=false;}
  $('availability').textContent=ready?'Servicio disponible. Completa tu información para generar el PDF.':'El servicio está temporalmente fuera de línea. Puedes preparar tu descripción aquí; no se enviará hasta que esté disponible.';
  $('generate').disabled=!ready||busy;
}
function token(){return Array.from(crypto.getRandomValues(new Uint8Array(32)),b=>b.toString(16).padStart(2,'0')).join('');}
function showError(error){$('stage').textContent=error.message;$('resume').hidden=!job;}
async function poll(){
  $('resume').hidden=true;
  for(let i=0;i<180;i++){
    try{
      const data=await (await call('/diagnostics/'+job,{headers:{Authorization:'Bearer '+key}})).json();
      $('stage').textContent=data.stage;
      if(data.status==='ready'){
        filename=data.filename||'diagnostico.pdf';$('download').hidden=false;$('expiry').hidden=false;
        $('save-status').textContent=data.saved?'Copia privada guardada y verificada en Google Drive.':'El PDF se generó, pero no se confirmó la copia en Drive. Descárgalo para conservarlo.';
        busy=false;return;
      }
      if(data.status==='failed'){
        busy=false;$('generate').disabled=!ready;key='';job='';submitted='';return;
      }
    }catch(error){showError(error);return;}
    await new Promise(resolve=>setTimeout(resolve,3000));
  }
  $('stage').textContent='El análisis sigue en curso. Puedes consultar su estado nuevamente.';$('resume').hidden=false;
}
form.addEventListener('submit',async event=>{
  event.preventDefault();if(busy||!ready||!form.reportValidity())return;
  const payload=Object.fromEntries(new FormData(form));payload.consent=form.elements.consent.checked;
  const body=JSON.stringify(payload);
  // Preserve the key across transport retries for the same request.
  if(body!==submitted){key=token();submitted=body;}
  busy=true;$('generate').disabled=true;$('result').hidden=false;$('result').focus();
  $('stage').textContent='Enviando tu solicitud…';$('download').hidden=true;$('expiry').hidden=true;$('save-status').textContent='';
  try{
    const data=await (await call('/diagnostics',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':key},body})).json();
    job=data.id;await poll();
  }catch(error){showError(error);busy=false;$('generate').disabled=!ready;}
});
$('download').addEventListener('click',async()=>{
  $('download').disabled=true;
  try{
    const response=await call('/diagnostics/'+job+'/pdf',{headers:{Authorization:'Bearer '+key}});
    if(!response.headers.get('content-type')?.includes('application/pdf'))throw Error('Respuesta PDF no válida.');
    const url=URL.createObjectURL(await response.blob());const a=document.createElement('a');
    a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
  }catch(error){showError(error);}finally{$('download').disabled=false;}
});
$('resume').addEventListener('click',poll);$('retry').addEventListener('click',availability);
availability();
})();
