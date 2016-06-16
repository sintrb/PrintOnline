# -*- coding: UTF-8 -*
'''
@author: sintrb
'''
"""

PrintOnline Server.

This module refer to SimpleHTTPServer

"""


__version__ = "0.0.1"

import BaseHTTPServer
import SocketServer
import json
import os
import shutil
import socket
import sys
import urlparse

import re
import inspect
import tempfile
import win32api, win32print

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

reload(sys)
# sys.setdefaultencoding("utf-8")

libdir = os.path.dirname(__file__)
if not libdir:
    libdir = os.getcwd()

options = {
        'tempdir':os.path.join(tempfile.gettempdir(), 'printonlie'),
        'bind':'0.0.0.0',
        'port':8000
        }

class ApiException(Exception):
    def __init__(self, res):
        self.res = res

def ex(e, c=-1):
    return ApiException({"code":c, "msg":e})

def get_printers():
    return [{'name':d[2]} for d in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]

def get_files():
    d = options['tempdir']
    if os.path.exists(d) and os.path.isdir(d):
        arr = []
        for f in os.listdir(options['tempdir']):
            if os.path.isfile(os.path.join(options['tempdir'], f)):
                arr.append({
                        'name':u'%s' % f.decode('windows-1252'),
                    })
        return arr 
    else:
        return []

def del_file(f):
    d = options['tempdir']
    if os.path.exists(d) and os.path.isdir(d) and os.path.exists(os.path.join(d, f)):
        os.remove(os.path.join(d, f))

def set_file(name, fp):
    d = options['tempdir']
    if not os.path.exists(d):
        os.makedirs(d)
    fn = os.path.join(d, name)
    with open(fn, 'wb') as f:
        f.write(fp.read())

def print_file(filename, printername):
    printername = win32print.GetDefaultPrinter()
#     filepath = os.path.join(options['tempdir'], filename).decode('utf-8')
    device = '/d:"%s"' % printername
#     print filepath, device
#     filepath = r'C:\Users\Administrator\Desktop\LeetCode\全页照片.pdf'
#     device = r'/d:"doPDF v7"'
    os.chdir(options['tempdir'])
    try:
        win32api.ShellExecute(0, "print", filename, device, options['tempdir'], 0)
    except Exception,e:
        print e
        

class PrintOnlineRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "PrintOnline/" + __version__
    protocol_version = "HTTP/1.1"
    editortmpl = ''
    def check_auth(self):
        if not options.get('auth'):
            return True
        au = self.headers.getheader('authorization')
        if au and len(au) > 6 and au.endswith(options.get('auth')):
            return True
        f = StringIO()
        f.write('<center><h2>401 Unauthorized</h2></center>')
        
        self.send_response(401, "Unauthorized")
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(f.tell()))
        self.send_header("WWW-Authenticate", 'Basic realm="%s"' % (options.get('realm') or self.server_version))
        self.send_header('Connection', 'close')
        self.end_headers()
        f.seek(0)
        shutil.copyfileobj(f, self.wfile)
        return False
    
    def api_printers(self):
        return get_printers()

    def api_files(self):
        return get_files()
    
    def api_update(self):
        return {
                'files':self.api_files(),
                'printers':self.api_printers()
                }
    def api_print(self, filename, printername):
        print_file(filename, printername)
        return {}
    def do_POST(self):
        if not self.check_auth():
            return
        f = StringIO()
        contenttype = 'text/html'
        statuscode = 200
        
#         length = int(self.headers.getheader('content-length'))
#         body = self.rfile.read(length)
#         print len(body)
#         print body
        import cgi 
        
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
              'CONTENT_TYPE':self.headers['Content-Type'],
            })
        uploadfile = form['file']
        filename = uploadfile.filename
        set_file(filename, uploadfile.file)
        res = {
               'name':filename
               }
        
        f.write(json.dumps(res))
        
        self.send_response(statuscode)
        self.send_header("Content-type", contenttype)
        self.send_header("Content-Length", str(f.tell()))
        self.send_header('Connection', 'close')
                
        self.end_headers()
        f.seek(0)
        shutil.copyfileobj(f, self.wfile)
    
    def do_GET(self):
        if not self.check_auth():
            return
        self.path = self.path.replace('..', '')
        url = urlparse.urlparse(self.path)
        contenttype = 'text/html'
        statuscode = 200
        f = StringIO()
