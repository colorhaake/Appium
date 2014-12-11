import socket
import threading
import SocketServer
from AppiumServerLauncher import AppiumServerLauncher

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def setup(self):
        self.request.settimeout(3.0)
         
    def handle(self):
        
        data = ''
        try:
            while True:
                tmp = self.request.recv(1024)
                if not tmp: 
                    break
                data += tmp
        except socket.timeout:
            pass
            
        cur_thread = threading.current_thread()
        response = "{}: {}".format(cur_thread.name, data)
        print "{} wrote:".format(self.client_address[0])
        print data
    
        # launch server
        appium_server_launcher.execute_server(data)
        
        self.request.sendall("Launch Server Success !")
        self.request.close(  )
        
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

appium_server_launcher = ''
if __name__ == "__main__":
    appium_server_launcher = AppiumServerLauncher()
    
    
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "", 12345

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server " + ip + ":" + str(port) + " loop running in thread:", server_thread.name

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

#     client(ip, port, "Hello World 1")
#     client(ip, port, "Hello World 2")
#     client(ip, port, "Hello World 3")

    print "\nServer ShutDown"
    server.shutdown()