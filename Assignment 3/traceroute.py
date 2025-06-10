from socket import * 
import os 
import sys 
import struct 
import time 
import select 
import binascii 
import signal  
ICMP_ECHO_REQUEST = 8 
MAX_HOPS = 30 
TIMEOUT  = 5.0  
TRIES    = 3 
# The packet that we shall send to each router along the path is the ICMP echo 
# request packet, which is exactly what we had used in the ICMP ping exercise. 
# We shall use the same packet that we built in the Ping exercise 


# Define signal handler to gracefully exit
def graceful_exit(signal, frame):
    print("\nStopping code")
    sys.exit(0)

# Register signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, graceful_exit)


def checksum(data):  
# In this function we make the checksum of our packet 
# hint: see icmpPing lab 
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


def build_packet(): 
# In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our 
# packet to be sent was made, secondly the checksum was appended to the header and 
# then finally the complete packet was sent to the destination. 
# Make the header in a similar way to the ping exercise. 
# Append checksum to the header. 
# Don’t send the packet yet , just return the final packet in this function. 
# So the function ending should look like this 
    myID = os.getpid() & 0xFFFF
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, 0, myID, 0) 
    data = struct.pack("d", time.time()) 
    myChecksum = checksum(header + data) 
    #myChecksum = htons(myChecksum) 
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 0)
    packet = header + data 
    return packet

# Main traceroute logic
def get_route(hostname): 
    timeLeft = TIMEOUT 
    try:
        destAddr = gethostbyname(hostname)
    except gaierror:
        print(f"Cannot resolve {hostname}")
        return
    
    print(f"Traceroute to {hostname} [{destAddr}], {MAX_HOPS} hops max: \n\n")

    for ttl in range(1,MAX_HOPS+1): 
        for tries in range(TRIES): 
            
            #print(ttl)
            #print(tries)
            try:
                # Create raw socket
                icmp_proto = getprotobyname("icmp")
                mySocket = socket(AF_INET, SOCK_RAW, icmp_proto)
            except PermissionError:
                print("You need to run this script with administrator/root privileges.")
                sys.exit(1)
        
            #Fill in start 
            # Make a raw socket named mySocket 
            #Fill in end  
            
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl)) 
            mySocket.settimeout(TIMEOUT) 

            try: 
                packet = build_packet() 
                mySocket.sendto(packet, (destAddr, 0)) 
                send_time = time.time()
                 
                startedSelect = time.time() 
                howLongInSelect = (time.time() - startedSelect)
                whatReady = select.select([mySocket], [], [], timeLeft) 
                if whatReady[0] == []: # Timeout 
                    print(f"TTL={ttl}    Trie={tries}   *        *        *    Request timed out. \n\n")
                    continue

                recvPacket, addr = mySocket.recvfrom(1024) 
                #print(recvPacket)
                recv_time = time.time() 
                timeLeft = timeLeft - howLongInSelect 
                if timeLeft <= 0: 
                    print("  *        *        *    Request timed out.") 

            except timeout: 
                continue    
                
            else: 
                #Fill in start         
                #Fetch the icmp type from the IP packet  
                #Fill in end 

                #print("hello")
                icmp_header = recvPacket[20:28]
                icmp_type, code,recv_checksum, packet_id, sequence = struct.unpack("!bbHHh", icmp_header)

                icmp_payload = recvPacket[28:]
                header_no_checksum = struct.pack("!bbHHh", icmp_type, code, 0, packet_id, sequence)
                calc_checksum = checksum(header_no_checksum + icmp_payload)
                #calc_checksum = htons(calc_checksum)

                if recv_checksum != calc_checksum:
                    print(f"TTL={ttl}    Trie={tries}   Checksum error. Skipping. \n\n")
                    continue

                #print(f"TTL={ttl}, ICMP Type={icmp_type}, From={addr[0]}")

                

                if icmp_type == 11: 
                    bytes = struct.calcsize("d")  
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0] 
                    print(f"TTL= {ttl}    trie={tries}    ICMP Type={icmp_type}    rtt={((recv_time - send_time)*1000):.2f} ms    {addr[0]}    " , end='', flush=True)
                    try:
                        hostnamesent = gethostbyaddr(addr[0])[0]
                    except (herror, gaierror):
                        hostnamesent = "Unknown"
                    print(hostnamesent+"\n\n")
                
                elif icmp_type == 3: 
                    bytes = struct.calcsize("d")  
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0] 
                    print(f"TTL= {ttl}    trie={tries}    ICMP Type={icmp_type}    rtt={((recv_time - send_time)*1000):.2f} ms    {addr[0]}    " , end='', flush=True)
                    try:
                        hostnamesent = gethostbyaddr(addr[0])[0]
                    except (herror, gaierror):
                        hostnamesent = "Unknown"
                    print(hostnamesent+"\n\n")
                
                elif icmp_type == 0: 
                    bytes = struct.calcsize("d")  
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0] 
                    print(f"TTL= {ttl}    trie={tries}    ICMP Type={icmp_type}    rtt={((recv_time - timeSent)*1000):.2f} ms    {addr[0]}    " , end='', flush=True)
                    try:
                        hostnamesent = gethostbyaddr(addr[0])[0]
                    except (herror, gaierror):
                        hostnamesent = "Unknown"
                    print(hostnamesent+"\n\n")
                    return 
                
                else: 
                    print("error")    
                break  

            finally:     
                mySocket.close()   

# To run traceroute for 4 continents it was better to run on specific IP Addresses than hostnames.

#if __name__ == "__main__":
    #host = input("Enter the host to ping (e.g., google.com): ")
    #get_route(host)

if __name__ == "__main__":
    host = input("Enter the IP Address to ping: ")
    get_route(gethostbyaddr(host)[0])