"""Read-only HTTP checks of the local production output at the root URL."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.request import urlopen
import threading,json
out=Path(__file__).resolve().parents[1]/'.build/pages'
class Quiet(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(out),**kwargs)
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
threading.Thread(target=server.serve_forever,daemon=True).start()
results={}
try:
    for path in ['/','/merge-alchemy.html']+['/'+p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()]:
        with urlopen(f'http://127.0.0.1:{server.server_port}{path}',timeout=10) as response:
            assert response.status==200
            results[path]=response.status
finally:server.shutdown();server.server_close()
print(json.dumps(results,indent=2))
