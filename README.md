# Spline_to_G-Code_for_Blender
A simple python script to output g-code directly from blender using a spline.

KEEP ALL POINTS ABOVE Z=0 ! ! !
This script is for absolute positioning.  Make sure to locate your spline in the blender file in reference to your printer's printspace. (IE all axes positive)

Be sure to modify the output file location to the locationyou want the g-code file saved.
Script looks for a curve named 'BezierCurve' to do it's calculations on
Every point controlls the action required to get TO the point.
Tilt controls the speed of the movement where +360 is 2x movement and -360 is half movement (f_r)
Radius controls the extrusion as a direct multiplier based on segment length
Softbody Weight controls extrusion based on forced extrusion amount (f_e) reguardless of segment length


For visualization purposes, it is best to scale all handles to 0 as the script is using the 'curve' as a polyline.
