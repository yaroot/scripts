#!/usr/bin/env python2

import BaseHTTPServer
import re
import StringIO


UPLOAD_HTML = """
<form enctype="multipart/form-data" method="post" action="/">
<input name="file" type="file"/>
<input type="submit" value="upload"/>
</form>
"""


class SimpleHttpUploadHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def save_file(self):
        boundary = self.headers.plisttext.split('=')[1]
        assert len(boundary) > 5

        bytestoread = int(self.headers['Content-Length'])

        line = self.rfile.readline()
        assert boundary in line
        bytestoread -= len(line)

        line = self.rfile.readline()
        fname_match = re.match(r'.*filename="(.*)"', line)
        assert fname_match is not None
        fname, = fname_match.groups()
        bytestoread -= len(line)

        line = self.rfile.readline()
        bytestoread -= len(line)
        line = self.rfile.readline()
        bytestoread -= len(line)

        tmp = StringIO.StringIO()
        while bytestoread > 0:
            line = self.rfile.readline()
            bytestoread -= len(line)
            if boundary not in line:
                tmp.write(line)
        with open(fname, 'wb') as f:
            f.write(tmp.getvalue()[:-2])

    def do_POST(self):
        self.save_file()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write("SUCCESS")

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(UPLOAD_HTML)
        else:
            self.send_response(200)
            self.end_headers()

def test(HandlerClass=SimpleHttpUploadHandler, ServerClass=BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    test()
