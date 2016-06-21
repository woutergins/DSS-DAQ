#!/bin/env python
#
# MIDAS tapeserver SHM demo client
# Subscribe to data over 0mq and parse tape headers
# P.Rahkila June 2016
#
import zmq
import struct

# open 0mq subscriber and subscribe to all data
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect ("tcp://localhost:5678")
socket.setsockopt(zmq.SUBSCRIBE, "")

# loop forever
while True:
	# receive block and parse MIDAS tape header 
	block = socket.recv()
	tapehdr = struct.unpack('8si4hi',block[0:24])
	print tapehdr
