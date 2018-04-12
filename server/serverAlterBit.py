# Name: Dung Le
# Python 2.7 
from socket import *
import time
import json

serverPort = 6000
serverSocket = socket(AF_INET, SOCK_DGRAM)
bufferSize = 1024
alpha, beta = 0.125, 0.25
countACK = 0 # Count number of ACKs sent back from client
serverSocket.bind(('',serverPort))



while True:
	estimatedRTT, ACK, Seq, startTime, endTime = 0, 0, 0, 0, 0
	sampleRTT, devRTT, timeOut = 0, 0, 0
	countPackets = 0
	# Sender always waiting for calls from receivers 
	print("Server is ready to receive...")
	recvMesg, clientAddress = serverSocket.recvfrom(bufferSize)
	print "Receiving request for: ", recvMesg.decode()
	
	initMesg = "Server accepts connection and sends data...!\n"
	# ...
	data = json.dumps({"seq":Seq, "d":initMesg})
	serverSocket.sendto(data, clientAddress)
	# Initial timeout to 1 second to find estimatedRTT
	serverSocket.settimeout(1) 
	startTime = time.time()
	# ...
	try:
		ACK, clientAddress = serverSocket.recvfrom(bufferSize)
		endTime = time.time()
		sampleRTT = endTime - startTime # 1st initial  estimatedRTT
		estimatedRTT = sampleRTT		# 1st initial  sampleRTT
		timeOut = estimatedRTT + 4*devRTT  # 1st initial  timeout interval
		# Set the previous ACK number to the sent package's Seq number
		previousACK = Seq
		print "previousACK = ", previousACK
		# Flip the bit of Seq number
		Seq = abs(Seq - 1)
		print "Seq = ", Seq
		
		serverSocket.settimeout(None) # Stop timmer
	# If first initilization was not successful, then server goes back to busy waiting	
	except timeout as err:
		serverSocket.settimeout(None)
		continue
		
	#--------------------------------------------------------------------------------#
	# Start sending file ...
	resend = False
	try:
		with open(recvMesg.decode(), 'r') as f:
			line = f.read(bufferSize)
			data = json.dumps({"seq":Seq, "d":line})
			while (line): # Keep reading file until the file is empty
				#print(line)
				
				serverSocket.sendto(data.encode(), clientAddress)
				if resend == False:
					startTime = time.time() # Start counting time... 
				serverSocket.settimeout(timeOut)
				
				try:
					ACK, clientAddress = serverSocket.recvfrom(bufferSize)
					endTime = time.time() # End counting time... 
					serverSocket.settimeout(None) # Stop timmer 
					print "ACK = ", ACK
					print "previousACK = ", previousACK
					print "Seq = ", Seq, "\n\n"
					# If duplicate ACK number is sent back from receiver due to premature timeout
					# then ignore, else then calculate new timeOut, set the previousACK, and
					# flip the Seq number.
					while previousACK == ACK: # Busy waiting for correct ACK number
						print "Busy wait..."
						ACK, clientAddress = serverSocket.recvfrom(bufferSize)
					# if previousACK != ACK:
					# Then set previousACK to sent package's Seq number
					previousACK = Seq
					
					
					countPackets += 1
					sampleRTT = endTime - startTime
					estimatedRTT = (1-alpha) * estimatedRTT + alpha * sampleRTT
					devRTT = (1 - beta) * devRTT + beta * abs(estimatedRTT-sampleRTT)
					timeOut = estimatedRTT + 4*devRTT
						
					
					resend = False
				# If timeout exception happens due to lost package sent from server, or lost ACK 
				# sent back from receiver
				except timeout as err:
					resend = True
					print "resend..."
					continue # Then go back to retransmit data
				# Flip the bit of Seq number	
				Seq = abs(Seq - 1)
				line = f.read(bufferSize)
				data = json.dumps({"seq":Seq, "d":line})
				
		f.close()
	except IOError:
		errorMsg = "Wrong file or file path"
		serverSocket.sendto(errorMsg.encode(), clientAddress)
    
	Seq = abs(Seq - 1)
	endRequest = "y" # Temp variable to close client side
	data = json.dumps({"seq": Seq, "d": endRequest})
	serverSocket.sendto(data.encode(), clientAddress)
	
	print("Data has been sent successfully! Server will wait for new requests\n")
	print countPackets, " packets were sent"
	break
	#serverSocket.settimeout(None)
	
	
serverSocket.close()