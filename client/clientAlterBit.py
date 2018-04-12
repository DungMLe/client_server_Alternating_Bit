# Name: Dung Le
# Python version 2.7 
#				 

from socket import *
import sys
import time
import json

serverName = '127.0.0.1'
serverPort = 6000
bufferSize = 1024
ACK, Seq, byte = 0, 0, 0


clientSocket = socket(AF_INET, SOCK_DGRAM)

requestMsg = raw_input("Enter file name: ")
#print(requestMsg)

# Initialization process to send file name
clientSocket.settimeout(2)
startTime = time.time()

counter = 0
clientSocket.sendto(requestMsg.encode(), (serverName, serverPort))
while True:
	try:
		initMesg, serverAddress = clientSocket.recvfrom(bufferSize)
		clientSocket.settimeout(None)
		initMesg = json.loads(initMesg.decode())
		# If the message has been received correctly, set ACK equal to sequence number of package. 
		print(initMesg.get("d"))
		ACK = initMesg.get("seq")
		print "ACK = ", ACK
		# Send back ACK number for Seq number of the successful received packet
		clientSocket.sendto(str(ACK), serverAddress)
		break
		
	except timeout as err:
		counter += 1
		if counter >= 3: # After sending 3 times, have not received any thing 
			print "Request ", err, " ! Cannot reach server."
			break
	
	

with open('text.txt', 'wb') as f:
	print "File ", requestMsg, " has opened..."
	print("Receiving data...")
	previousSeq = ACK
	count = 0
	while True:
		clientSocket.settimeout(2)
		data, serverAddress = clientSocket.recvfrom(2000)
		clientSocket.settimeout(None)
		#print(len(data))
		data = json.loads(data.decode())
		ACK = data.get("seq") # Get sequence number of the packet
		# print "ACK = ", ACK
		mesg = data.get("d") # Get message from data from the packet
		
		if mesg == "y":
			break
		
		#print(data.decode())
		# if not mesg:
			# break
		#sys.getsizeof(mesg)
		if previousSeq != ACK:
			f.write(mesg)
			previousSeq = ACK
			byte = byte + len(mesg)
			clientSocket.sendto(str(ACK), serverAddress)
			count += 1
			print "ACK = ", ACK
		else:
			clientSocket.sendto(str(ACK), serverAddress)
		
f.close()
print "Total of ", byte, " bytes received", ". Number of packets sent is ", count
print("Successful received data!")
clientSocket.close()
print("Connection closed...")
		
		

