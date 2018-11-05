#
# SimpleVectorMapperTool.cpp
#  
#  Created on: Oct, 2018
#       Author: wntun (wntun.robust@gmail.com)
# 
#  
# this is a tool to generate simple vector map from waypoints for autoware users
# For map with many lanes, it is better to have connectedLanesInfo.csv to define which lane is connected to which lane.
# point.csv, dtlane.csv, lane.csv, node.csv


## Tips from Hatem
# (1) points from different lanes shouldn't be overlapped
# (2) lanes shouldn't be long (from one node to one node)
# (3) lanes should stop at branching or start from a branch (You shouldn't branch from the center of the lane)


import csv
import collections
import numpy as np
import sys

class Waypoint:
	def __init__(self, x, y, z, yaw, vel):
		# print(x)
		self.x = float(x)
		self.y = float(y)
		# self.z = z
		self.z = 0.0
		self.yaw = np.float64(yaw)
		self.vel = np.float64(vel)

	def __eq__(self, other):
		return (self.x==other.x and self.y==other.y and self.z==other.z and self.yaw==other.yaw and self.vel==other.vel)

	def __hash__(self):
		return hash((self.x, self.y, self.z, self.yaw, self.vel))

class Node:
	def __init__(self, nid, pid, x, y):
		self.nid = int(nid)
		self.pid = int(pid)
		self.x = np.float64(x)
		self.y = np.float64(y)
		# self.z = z
		self.z = 0

class Dtlane:
	def __init__(self, did, dist, pid, dir):
		self.did = int(did) 
		self.dist = int(dist)
		self.pid = int(pid)
		self.dir = np.float64(dir) 

	

class Lane:
	def __init__(self, lnId, did, blid, flid, bnid, fnid, jct, blid2, flid2, blid3, flid3, blid4, flid4, span, lcnt, lno, limitVel, refVel, laneChgFG):
		self.lnId = int(lnId)
		self.did = int(did)
		self.blid = int(blid)
		self.flid = int(flid)
		self.bnid = int(bnid)
		self.fnid = int(fnid) 
		self.jct = int(jct)
		self.blid2 = int(blid2)
		self.flid2 = int(flid2)
		self.blid3 = int(blid3)
		self.blid4 = int(blid4)
		self.flid2 = int(flid2)
		self.flid3 = int(flid3)
		self.flid4 = int(flid4)
		self.span = float(span)
		self.lcnt = int(lcnt) 
		self.lno = int(lno) 
		self.limitVel = np.float64(limitVel)
		self.refVel = np.float64(refVel)
		self.laneChgFG = int(laneChgFG)

class ConnectedLaneInfo:
	def __init__(self, t_id, t_start, t_end):
		self.id = int(t_id)
		self.t_start = int(t_start)
		self.t_end = int(t_end)

class StopLine:
	def __init__(self, temp_id, lid, tlid, signid, linkid):
		self.id = int(temp_id)
		self.lid = int(lid)
		self.tlid = int(tlid)
		self.signid = int(signid)
		self.linkid = int(linkid)

class Line:
	def __init__(self, lid, bpid, fpid):
		self.lid = int(lid)
		self.bpid = int(bpid) 
		self.fpid = int(fpid) 


def getLaneByDID(did, lanes):
	for i in range(0, len(lanes)):
		if did == lanes[i].did:
			return lanes[i].lnId

def getDTLaneByPID(pid, dtlanes):
	for i in range(0, len(dtlanes)):
		# print(dtlanes[i].pid)
		if pid == dtlanes[i].pid:
			# print(dtlanes[i].did)
			return dtlanes[i].did

def getDistinctWaypoints(waypoint_list):
	seen = set()
	unique = []
	for x in waypoint_list:
		if x not in seen:
			unique.append(x)
			seen.add(x)
	return unique

def getDistance(p1, p2):
	return np.sqrt(np.power(p1.x-p2.x,2)+np.power(p1.y-p2.y,2))


def getNearestNID(node1, lanes):
	min_distance = sys.float_info.max
	lid = -1
	nid = -1
	threshold = float(len(lanes))/(len(num_waypoints)*3)
	print("Threshold for nearest laneID of %d : %f" % (node1.nid, threshold))
	for i in range(0, len(node_list)-1):
		if node1.nid != node_list[i].nid and np.abs(node1.nid-node_list[i].nid)>threshold:
			p2 = node_list[i]
			distance = getDistance(node1, p2)
			# print(distance)
			if distance<min_distance:
				min_distance = distance
				nid = node_list[i].nid;

	return nid
	# return lid 


