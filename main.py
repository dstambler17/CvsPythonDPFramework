import http.server
import socketserver
import os
import json
from Crypto.Cipher import AES
import re
import myModule
import timeit
from fib_comp import fib

# PythonDecorators/decorator_with_arguments.py
class route(object):
    def __init__(self, route, method):
        self.route = route
        self.method = method

    def __call__(self, f):
        def wrapped_f(*args):
            print("Decorator arguments:", self.route)
            path = args[0]
            print('PATH')
            print(path)
            if func_dict[f.__name__] in path:
                #find argument params
                var_finder = path.split(func_dict[f.__name__])[1]
                matches = var_finder.split('/')
                return f(*matches)
            else:
                return None, None
        return wrapped_f

'''Test route for the framework'''
@route("/item/<val>", method='GET')
def baseRoute(val):
    print('test, test')
    return json.dumps({'test': val}).encode('utf-8'), 200


@route("/encrypt/<message>", method='GET')
def encrypt_message(message):
    message = message.replace('%20', ' ')
    obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    try:
        encrypt_text = obj.encrypt(message)
    except ValueError as e:
        return str(e), 400
    return json.dumps({'encrypted message' : str(encrypt_text)}).encode('utf-8'), 200

@route("/decrypt/message", method='GET')
def decrypt_message(message):
    obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    try:
        print(message)
        text = obj.decrypt(message)
    except ValueError as e:
        return str(e), 400
    return json.dumps({'decrypted message' : str(text)}).encode('utf-8'), 200

@route("/c_extension/<val>", method='GET')
def call_c_extension(val):
    val = int(val)
    if val > 15: #taking too long so return error
        return 'Taking too long due to high value', 401
    res = myModule.fib(val)
    #python string
    my_string = 'myModule.fib(' + str(val) + ')'
    my_string_py = 'fib(' + str(val) + ')'
    print('call')
    #call timeit
    t_c_func = timeit.timeit(my_string, setup='import myModule', number=1000)
    python_time_comp = timeit.timeit(my_string_py, setup='from fib_comp import fib', number=1000)
    return json.dumps({'result' : str(res), 'c_time': str(t_c_func), 'py_time' : str(python_time_comp)}).encode('utf-8'), 200



func_dict = {'baseRoute': 'item/', 'encrypt_message': 'encrypt/', 'decrypt_message' : 'decrypt/', 'call_c_extension' : 'c_extension/'}
func_list = [baseRoute, encrypt_message, decrypt_message, call_c_extension]


class customHandler(http.server.BaseHTTPRequestHandler):
    #Handler for the GET requests
    def do_GET(self):
        if self.path == "/" or self.path == '' or self.path == 'index.html':
            self.path="index.html"
        elif self.path.strip() == '/favicon.ico':
            print(self.path)
        else: #for the routes
            '''
            cycle through the list of functions
            '''
            for x in func_list:
                #for this framework, variable params will be passed inbetween <>
                #res, code = x('the answer is no')
                res, code = x(self.path)
                if code is not None:
                    if code >= 400: #send errors
                        self.send_error(code,res + ': %s' % self.path)
                    self.send_response(code)
                    self.send_header('Content-type','application.json')
                    self.end_headers()
                    print(res)
                    self.wfile.write(res)
                    return
            self.send_error(404,'File Not Found: %s' % self.path)
            print(self.path)

        try:
            #Check the file extension required and set the right mime type
            file_types = {'.html' : 'text/html', '.jpg' : 'image/jpg', '.gif' : 'image/gif',
             '.js' : 'application/javascript', '.css' : 'text/css', '.json' : 'application.json'}

            mimetype = None
            for key in file_types.keys():
                if self.path.endswith(key):
                    mimetype = file_types[key]

            if mimetype is not None:
                f = open(os.curdir + os.sep + self.path, 'rb')
                print(os.curdir + os.sep + self.path)
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return


        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

def run_server():
    PORT_NUMBER = 8080
    
    try:
        server = http.server.HTTPServer(('', PORT_NUMBER), customHandler)
        print(f'Started httpserver on port {PORT_NUMBER}')        
        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()


def main():
    run_server()


if __name__ == "__main__":
    main()