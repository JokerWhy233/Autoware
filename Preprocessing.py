#
# Preprocessing.cpp
#  
#  Created on: Oct, 2018
#       Author: wntun (wntun.robust@gmail.com)
# 
#  
## This is to preprocess High Quality (HQ) map from the competition to generate waypoints formatted in Autoware. 
## It calculates heading with (np.arctan2(yt[i]-yt[i-1], xt[i]-xt[i-1]))
## splitLine is to find points for straight line
## bezierCurve is to find points for curve. (However, it's not accurate!!!)
## combineSegments is to combine two segments with one straight line.
## Since Autoware works in ENU, latitude and longitude are converted to ENU in toENU.
## One additional file is connectedLanesInfo.csv to define which lane to connect from endpoints of which lane.


import scipy.io
import numpy as np 
import matplotlib.pyplot as plt
import csv


def splitLine(lat1, lat2, lon1, lon2, count):
	lat = []
	lon = []
	count = count + 1
	# print(lat1)

	d = np.sqrt(np.power(lat1-lat2,2)+np.power(lon1-lon2,2))/count
	fi = np.arctan2(lon2-lon1, lat2-lat1)

	for i in range(0, count+1):
		temp_lat = lat1 + i *d * np.cos(fi)
		temp_lon = lon1 + i * d * np.sin(fi)
		lat.append(temp_lat)
		lon.append(temp_lon)
	# print(lat)

	return [lat, lon]

# ref https://en.wikipedia.org/wiki/B%C3%A9zier_curve
# ref 
def bezierCurve(p0_lat, p1_lat, p2_lat, p0_lon, p1_lon, p2_lon, count):
	count = count +1
	interval = 1.0/count
	lat = []
	lon = []
	for i in range(0,count+1):
		t = interval * i
		temp_lat = (1-t)* ((1-t)*p0_lat + t* p1_lat) + t*((1-t)*p1_lat + t * p2_lat)
		temp_lon = (1-t) *((1-t)*p0_lon + t* p1_lon) + t*((1-t)*p1_lon + t * p2_lon)		
		lat.append(temp_lat)
		lon.append(temp_lon)
	return [lat, lon]


def combineSegments(straightSeq):
	seg_latt = []
	seg_lont = []
	# print(len(seg_lat[5])-1)

	for i in range(0, len(straightSeq)-1):
		start = straightSeq[i]
		end = straightSeq[i+1]
		# print("%d and %d " % (start, end))
		[new_lat, new_lon] = splitLine(seg_lat[start][len(seg_lat[start])-1],seg_lat[end][0],seg_lon[start][len(seg_lon[start])-1], seg_lon[end][0],10)
		if len(seg_latt)==0:
			seg_latt = seg_latt + seg_lat[start] + new_lat + seg_lat[end]
			seg_lont = seg_lont + seg_lon[start] + new_lon + seg_lon[end]
		else:
			seg_latt = seg_latt + new_lat + seg_lat[end]
			seg_lont = seg_lont + new_lon + seg_lon[end]
	if(len(straightSeq)==1):
		seg_latt = seg_lat[straightSeq[0]]
		seg_lont = seg_lon[straightSeq[0]]
	return [seg_latt, seg_lont]



def lengthOfDegreeLongitude(refLatDeg):
	ref_latitude_rad = refLatDeg * np.pi / 180
	p1 = 111412.84 
	p2 = -93.5 
	p3 = 0.118 

	res = (p1 * np.cos(ref_latitude_rad)) + (p2 * np.cos(3 * ref_latitude_rad)) + (p3 * np.cos(5 * ref_latitude_rad))
	return res

def lengthOfDegreeLatitude(refLatDeg):
	ref_latitude_rad = refLatDeg * np.pi / 180
	m1 = 111132.92 
	m2 = -559.82 
	m3 = 1.175
	m4 = -0.0023 
	res = m1 + (m2 * np.cos(2 * ref_latitude_rad)) + (m3 * np.cos(4 * ref_latitude_rad)) + (m4 * np.cos(6 * ref_latitude_rad))
	return res

def toEnu(lat, lon):
	refLatLon = [35.8349389, 128.6811557]
	xt = (lon-refLatLon[1]) * lengthOfDegreeLongitude(refLatLon[0])
	yt = (lat - refLatLon[0]) * lengthOfDegreeLatitude(refLatLon[0])
	yawt = np.zeros(xt.size, dtype=np.float)
	for i in range(1, len(xt)):
		dist = np.sqrt(np.power(xt[i]-xt[i-1],2)+np.power(yt[i]-yt[i-1],2))
		if(dist)>0.2:
			yawt[i] = (np.arctan2(yt[i]-yt[i-1], xt[i]-xt[i-1]))
		else:
			yawt[i] = yawt[i-1]
	# print(type(x))
	yawt[0] = yawt[1]
	# print(yawt)
	return [xt, yt, yawt]


