from ConfigParser import SafeConfigParser
import os
import os.path
import threading
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import subprocess
import sys

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Wall</title>
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.6.4.min.js"></script>
</head>
<body>
    <h1>Wall</h1>
    <div id="wall"></div>
    <script type="text/javascript">
        $(document).ready(function(){
            if ("WebSocket" in window) {
              var ws = new WebSocket("ws://localhost:8080/websocket/");
              ws.onmessage = function (evt) {
                  var html = evt.data + "<br>"
                  $("#wall").append(html);
              };
              ws.onclose = function() {
                  $("#wall").append("<p>That's all, folks!</p>");
              };
            } else {
                  $("#wall").html("<p>Sorry, your browser is not supported.</p>");
            }
        });
    </script>
</body>
</html>
"""


LISTENERS = []

def read_config():
    if os.path.isfile('wos.ini'):
        parser = SafeConfigParser()
        parser.read('wos.ini')
        return parser
    else:
        sys.exit('wos.ini not found')

def monitor():
    interface = config.get('dsniff', 'interface')
    p = subprocess.Popen(['sudo', 'dsniff', '-n', '-i', interface],
                         stdout=subprocess.PIPE)
    while p.poll() is None:
        line = p.stdout.readline()
        if line:
            for c in LISTENERS:
                c.write_message(unicode(line))


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(TEMPLATE)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        LISTENERS.append(self)

    def on_message(self, message):
        pass

    def on_close(self):
        LISTENERS.remove(self)

application = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/websocket/', WebSocketHandler),
])


if __name__ == "__main__":
    config = read_config()
    port = config.get('tornado', 'port')
    threading.Thread(target=monitor).start()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
