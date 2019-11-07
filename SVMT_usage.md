### SVMT Tool

The main file is SimpleVectorMapperTool.py.

The two preprocessing files are to generate Autoware-format waypoint files from latitude and longitute values.

#### Usage 
Before we update the program, please prepare waypoint files naming with 'waypoints_[num].csv' where num starts from 0 to (1-num-lanes).

In the "main" part, please update the following
- num_lanes : number of waypoint files
- connectedLaneInfo_file : file name of connected lanes information (please check the file format in my paper)
- lane_status : prepare the lane status for each lane according to the lane type for connection 
  - status : 1 => loop (connect itself)
  - status : 2 => find nearest point from the first lane to connect with end point of the second lane 
  - status : 3 => find nearest point from the first lane to connect with first point of the second lane 
  - status : 4 => find nearest points from the first lane to connect with two end points of second lane
 
where the first lane means the just-newly constructed lane network, the second lane is the current index lane
(For example, if we have 5 waypoint files, assume the current index is 3. Then, the first lane means the lane network which includes waypoints_0, waypoints_1, and waypoints_2 files. 
  The second lane means waypoints_3 file.)

#### Please cite this following [this paper](https://ieeexplore.ieee.org/abstract/document/8679340) if the code is useful to you!

