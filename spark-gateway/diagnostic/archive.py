"""Reuse Spark's existing rclone authentication without exposing OAuth tokens."""
import hashlib,json,os,re,subprocess
FOLDER=os.getenv('AFAI_DIAGNOSTIC_DRIVE_FOLDER','1DqdrricH-3vNmZBs_wURJ12aa0RifLBi')
REMOTE=os.getenv('AFAI_DIAGNOSTIC_RCLONE_REMOTE','knowledge-drive')

def command(*args):
    if not re.fullmatch(r'[A-Za-z0-9_-]+',REMOTE) or not re.fullmatch(r'[A-Za-z0-9_-]+',FOLDER):
        raise RuntimeError('Invalid archive configuration')
    result=subprocess.run(['rclone',*args,'--drive-root-folder-id',FOLDER,
        '--drive-shared-with-me=false','--contimeout','10s','--timeout','45s','--retries','2'],
        capture_output=True,text=True,timeout=100,check=True)
    return result.stdout

def check():
    command('lsjson',REMOTE+':','--max-depth','1','--dirs-only')

def upload(path,name):
    # Names never contain slashes. The private, dedicated folder is not shared by this service.
    if '/' in name or '\\' in name: raise ValueError('Invalid filename')
    command('copyto',str(path),REMOTE+':'+name)
    info=json.loads(command('lsjson',REMOTE+':'+name,'--stat','--hash'))
    expected=hashlib.md5(path.read_bytes()).hexdigest()
    if info.get('Size')!=path.stat().st_size or info.get('Hashes',{}).get('md5')!=expected:
        raise RuntimeError('Drive upload verification failed')
    return info.get('ID','')
