import socket
import threading
import json
PORT = 8888
ADDRESS = "0.0.0.0"
ADDR = (ADDRESS, PORT)

data = []
clients = []

def return_json(response: str):
    headers, body = response.split("\r\n\r\n", 1)
    return json.loads(body.strip())

def get_query(response: str):
    request, rest = response.split("\r\n", 1)
    print(request.split(' ', 2)[1])
    return request.split(' ', 2)[1]

def parse(response: str):
    
    if response.startswith("GET"):
        return 'get'
    elif response.startswith("POST"):
        return 'post'


def handle_responses(connection, address, sock):
    with open("client/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    while True:
      try:
        req = connection.recv(4096)
        if not req:
            connection.close()
            continue
        get_query(req.decode())
        if parse(req.decode()) == 'get' and get_query(req.decode()) == '/':
            bod = html.encode('utf-8')
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(bod)}\r\n"
                "Connection: close\r\n"
                "\r\n"
                                
            )
                    
            connection.sendall(headers.encode("utf-8")+bod)
        elif parse(req.decode()) == 'get' and get_query(req.decode()) == '/msgref':
            
            bod = json.dumps(data)
            bod = bod.encode()
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(bod)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
            connection.sendall(headers.encode("utf-8")+bod)
        elif parse(req.decode()) == 'post':
            data.append(return_json(req.decode()))
            print(data)
            bod_json = json.dumps(data)
            bod_bytes = bod_json.encode()
            headers = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json; charset=utf-8\r\n"
                    f"Content-Length: {len(bod_bytes)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )
                                
            connection.sendall(headers.encode("utf-8")+bod_bytes)
      except Exception:
        pass
      finally:
        connection.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(ADDR)
    sock.listen()
    while True:
        connection, address = sock.accept()
        
        thread = threading.Thread(
                        target=handle_responses, 
                        args=(connection, address, sock),
                        daemon=True
                    )
        thread.start()
        
if __name__ == "__main__":
    main()