def writeWaypointsCVS(enu_x, enu_y, yaw, filename):
	# print(type(lat))
	with open(filename, mode='w') as xy_file:
		col_names = ['x', 'y', 'z', 'yaw', 'velocity', 'change_flag']
		file_writer = csv.DictWriter(xy_file, fieldnames=col_names)
		file_writer.writeheader()
		for i in range(0, len(enu_x)):
			file_writer.writerow({'x': enu_x[i], 'y':enu_y[i], 'z':1.48, 'yaw': yaw[i], 'velocity':0,'change_flag': 0})

def writeConnectedLanesInfo(lane_info, num_straight_lanes, filename):
	with open(filename, mode='w') as c_file:
		col_names = ['b_index','start', 'end']
		file_writer = csv.DictWriter(c_file, fieldnames=col_names)
		file_writer.writeheader()
		for i in range(0, len(lane_info)):
			file_writer.writerow({'b_index': (i+num_straight_lanes),'start': lane_info[i][0], 'end': lane_info[i][1]})

mat = scipy.io.loadmat('Daegu_Link.mat')

link_data = mat['link_data']

latitude = []
longitude = []
for i in range(0, link_data.size):
	temp_lane = link_data[0][i]
	temp_lat = temp_lane[2].tolist()
	temp_lon = temp_lane[1].tolist()
	latitude.append(temp_lat)
	longitude.append(temp_lon)

# print latitude[0][0]
######## NEVER CHANGE THESE INDICES!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
indices = [[0,2,4], [1,3,5], [6,8,10,12,14,16,18], [7,9,11,13,15,17,19],[20,22,24],[21,23,25],[26,28,30,32],[27,29,31,33],
[34,36,39,43],[35,37,38,44],[40,41,42],[45,47,49,51,53,57],[46,48,50,52,54,58], [55,56], [59,61,64,65],[60,62,63,66],
[67,69,71,73,75,77,79,81,83,85,87],
[68,70,72,74,76,78,80,82,84,88],[89,91,93,95,99,102],[90,92,94,96,100,103],[97,98,101],[104,107],[105,108],[106,109],[114,115,118,121],
[110,112,116,119,122],[111,113,117,120,123],
[124,126],[125,127],[128,129,130],[131,132],[133,134],[139],[135,136],[137,138],[140,142],[141,143],[148,150],[149,151],
[153,155,157,159],[152,154,156,158],
[160,162],[161,163],[164,167],[165,166],[168,171,174,176],[169,172,175,177],[170,173],[178,180],[179,181],[182,184],[183,185],[186,188],[187,189],
[190,192],[191,193],[194,196],[195,197],[198],[199],[200,201,202],[203,204,205],[206,207,208],[209,210,211],[212,213,214],[215,216,217],
[218,220],[219,221],
[222,224,226,228],[223,225,227,229],[230,232],[231,233],[234,236,238,240],[235,237,239,241],[243,242],[244,245,246,247],[248,249,250,251],[144,146],[145,147]]

seg_lat = []
seg_lon = []
text = []
for i in range(0, len(indices)):
	temp_lat = []
	temp_lon = []
	for j in range(0, len(indices[i])):
		for p in range(0, len(latitude[indices[i][j]])):
			temp_lat = temp_lat + latitude[indices[i][j]][p]
			temp_lon = temp_lon + longitude[indices[i][j]][p]

	seg_lat.append(temp_lat)
	seg_lon.append(temp_lon)


# website https://www.fcc.gov/media/radio/dms-decimal
# [73,46],[72,45] => 35.835,35.834997, 128.681254,128.681214
# [57,67] => 35.834947, 128.681114 
# [11,0] => 35.839061,128.6894
# [23,26] => 35.839117,128.689444
controlPoints_lat = [35.8351, 35.834997,  35.839042, 35.839089,35.836611,35.836633,35.836581,
35.836619,35.836381,35.836372,35.835631,35.835583,35.835622,35.835581,35.835894,35.835886,35.835831,35.835836,
35.834856,35.834778,35.834864,35.834794,35.834583,35.834617,35.83455,35.8346,35.833939,35.833917,35.833639,35.833694,
35.834333,35.834361,35.834333,35.834356]
controlPoints_lon = [128.681333, 128.681114, 128.689389,  128.689417,128.681511,128.681528,128.681489,
128.681444,128.683111,128.683069,128.682897,128.682919,128.682939,128.682897,128.681339,128.681236,128.681283,128.681322,
128.682708,128.682725,128.682778,128.682781,128.684925,128.684869,128.684919,128.685003,128.684861,128.684836,128.687503,128.687497,
128.68765,128.687667,128.687611,128.687594]

