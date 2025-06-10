import socket


server_integer = 50
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
	data = client_socket.recv(1024).decode()
	client_name , client_integer_s = data.split("\n")
	client_integer = int(client_integer_s)



	#Check if client integer is in range
	if(client_integer in range(1,101)):


		#Send data to client
		client_socket.send(f"{server_name} \n {server_integer}".encode())

		client_socket.shutdown(socket.SHUT_RDWR)

		#Print client_integer, server_integer and their sum
		print(f"{server_name} is connected to {client_name}")
		print(f"Client integer recieved is {client_integer}")
		print(f"Server integer is {server_integer}")
		integer_sum = server_integer + client_integer
		print(f"Sum = {integer_sum}")


		
		


		print("Closing connection with ", client_address)
		client_socket.close()




	#Close connection if client integer OUT OF RANGE	
	else:

		client_socket.send(f"Integer OUT OF RANGE \n 0".encode())
		print(f"Closing connection with {client_address} because recieved client integer OUT OF RANGE")
		client_socket.close()
		

