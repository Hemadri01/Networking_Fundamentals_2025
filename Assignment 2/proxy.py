import socket



CACHE = {}  # Dictionary to store cached responses

def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode()

        if not request:
            client_socket.close()
            return
        
        # Extract the requested resource from the GET request
        lines = request.splitlines()
        request_line = lines[0].split()
        
        if len(request_line) < 2:
            client_socket.close()
            return
        
        # Extract the requested URL from the GET request
        requested_url = request_line[1]

        # Check if the requested URL is in cache
        if requested_url in CACHE:
            print(f"Serving from cache: {requested_url}")
            cached_response = CACHE[requested_url]
            client_socket.send(cached_response)
        else:
            print(f"Requesting from web server: {requested_url}")
            
            # Connect to the web server
            web_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            web_server_socket.connect(('localhost', 9999))  # Change this to the web server's address

            # Send the original request to the web server
            web_server_socket.send(request.encode())

            # Receive the response from the web server
            web_response = web_server_socket.recv(4096)
            
            # Cache the response
            CACHE[requested_url] = web_response

            # Send the web server response to the client
            client_socket.send(web_response)

            web_server_socket.close()
        
        client_socket.close()

    except Exception as e:
        print(f"Error handling client: {e}")
        client_socket.close()









def start_proxy_server(host='localhost', port=9998):
    # Create a socket to listen for incoming connections
    proxy_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_server_socket.bind((host, port))
    proxy_server_socket.listen(1)
    print(f"Proxy server started on {host}:{port}")

    while True:
        # Accept incoming client connections
        client_socket, client_address = proxy_server_socket.accept()
        print(f"Accepted connection from {client_address}")
        
        # Handle the client connection
        handle_client(client_socket)

        # Close the connection after handling one request
        print("Closing connection with client.")
        client_socket.close()


def main():
    start_proxy_server()

main()