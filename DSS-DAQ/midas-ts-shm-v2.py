#!/bin/env python
#
# MIDAS tapeserver SHM demo server
# Read blocks from shared memory and relay over 0mq
# P.Rahkila June 2016
#
import mmap
import struct
import time
import zmq

# open 0mq publisher for data at port 5678
# context = zmq.Context()
# socket = context.socket(zmq.PUB)
# socket.bind("tcp://*:5678")

# open the linux shm device for tapeserver at address 10205
f = open('/dev/shm/SHM_110205','r')
mm = mmap.mmap(f.fileno(), 0, mmap.MAP_PRIVATE, mmap.PROT_READ)

# retrieve settings from the ts data header, described in tsspy.h
(oset,cnt,bsize,last,maxcnt,none,none,none) = struct.unpack('8i',mm[:32])
oldage = struct.unpack('l',mm[32:40])[0]-1

# loop forever
while True:
	# find available blocks
	nextage = struct.unpack('l',mm[32:40])[0]
	block_ages = struct.unpack('128l',mm[40:1064])
	# if too many blocks received since last read, reset
	if(nextage - oldage) >= cnt:
		oldage = nextage
		continue
	# loop over all blocks received since last read
	for age in range(oldage+1,nextage):
		oldage = age
		# find the index for block with certain age
		idx = block_ages.index(age)
		offset = oset+bsize*idx
		block = mm[offset:offset+bsize]
		# publish data over 0mq
		# socket.send(block)
		print(block)
        # if no new data received, sleep a millisecond
	if nextage == struct.unpack('l',mm[32:40])[0]:
		time.sleep(0.001)
# clean up
mm.close()
f.close()