def readWaypointCSV(fileName):
	waypoints = []
	with open(fileName) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count==0:
				print('reading csv')
			else:
				#if line_count%10==0:
				wp = Waypoint(row[0], row[1], row[2], row[3], row[4]) 
				waypoints.append(wp)
			line_count += 1
	return waypoints

def readConnectedLaneCSV(fileName):
	# connected = []
	ids = []
	start = []
	end = []
	with open(fileName) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count==0:
				print("column names \n")
			else:
				ids.append(int(row[0]))
				start.append(int(row[1]))
				end.append(int(row[2]))
			line_count += 1
	return [ids, start, end]

def getNode(waypoints):
	acc = len(node_list)
	for i in range(0, len(waypoints)):
		n = Node(acc+i+1, acc+i+1, waypoints[i].x, waypoints[i].y)
		node_list.append(n)

def getDtlane(waypoints):
	acc = len(dtLane_list)
	# print(acc)
	for i in range(0, len(waypoints)):
		dt = Dtlane(i+1+acc, i, i+1+acc, waypoints[i].yaw)
		dtLane_list.append(dt)


# status : 1 => loop, 
# status : 2 => find nearest point from first lane to connect with end point of the second lane 
# status : 3 => find nearest point from first lane to connect with first point of the second lane 
# status : 4 => find nearest points from first lane to connect with two end points of second lane
def getLane(num_lanes, lanes_info, status):
	did_acc = 1
	for i in range(0, len(node_list)):
		temp_lnId = i+1
		temp_did = i+1 
		
		temp_bnid = node_list[i].nid  
		temp_fnid = temp_bnid + 1
		temp_jct = 0
		temp_blid2 = 0
		temp_flid2 = 0
		temp_blid3 = 0
		temp_flid3 = 0
		temp_blid4 = 0
		temp_flid4 = 0
		temp_span = 1
		temp_lcnt = 1
		temp_lno = 1
		temp_limitVel = 40
		temp_refVel = 40
		temp_laneChgFG = 0

		temp_flid = temp_lnId + 1

		if dtLane_list[i].dist == 0:
			temp_blid = 0
		else: 
			temp_blid = i 


		l = Lane(temp_lnId, temp_did, temp_blid, temp_flid, temp_bnid, temp_fnid, temp_jct, temp_blid2, temp_flid2, temp_blid3, temp_flid3, temp_blid4, temp_flid4, temp_span, temp_lcnt, temp_lno, temp_limitVel, temp_refVel, 
			temp_laneChgFG)
		lane_list.append(l)

	for i in range(0, num_lanes):
		last_index_lane = acc_waypoints[i]-1
		first_index_lane = 0
		if i>0:
			first_index_lane = acc_waypoints[i-1]
		#normal lane
		lane_list[last_index_lane].flid = 0

		if status[i]==1:
			nearestNID = getNearestNID(node_list[last_index_lane], lane_list[first_index_lane:last_index_lane+1])
			lane_list[nearestNID].blid = last_index_lane + 1
			lane_list[last_index_lane].flid = nearestNID + 1
			print("nearestNID : %d" % (nearestNID))
				
			# starting from the second lane <<joining>>
		elif status[i]==2:	
			nearestNID = getNearestNID(node_list[last_index_lane], lane_list)
			print("nearest %d" % nearestNID)
			if nearestNID > -1:
				if lane_list[nearestNID].blid2 == 0:
					lane_list[nearestNID].blid2 = lane_list[last_index_lane].lnId
				elif lane_list[nearestNID].blid3 == 0:
					lane_list[nearestNID].blid3 = lane_list[last_index_lane].lnId
				else:
					lane_list[nearestNID].blid4 = lane_list[last_index_lane].lnId
				lane_list[last_index_lane].flid = nearestNID + 1

		elif status[i]==3:			
			nearestNID = getNearestNID(node_list[first_index_lane], lane_list)
			print("nearest %d" % nearestNID)
			if nearestNID> -1:
				
				lane_list[first_index_lane].blid = nearestNID + 1
				if lane_list[nearestNID].flid2 == 0:
					lane_list[nearestNID].flid2 = lane_list[first_index_lane].lnId
				elif lane_list[nearestNID].flid3 == 0:
					lane_list[nearestNID].flid3 = lane_list[first_index_lane].lnId
				else:
					lane_list[nearestNID].flid4 = lane_list[first_index_lane].lnId
		
		elif status[i]==4:
			nearestNID = -1
			if i in lanes_info[0]:
				ind = lanes_info[0].index(i)
				start_index = 0 if lanes_info[2][ind]==0 else acc_waypoints[lanes_info[2][ind]-1]
				end_index = acc_waypoints[lanes_info[2][ind]]-1

				nearestNID = getNearestNID(node_list[last_index_lane], lane_list[start_index:end_index+1])
			else:
				nearestNID = getNearestNID(node_list[last_index_lane], lane_list)
			print("nearest %d" % nearestNID)
			if nearestNID > -1:								
				lane_list[last_index_lane].flid = nearestNID + 1
				if lane_list[nearestNID].blid2 == 0:
					lane_list[nearestNID].blid2 = lane_list[last_index_lane].lnId
				elif lane_list[nearestNID].blid3 == 0:
					lane_list[nearestNID].blid3 = lane_list[last_index_lane].lnId
				else:
					lane_list[nearestNID].blid4 = lane_list[last_index_lane].lnId

			nearestNID = -1
			if i in lanes_info[0]:
				ind = lanes_info[0].index(i)
				start_index = 0 if lanes_info[1][ind]==0 else acc_waypoints[lanes_info[1][ind]-1]
				end_index = acc_waypoints[lanes_info[1][ind]]-1

				nearestNID = getNearestNID(node_list[first_index_lane], lane_list[start_index:end_index+1])

			else:
				nearestNID = getNearestNID(node_list[first_index_lane], lane_list)
			print("nearest %d" % nearestNID)
			if nearestNID> -1:
				
				lane_list[first_index_lane].blid = nearestNID + 1
				if lane_list[nearestNID].flid2 == 0:
					lane_list[nearestNID].flid2 = lane_list[first_index_lane].lnId
				elif lane_list[nearestNID].flid3 == 0:
					lane_list[nearestNID].flid3 = lane_list[first_index_lane].lnId
				else:
					lane_list[nearestNID].flid4 = lane_list[first_index_lane].lnId


