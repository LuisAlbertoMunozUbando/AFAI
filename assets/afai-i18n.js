/* AFAI multilingual foundation. Local-only translations; no user content leaves the browser. */
(()=>{'use strict';
const langs={en:'English',es:'Español',fr:'Français',it:'Italiano',de:'Deutsch',ja:'日本語',zh:'中文（简体）',ar:'العربية'};
const words={
'Home':['Inicio','Accueil','Home','Startseite','ホーム','首页','الرئيسية'],
'About':['Acerca de','À propos','Informazioni','Über uns','概要','关于','حول'],
'Services':['Servicios','Services','Servizi','Dienste','サービス','服务','الخدمات'],
'How it works':['Cómo funciona','Fonctionnement','Come funziona','So funktioniert es','仕組み','工作原理','كيف يعمل'],
'Contact':['Contacto','Contact','Contatti','Kontakt','お問い合わせ','联系','اتصل بنا'],
'Products':['Productos','Produits','Prodotti','Produkte','製品','产品','المنتجات'],
'Community':['Comunidad','Communauté','Comunità','Community','コミュニティ','社区','المجتمع'],
'Experiment':['Experimento','Expérience','Esperimento','Experiment','実験','实验','تجربة'],
'Business Model':['Modelo de negocio','Modèle économique','Modello di business','Geschäftsmodell','ビジネスモデル','商业模式','نموذج العمل'],
'Ask Anything':['Pregunta lo que quieras','Posez votre question','Chiedi qualsiasi cosa','Frag alles','何でも質問','随便提问','اسأل أي شيء'],
'Ask anything':['Pregunta lo que quieras','Posez votre question','Chiedi qualsiasi cosa','Frag alles','何でも質問','随便提问','اسأل أي شيء'],
'Get started':['Comenzar','Commencer','Inizia','Loslegen','始める','开始使用','ابدأ'],
'Learn more':['Más información','En savoir plus','Scopri di più','Mehr erfahren','詳しく見る','了解更多','اعرف المزيد'],
'Submit':['Enviar','Envoyer','Invia','Senden','送信','提交','إرسال'],
'Search':['Buscar','Rechercher','Cerca','Suchen','検索','搜索','بحث'],
'Language':['Idioma','Langue','Lingua','Sprache','言語','语言','اللغة'],
'Student':['Estudiante','Étudiant','Studente','Studierende','学生','学生','طالب'],
'All rights reserved.':['Todos los derechos reservados.','Tous droits réservés.','Tutti i diritti riservati.','Alle Rechte vorbehalten.','無断転載禁止。','保留所有权利。','جميع الحقوق محفوظة.']
};
const order=['es','fr','it','de','ja','zh','ar'];
const lookup=new Map();
for(const [english,values] of Object.entries(words)){lookup.set(english,{en:english,...Object.fromEntries(order.map((x,i)=>[x,values[i]]))});for(const v of values)lookup.set(v,{en:english,...Object.fromEntries(order.map((x,i)=>[x,values[i]]))});}
const key='afai-language';const valid=x=>Object.hasOwn(langs,x);
let lang=new URLSearchParams(location.search).get('lang')||localStorage.getItem(key)||'en';if(!valid(lang))lang='en';
function translateNode(node){if(node.nodeType!==3||!node.parentElement||node.parentElement.closest('script,style,textarea,pre,code,[data-no-translate],.afai-language-control'))return;const text=node.nodeValue;const trimmed=text.trim();const entry=lookup.get(trimmed);if(entry)node.nodeValue=text.replace(trimmed,entry[lang]||entry.en);}
function apply(){document.documentElement.lang=lang;document.documentElement.dir=lang==='ar'?'rtl':'ltr';document.querySelectorAll('body *').forEach(el=>{if(el.closest('[data-no-translate],.afai-language-control'))return;for(const n of el.childNodes)translateNode(n);});document.querySelectorAll('.afai-language-control select').forEach(s=>s.value=lang);}
function init(){const css=document.createElement('style');css.textContent='.afai-language-control{position:fixed;top:86px;right:16px;z-index:9999;background:#101a20;color:#f2f6f6;border:1px solid #a3e635;border-radius:9px;padding:7px 10px;box-shadow:0 6px 24px #0007;font:600 13px system-ui}.afai-language-control select{background:#101a20;color:#f2f6f6;border:0;max-width:155px;cursor:pointer}.afai-language-control label{margin-inline-end:5px}.afai-i18n-notice{font:11px system-ui;opacity:.8;margin-top:3px;max-width:185px}@media(max-width:600px){.afai-language-control{top:auto;bottom:12px;right:12px}}';document.head.append(css);
const box=document.createElement('div');box.className='afai-language-control';box.setAttribute('data-no-translate','');const label=document.createElement('label');label.textContent='🌐';label.setAttribute('for','afai-lang-select');const select=document.createElement('select');select.id='afai-lang-select';select.setAttribute('aria-label','Website language');for(const [code,name] of Object.entries(langs)){const o=document.createElement('option');o.value=code;o.textContent=name;select.append(o);}select.value=lang;select.addEventListener('change',()=>{lang=select.value;localStorage.setItem(key,lang);apply();});box.append(label,select);document.body.append(box);apply();
const observer=new MutationObserver(records=>{for(const r of records){for(const n of r.addedNodes){if(n.nodeType===3)translateNode(n);else if(n.nodeType===1&&!n.closest('.afai-language-control')){for(const t of n.querySelectorAll('*'))for(const c of t.childNodes)translateNode(c);}}}});observer.observe(document.body,{subtree:true,childList:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();