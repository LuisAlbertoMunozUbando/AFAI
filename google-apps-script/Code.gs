/**
 * Automation Foundry AI — Community signup receiver.
 * Google Apps Script: Extensions > Apps Script in the AFAI subscriber spreadsheet.
 * Deploy as Web App: Execute as Me; access Anyone.
 * IMPORTANT: Review privacy policy and security settings before publishing.
 */
const SHEET_NAME = 'Subscribers';
const MAX = {fullName:120,email:200,company:180,jobTitle:120,region:120,challenges:3000};
function clean(v, n) { return String(v == null ? '' : v).trim().slice(0,n).replace(/^[=+@-]/,"'"+String(v == null ? '' : v).trim().charAt(0)); }
function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    const payload = JSON.parse((e.parameter && e.parameter.payload) || '{}');
    if (payload.website) return ContentService.createTextOutput('ignored');
    if (payload.consent !== true || payload.privacy !== true) throw new Error('Consent required');
    const email = String(payload.email||'').trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length>200) throw new Error('Invalid email');
    if (!String(payload.fullName||'').trim() || !String(payload.company||'').trim() || !String(payload.challenges||'').trim()) throw new Error('Required fields missing');
    if (JSON.stringify(payload).length > 12000) throw new Error('Payload too large');
    const allowed = a => Array.isArray(a) ? a.slice(0,20).map(x=>clean(x,100)).join('; ') : '';
    const row = [
      new Date(), clean(payload.fullName,MAX.fullName), clean(email,MAX.email),
      clean(payload.company,MAX.company), clean(payload.jobTitle,MAX.jobTitle),
      clean(payload.region,MAX.region), allowed(payload.roles),
      clean(payload.maturity,100), clean(payload.challenges,MAX.challenges),
      allowed(payload.interests), allowed(payload.updates), 'Yes', 'Yes',
      payload.pilot===true?'Yes':'No', clean(payload.source,400),
      clean(payload.submissionId,100), 'Subscribed'
    ];
    lock.waitLock(15000);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    if (!sheet) throw new Error('Subscribers tab missing');
    const last = sheet.getLastRow();
    if (last>1) {
      const ids=sheet.getRange(2,16,last-1,1).getValues().flat();
      if (ids.includes(row[15])) return ContentService.createTextOutput('already received');
    }
    sheet.appendRow(row);
    return ContentService.createTextOutput('received');
  } catch (err) {
    console.error(err);
    return ContentService.createTextOutput('invalid');
  } finally {try{lock.releaseLock()}catch(_){}} 
}
/** To stop emailing someone: set their Status cell to Unsubscribed, or delete their row on request. */