def getLines(stopLines_end_points):
	lines = []
	for i in range(0, len(stopLines_end_points)/2):
		temp_lid = i+1
		temp_bpid = stopLines_end_points[i*2]
		temp_fpid = stopLines_end_points[i*2+1]

		l = Line(temp_lid, temp_bpid, temp_fpid, 0, 0)
	return lines


def getStopLine(stopLines_middle_points, lanes):
	stopLines = []
	for i in range(0, len(stopLines_middle_points)):
		temp_id = i+1
		temp_lid = i+1
		temp_linkID = getNearestLID(stopLines_middle_points[i], lanes)

		sl = StopLine(temp_id, temp_lid, 0, 0, temp_linkID)
		stopLines.push_back(sl)
	return stoplines 



def writePoint(waypoints):
	with open('vm/point.csv', mode='w') as point_file:
		col_names = ['PID', 'B', 'L', 'H', 'Bx', 'Ly', 'ReF', 'MCODE1', 'MCODE2', 'MCODE3']
		point_writer = csv.DictWriter(point_file, fieldnames=col_names)
		point_writer.writeheader()
		for i in range(0, len(waypoints)):
			point_writer.writerow({'PID': (i+1), 'B': 0, 'L': 0, 'H': waypoints[i].z, 'Bx': waypoints[i].y, 'Ly': waypoints[i].x, 
				'ReF': 0, 'MCODE1': 0, 'MCODE2': 0, 'MCODE3': 0})

def writeNode(nodes):
	with open('vm/node.csv', mode='w') as node_file:
		col_names = ['NID', 'PID']
		node_writer = csv.DictWriter(node_file, fieldnames=col_names)
		node_writer.writeheader()
		for i in nodes:
			node_writer.writerow({'NID': i.nid, 'PID': i.pid})

def writeDtlane(dtLanes):
	with open('vm/dtlane.csv', mode='w') as dt_file:
		col_names = ['DID', 'Dist', 'PID', 'Dir', 'Apara', 'r', 'slope', 'cant', 'LW', 'RW']
		dt_writer = csv.DictWriter(dt_file, fieldnames=col_names)
		dt_writer.writeheader()
		for i in range(0, len(dtLanes)):
			dt_writer.writerow({'DID': dtLanes[i].did, 'Dist': dtLanes[i].dist, 'PID': dtLanes[i].pid, 'Dir': dtLanes[i].dir, 'Apara': 0, 'r': 0, 'slope': 0, 'cant': 0, 'LW': 0, 'RW': 0})

