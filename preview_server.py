import http.server, os
os.chdir(os.path.expanduser("~"))
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/mc-boychild.html"
        super().do_GET()
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
http.server.ThreadingHTTPServer.allow_reuse_address = True
http.server.ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
