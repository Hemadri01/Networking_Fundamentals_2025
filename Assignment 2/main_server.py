import socket
import time

def filereader(name):
    count = 0

    try:
        with open(name,encoding='UTF-8') as fhandle:
            data = fhandle.read()
            for line in data:
                count += 1
        print(count)
        return data

    except FileNotFoundError:
        print("File Not Found")
        return ""
    


    

def main_serversocket():

    
    server_name = "Server of Hemadri"

    server_socket = socket.socket() #Uses default which is AF_INET and SOCK_STREAM

    server_socket.bind(('localhost',9999))

    server_socket.listen(1)
    print(f"\n{server_name} waiting for connection.")

    while True:

        #Display quit message
        print("\nPress ctrl+break or ctrl+fn+s to end the program",end="")


        client_socket , client_address = server_socket.accept()


        #Confirm connection
        print("\r" + " "*80 + f"\nConnected with {client_address}")

        #Receive client data
        timeout = 3
        html_request_name = ""

        client_socket.settimeout(timeout)

        try:
            data = client_socket.recv(1024).decode()  # Try to receive data

            lines = data.splitlines()

            if data:
                print(data)  # If data is received, print it

                for line in lines:
                    if line.startswith('GET '):
                        html_request_name = line[5:line.find(' H')]
            
                print(html_request_name)

                if(html_request_name == "favicon.ico"):

                    client_socket.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n".encode())

                else:
                    
                    html_file = filereader(html_request_name)

                    client_socket.send(f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n{html_file}".encode())
                
               

        except socket.timeout:
            # This will trigger if no data is received within the timeout
            print(f"No data received from {client_address} within {timeout} seconds.")


            
            
        # Close the connection after the timeout or when data is received
        print(f"Closing connection with {client_address}")
        client_socket.close()

        


def main():
    main_serversocket()


main()