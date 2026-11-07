'use strict';
(()=>{
const BASE='https://afai-api.albertomunoz.ai';
const $=id=>document.getElementById(id), form=$('diagnostic-form');
let key='',job='',filename='',busy=false,ready=false,submitted='';
async function call(path,options={}){
  const response=await fetch(BASE+path,{...options,signal:AbortSignal.timeout(20000),cache:'no-store'});
  if(!response.ok){
    const data=await response.json().catch(()=>({}));
    throw Error(typeof data.detail==='string'?data.detail:'Unable to complete the request. Check your details or try again later.');
  }
  return response;
}
async function availability(){
  $('availability').textContent='Checking service availability…';
  try{ready=(await (await call('/diagnostics/health')).json()).ready===true;}catch{ready=false;}
  $('availability').textContent=ready?'Service available. Complete your information to generate the PDF.':'The service is temporarily offline. You can prepare your description here; it will not be submitted until service is available.';
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
        filename=data.filename||'assessment.pdf';$('download').hidden=false;$('expiry').hidden=false;
        $('save-status').textContent=data.saved?'Private copy saved and verified in Google Drive.':'The PDF was generated, but the Drive copy could not be confirmed. Download it to keep a copy.';
        busy=false;return;
      }
      if(data.status==='failed'){
        busy=false;$('generate').disabled=!ready;key='';job='';submitted='';return;
      }
    }catch(error){showError(error);return;}
    await new Promise(resolve=>setTimeout(resolve,3000));
  }
  $('stage').textContent='Analysis is still in progress. You can check its status again.';$('resume').hidden=false;
}
form.addEventListener('submit',async event=>{
  event.preventDefault();if(busy||!ready||!form.reportValidity())return;
  const payload=Object.fromEntries(new FormData(form));payload.consent=form.elements.consent.checked;
  payload.language=document.documentElement.lang||'en';
  const body=JSON.stringify(payload);
  // Preserve the key across transport retries for the same request.
  if(body!==submitted){key=token();submitted=body;}
  busy=true;$('generate').disabled=true;$('result').hidden=false;$('result').focus();
  $('stage').textContent='Submitting your request…';$('download').hidden=true;$('expiry').hidden=true;$('save-status').textContent='';
  try{
    const data=await (await call('/diagnostics',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':key},body})).json();
    job=data.id;await poll();
  }catch(error){showError(error);busy=false;$('generate').disabled=!ready;}
});
$('download').addEventListener('click',async()=>{
  $('download').disabled=true;
  try{
    const response=await call('/diagnostics/'+job+'/pdf',{headers:{Authorization:'Bearer '+key}});
    if(!response.headers.get('content-type')?.includes('application/pdf'))throw Error('Invalid PDF response.');
    const url=URL.createObjectURL(await response.blob());const a=document.createElement('a');
    a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
  }catch(error){showError(error);}finally{$('download').disabled=false;}
});
$('resume').addEventListener('click',poll);$('retry').addEventListener('click',availability);
availability();
})();