def writeLane(lanes):
	with open('vm/lane.csv', mode='w') as lane_file:
		col_names = ['LnID', 'DID', 'BLID', 'FLID', 'BNID', 'FNID', 'JCT', 'BLID2', 'BLID3', 'BLID4', 'FLID2', 'FLID3', 'FLID4', 'ClossID', 
		'Span', 'LCnt', 'Lno', 'LaneType', 'LimitVel', 'RefVel', 'RoadSecID', 'LaneChgFG']
		lane_writer = csv.DictWriter(lane_file, fieldnames=col_names)
		lane_writer.writeheader()
		for i in range(0, len(lanes)):
			lane_writer.writerow({'LnID': lanes[i].lnId,'DID': lanes[i].did,'FLID': lanes[i].flid, 'BLID': lanes[i].blid,'BNID': lanes[i].bnid,'FNID': lanes[i].fnid,
				'JCT': lanes[i].jct,'BLID2': lanes[i].blid2,'BLID3': lanes[i].blid3,'BLID4': lanes[i].blid4,'FLID2': lanes[i].flid2,'FLID3': lanes[i].flid3,'FLID4': lanes[i].flid4,'ClossID': 0,'Span': lanes[i].span,
				'LCnt': lanes[i].lcnt,'Lno': lanes[i].lno,'LaneType': 0,'LimitVel': lanes[i].limitVel,'RefVel': lanes[i].refVel,'RoadSecID': 0,'LaneChgFG': lanes[i].laneChgFG})

def writeStopLine(stopLines):
	with open('vm/stopline.csv', mode='w') as stopline_file:
		col_names = ['ID', 'LID', 'TLID', 'SignID', 'LinkID']
		stopline_writer = csv.DictWriter(stopline_file, fieldnames=col_names)
		stopline_writer.writeheader()
		for i in range(0, len(stopLines)):
			stopline_writer.writerow({'ID': stopLines[i].id, 'LID': stopLines[i].lid, 'TLID': stopLines[i].tlid, 'SignID': stopLines[i].signid, 'LinkID': stopLines[i].linkid})

def writeLine(lines):
	with open('vm/line.csv', mode='w') as line_file:
		col_names = ['LID', 'BPID', 'FPID', 'BLID', 'FLID']
		line_writer = csv.DictWriter(line_file, fieldnames=col_names)
		line_writer.writeheader()
		for i in range(0, len(lines)):
			line_writer.writerow({'LID': lines[i].lid, 'BPID': lines[i].bpid, 'FPID': lines[i].fpid, 'BLID': 0, 'FLID': 0})



if __name__=="__main__":

	num_lanes = 24+34
	fileNames = []
	for i in range(0, num_lanes):
	# 	# temp_name = 'csv/Daegu_Loop'+str(i+1)+'.csv'
		temp_name = 'hq_waypoints/waypoints_'+str(i)+'.csv'
		fileNames.append(temp_name)

	num_waypoints = []
	waypoints =  []

	for i in range(0,num_lanes):
		print i
		temp_waypoint = readWaypointCSV(fileNames[i])
		num_waypoints.append(len(temp_waypoint))
		waypoints = waypoints + temp_waypoint

	[bid, start, end] = readConnectedLaneCSV('hq_waypoints/connectedLanesInfo.csv')
	lane_info = [bid, start, end]

	acc_waypoints = []
	for i in range(0, num_lanes):
		sum = 0
		for j in range(0, i+1):
			sum += num_waypoints[j]
		acc_waypoints.append(sum)
	dtLane_list = []

	for i in range(0,num_lanes):
		start = 0
		if i!= 0:
			start = acc_waypoints[i-1]
		getDtlane(waypoints[start: acc_waypoints[i]])
	# 	# print(len(dtLane_list))

	node_list = []
	for i in range(0, num_lanes):
		start = 0
		if i!= 0:
			start = acc_waypoints[i-1]
		getNode(waypoints[start: acc_waypoints[i]])


	lane_list = []

	laneStatus = []
	for i in range(0, 24):
		laneStatus.append(0)

	laneStatus[6] = 3
	laneStatus[7] = 2

	for i in range(0, 34):
		laneStatus.append(4)

	getLane(num_lanes, lane_info, laneStatus)

	writePoint(waypoints)
	writeDtlane(dtLane_list)
	writeNode(node_list)
	writeLane(lane_list)

