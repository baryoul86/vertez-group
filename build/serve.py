import http.server, os, sys
ROOT=sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def translate_path(s,p):
        p=p.split('?')[0].split('#')[0]
        fp=os.path.join(ROOT,p.lstrip('/'))
        if os.path.isdir(fp): fp=os.path.join(fp,'index.html')
        elif not os.path.exists(fp) and os.path.exists(fp+'.html'): fp+='.html'
        return fp
    def log_message(s,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',8765),H).serve_forever()