#         print url
        if url.path.startswith('/api/'):
            try:
                from urllib import unquote
                contenttype = 'text/json'
                apiname = 'api_%s' % (url.path.replace('/api/', ''))
                if not hasattr(self, apiname):
                    raise ex('not such api: %s' % apiname)
                
                param = dict([(r[0], unquote(r[1]).replace('+', ' ')) for r in re.findall('([^&^=]+)=([^&^=]*)', url.query)])
                apifunc = getattr(self, apiname)
                
                argspec = inspect.getargspec(apifunc)
                kvargs = {}
                funcagrs = argspec.args
                defaults = argspec.defaults
                if defaults:
                    for i, v in enumerate(funcagrs[-len(defaults):]):
                        kvargs[v] = defaults[i]

                if len(funcagrs):
                    param['_param'] = param
                    argslen = len(funcagrs) - (len(defaults) if defaults else 0) - 1
                    missargs = []
                    for i, k in enumerate(funcagrs[1:]):
                        if k in param:
                            kvargs[k] = param[k]
                        elif i < argslen:
                            missargs.append(k)
                    if missargs:
                        raise ex('need argments: %s' % (', '.join(missargs)))
                data = apifunc(**kvargs)
                res = {'data':data, 'code':0}
            except ApiException, e:
                res = e.res
            f.write(json.dumps(res))
        else:
            filepath = os.path.join(libdir, url.path.strip('/') or 'index.html')
            if os.path.exists(filepath) and os.path.isfile(filepath):
                f.write(open(filepath, 'rb').read())
            else:
                statuscode = 404
                f.write("404 not found")

        self.send_response(statuscode)
        self.send_header("Content-type", contenttype)
        self.send_header("Content-Length", str(f.tell()))
        self.send_header('Connection', 'close')
        self.end_headers()
        f.seek(0)
        shutil.copyfileobj(f, self.wfile)


class ThreadingHTTPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = 1  # Seems to make sense in testing environment
    def server_bind(self):
        """Override server_bind to store the server name."""
        SocketServer.TCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

def start():
    port = options['port'] if 'port' in options else 8000
    server_address = (options['bind'], port)
    httpd = ThreadingHTTPServer(server_address, PrintOnlineRequestHandler)
    sa = httpd.socket.getsockname()
    print "Temp Directory: %s" % options.get('tempdir')
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()

def config(argv):
    import getopt
    opts, args = getopt.getopt(argv, "u:p:r:ht:")
    for opt, arg in opts:
        if opt == '-u':
            options['username'] = arg
        elif opt == '-p':
            options['password'] = arg
        elif opt == '-r':
            options['realm'] = arg
        elif opt == '-t':
            options['tempdir'] = arg
        elif opt == '-h':
            print 'Usage: python -m PrintOnline [-u username] [-p password] [-r realm] [-t tempdir] [bindaddress:port | port]'
            print 'Report bugs to <sintrb@gmail.com>'
            exit()

    if options.get('username') and options.get('password'):
        import base64
        options['auth'] = base64.b64encode('%s:%s' % (options.get('username'), options.get('password')))
    if len(args) > 0:
        bp = args[0]
        if ':' in bp:
            options['bind'] = bp[0:bp.index(':')]
            options['port'] = int(bp[bp.index(':') + 1:])
        else:
            options['bind'] = '0.0.0.0'
            options['port'] = int(bp)
    
    
def main():
    config(sys.argv[1:])
    start()

def test():
    config(sys.argv[1:])
    print get_files()

if __name__ == '__main__':
#     test()
    main()
