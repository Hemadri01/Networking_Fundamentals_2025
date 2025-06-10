from socket import * 
import os 
import sys 
import struct 
import time 
import select 
import binascii   
import signal
ICMP_ECHO_REQUEST = 8 
avg_rtt = 0


# Define signal handler to gracefully exit
def graceful_exit(signal, frame):
    print("\nStopping code")
    print(f"Average round trip time (rtt) = {avg_rtt:.2f}ms")
    sys.exit(0)

# Register signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, graceful_exit)



def checksum(data):  
    sum = 0
    length = len(data)
    if length % 2:
        data += b'\x00'

    # Process every 16-bit chunk
    for i in range(0, length, 2):
        word = (data[i] << 8) + (data[i+1])
        sum += word
        
    # Fold 32-bit sum to 16 bits and return the complement
    sum = (sum >> 16) + (sum & 0xFFFF)
    sum += (sum >> 16)
    return ~sum & 0xFFFF
  

def receiveOnePing(mySocket, ID, timeout, destAddr): 
    timeLeft = timeout 
    global avg_rtt


    while True:  
        startedSelect = time.time() 
        whatReady = select.select([mySocket], [], [], timeLeft) 
        howLongInSelect = (time.time() - startedSelect) 
        if whatReady[0] == []:  # Timeout when no data is recieved
            return "Request timed out." 
        
        timeReceived = time.time()  
        recPacket, addr = mySocket.recvfrom(1024)

        # The IP header is 20 bytes, ICMP header + data comes after that
        icmp_header = recPacket[20:28]
        type, code, recv_checksum, packetID, sequence = struct.unpack("!bbHHh", icmp_header)

        icmp_header_data = struct.pack("!bbHHh", type, code, 0, packetID, sequence)
        icmp_data = recPacket[28:]

        # Recalculate checksum to verify integrity
        #icmp_data = recPacket[20:]  # Full ICMP packet (header + data)
        calc_checksum = checksum(icmp_header_data+icmp_data)
        #calc_checksum = htons(calc_checksum)
        if calc_checksum != recv_checksum:
            return "Checksum error in received packet."
        else:
            # Verify ID and ICMP type (0 = Echo Reply)
            if packetID == ID and type == 0 and code == 0:
                timeSent = struct.unpack("d", icmp_data)[0]
                rtt = (timeReceived - timeSent) * 1000
                if(avg_rtt == 0):
                    avg_rtt = rtt
                else:
                    avg_rtt = (avg_rtt + rtt)/2
                return f"Reply from {destAddr}: bytes={len(recPacket)} time={round(rtt, 2)}ms"

        timeLeft -= howLongInSelect
        if timeLeft <= 0: # Timeout when garbled data is recieved before timeout
            return "Request timed out."

  
def sendOnePing(mySocket, destAddr, ID): 
    # Header is type (8), code (8), checksum (16), id (16), sequence (16) 
    
    myChecksum = 0 
    # Make a dummy header with a 0 checksum 
    # struct -- Interpret strings as packed binary data 
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) 
    data = struct.pack("d", time.time()) 
    # Calculate the checksum on the data and the dummy header. 
    myChecksum = checksum((header + data)) 
    # Get the right checksum, and put in the header 
    ##if sys.platform == 'darwin': 
        # Convert 16-bit integers from host to network  byte order 
        #myChecksum = htons(myChecksum) & 0xffff   
    #else: 
    #myChecksum = htons(myChecksum) 

    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) 
    packet = header + data 

    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str 
    # Both LISTS and TUPLES consist of a number of objects 
    # which can be referenced by their position number within the object. 

def doOnePing(destAddr, timeout):  
    icmp = getprotobyname("icmp") 
    # SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw 
    
    mySocket = socket(AF_INET, SOCK_RAW, icmp) 
    
    myID = os.getpid() & 0xFFFF  # Return the current process i 
    #print(myID)
    sendOnePing(mySocket, destAddr, myID) 
    delay = receiveOnePing(mySocket, myID, timeout, destAddr) 
    mySocket.close() 
    return delay 

def ping(host, timeout=1): 
    # timeout=1 means: If one second goes by without a reply from the server, 
    # the client assumes that either the client's ping or the server's pong is lost 
    dest = gethostbyname(host) 
    print("Pinging " + dest + " using Python:") 
    print("") 
    # Send ping requests to a server separated by approximately one second 
    while 1 : 
        delay = doOnePing(dest, timeout) 
        print(delay) 
        time.sleep(1)# one second 
    return delay

# To run traceroute for 4 continents it was better to run on specific IP Addresses than hostnames.

#if __name__ == "__main__":
    #host = input("Enter the host to ping (e.g., google.com): ")
    #get_route(host)

if __name__ == "__main__":
    host = input("Enter the IP Address to ping: ")
    ping(gethostbyaddr(host)[0])