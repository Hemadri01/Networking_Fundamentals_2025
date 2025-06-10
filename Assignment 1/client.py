import socket


#inputs

client_name = "Client of " + input("\nEnter the client name: ")
client_integer = int(input("Enter the client integer: "))


#socket programming starts

client_socket = socket.socket() #Uses default which is AF_INET and SOCK_STREAM

client_socket.connect(("localhost",9999))


#Send data to server
client_socket.send(f"{client_name} \n {client_integer}".encode())


#Receive data from server
data = client_socket.recv(1024).decode()
server_name , server_integer_s = data.split("\n")
server_integer = int(server_integer_s)


if("OUT OF RANGE" in server_name):
	print("\n\nERROR MESSAGE FROM SERVER: " + server_name)
	client_socket.close()

else:

	client_socket.shutdown(socket.SHUT_RDWR)


	#Print data
	print(f"\n{client_name} is connected to {server_name}")
	print(f"Server integer = {server_integer}")
	print(f"Client integer = {client_integer}")

	integer_sum = server_integer + client_integer

	print(f"Sum = {integer_sum}")


	client_socket.close()