indicesToStright = [[1,3,5,7,71,73],[0,2,4,6,70,72],[66,68,14,16,18,22],[67,69,15,17,19,23], [46,49,51,36,78,38,9,12], [45,48,50,35,77,37,8,11],[74],[47], 
[25,27,40,41,43,52,54,56],[26,28,39,42,44,55,57], [58,60],[61,59],[62],[63],[65,63],[62,64],[75],[76],[33],[31],[30],[34],[32],[29]]
indicesToCurve = [[74,47],[56,66], [12,1], [22,25],[59,51],[59,54],[49,58],[52,58],[63,61],[60,62],[62,76],
[75,63],[65,76],[75,64],[76,49],[76,56],[54,75],[46,75],[64,73],[64,68],[71,65],[66,65],[69,33],[6,33],[31,15],[31,70],[30,31],
[33,34],[34,32],[29,30],[32,17],[32,6],[15,29],[4,29]]

connectedLanesInfo = np.zeros((len(indicesToCurve),2), dtype=np.int)
for c in range(0, len(indicesToCurve)):
	start = indicesToCurve[c][0]
	end = indicesToCurve[c][1]
	# print("%d, %d \n" %(start, end))
	for i in range(0,len(indicesToStright)):
		if start in indicesToStright[i]:
			connectedLanesInfo[c][0] = i
		if end in indicesToStright[i]:
			connectedLanesInfo[c][1] = i


writeConnectedLanesInfo(connectedLanesInfo, len(indicesToStright), 'hq_waypoints/connectedLanesInfo.csv')


new_seg_lat = []
new_seg_lon = []
for i in range(0, len(indicesToStright)):
	[new_lat, new_lon] = combineSegments(indicesToStright[i])
	new_seg_lat.append(new_lat)
	new_seg_lon.append(new_lon)
	text.append('seg_'+str(i))

b_seg_lat = []
b_seg_lon = []
for i in range(0, len(indicesToCurve)):
	start = indicesToCurve[i][0]
	end = indicesToCurve[i][1]
	p0_lat = seg_lat[start][len(seg_lat[start])-1]
	p0_lon = seg_lon[start][len(seg_lon[start])-1]
	p2_lat = seg_lat[end][0]
	p2_lon = seg_lon[end][0]
	p1_lat = controlPoints_lat[i]
	p1_lon = controlPoints_lon[i]
	[b_lat, b_lon] = bezierCurve(p0_lat, p1_lat, p2_lat, p0_lon, p1_lon, p2_lon, 10)
	b_lat = seg_lat[start][len(seg_lat[start])-3:len(seg_lat[start])-1] + b_lat + seg_lat[end][0:3]
	b_lon = seg_lon[start][len(seg_lon[start])-3:len(seg_lon[start])-1] + b_lon + seg_lon[end][0:3]
	b_seg_lat.append(b_lat)
	b_seg_lon.append(b_lon)
	text.append('b_seg'+str(i))

for i in range(len(b_seg_lon)):
	plt.plot(b_seg_lon[i], b_seg_lat[i])


x = []
y = []
yaw = []
for i in range(0, len(new_seg_lon)):
	[temp_x, temp_y, temp_yaw] = toEnu(np.asarray(new_seg_lat[i]), np.asarray(new_seg_lon[i]))
	x.append(temp_x)
	y.append(temp_y)
	yaw.append(temp_yaw)

for i in range(0, len(b_seg_lon)):
	[temp_x, temp_y, temp_yaw] = toEnu(np.asarray(b_seg_lat[i]), np.asarray(b_seg_lon[i]))
	x.append(temp_x)
	y.append(temp_y)
	yaw.append(temp_yaw)

for i in range(0, len(x)):
	writeWaypointsCVS(x[i], y[i], yaw[i], 'hq_waypoints/waypoints_'+str(i)+'.csv')

 
for i in range(0, len(new_seg_lon)):
	plt.plot(new_seg_lon[i], new_seg_lat[i])


plt.legend(text)

plt.show()
