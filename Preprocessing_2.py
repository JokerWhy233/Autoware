#
# Preprocessing_2.cpp
# * 
#*  Created on: Oct 24, 2018
# *      Author: wntun (wntun.robust@gmail.com)
# *
# * It reads csv file : lat, lon, heading (radian) and converts to waypoints csv file used in autoware
# * Autoware sometimes fails to read csv waypoints file. Then, convert it to txt file format (x, y, z, velocity)
# *
# */

import csv
import numpy as np

def readCSV(fileName):
	waypoints = []
	lat = []
	lon = []
	heading = []
	with open(fileName) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		row_count = 0
		for row in csv_reader:
			if row_count>1:
				row_count+=1
				if row_count%10==0:
					t_lat = float(row[0])
					t_lon = float(row[1])
					t_heading = float(row[2])
					lat.append(t_lat)
					lon.append(t_lon)
					heading.append(t_heading)
			else:
				row_count+=1
	return [lat, lon, heading]

def lengthOfDegreeLongitude(refLatDeg):
	ref_latitude_rad = refLatDeg * np.pi / 180.0
	p1 = 111412.84 
	p2 = -93.5 
	p3 = 0.118 
	res = (p1 * np.cos(ref_latitude_rad)) + (p2 * np.cos(3 * ref_latitude_rad)) + (p3 * np.cos(5 * ref_latitude_rad))
	return res

def lengthOfDegreeLatitude(refLatDeg):
	ref_latitude_rad = refLatDeg * np.pi / 180.0
	m1 = 111132.92 
	m2 = -559.82 
	m3 = 1.175
	m4 = -0.0023 
	res = m1 + (m2 * np.cos(2 * ref_latitude_rad)) + (m3 * np.cos(4 * ref_latitude_rad)) + (m4 * np.cos(6 * ref_latitude_rad))
	return res

def toEnu(lat, lon):
	refLatLon = [37.540032, 127.0709544] ##For Konkuk
	# refLatLon = [35.8349389, 128.6811557] ## For Daegu
	xt = (lon-refLatLon[1]) * lengthOfDegreeLongitude(refLatLon[0])
	yt = (lat - refLatLon[0]) * lengthOfDegreeLatitude(refLatLon[0])
	return [xt, yt]

def writeWayPointCSV(x,y,yaw, fileName):
	with open(fileName, mode='w') as line_file:
		col_names = ['x', 'y', 'z', 'yaw', 'velocity', 'change_flag']
		line_writer = csv.DictWriter(line_file, fieldnames=col_names)
		line_writer.writeheader()
		for i in range(0, len(x)):
			line_writer.writerow({"x":x[i], 'y':y[i], 'z':0.0, 'yaw':yaw[i], 'velocity':0.0, 'change_flag':0})


if __name__=='__main__':
	[lat, lon, heading] = readCSV('waypoints.csv')
	[x,y] = toEnu(np.asarray(lat), np.asarray(lon))
	writeWayPointCSV(x,y,heading, 'enu_waypoints.csv')
