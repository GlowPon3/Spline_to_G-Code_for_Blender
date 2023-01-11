# Spline_to_G-Code_for_Blender
A simple python script to output g-code directly from blender using a spline.

Be sure to modify the output file location to the locationyou want the g-code file saved.
Script looks for a curve named 'BezierCurve' to do it's calculations on
Every point controlls the action required to get TO the point.
Tilt controls the speed of the movement where +360 is 2x movement and -360 is half movement (f_r)
Radius controls the extrusion as a direct multiplier based on segment length
Softbody Weight controls extrusion based on forced extrusion amount (f_e) reguardless of segment length
