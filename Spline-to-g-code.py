import bpy
import math

# Get a reference to the curve object
curve_object = bpy.data.objects['BezierCurve']
# Set the extrusion multiplier (mm3 per cm)
e_m = 4/10
# Set the signifigance value (Default 3 decimal places)
d = 4
# Set the feedrate
f_r = 1200
# add debug toggle
debug_g = 0
# Set f_e as the maximum amoutn of extrusion that can be added per point.
f_e = 1# Set filename and location
g_file = 'C:/Directory/goes/here/spline.gcode'

# Open g-code file for output
with open(g_file, 'w') as f:
    # write the start gcode to the file
    f.write(f""";start g-code
M221 T0 S100.00
M140 S55.00
M190 S55.00
M104 T0 S215.00
M109 T0 S215.00
T0
G28 ;Home
G92 E0 ;Reset Extruder
G1 Z2.0 F3000 ;Move Z Axis up
G90 ;Set absolute position mode
;start g-code
;Begin drawing spline by drawing to the first point
""")
    #set the last_vertex vars to the object's location
    x2 = round(curve_object.location.x, d)
    y2 = round(curve_object.location.y, d)
    z2 = round(curve_object.location.z, d)
    # Iterate over the vertices of the mesh rounding where needed
    for point in curve_object.data.splines.active.bezier_points:
        x1 = round(point.co.x, d)
        y1 = round(point.co.y, d)
        z1 = round(point.co.z, d)
        w1 = round(point.weight_softbody, d) * f_e # let weight add a percentage of f_e to the extrusion when approaching this point even with no motion
        r1 = round(point.radius, d) # let radius control the amount of extrustion when approcaching this point
        t1 = round(point.tilt, d) # let tilt control the speed the nozzle's movement when approching this point
        s1 = round(((t1 / (math.pi * 2))*f_r) + f_r) # Let the tilt add a multiple of the feedrate back to the feedrate
        # multiply the flow by the distance travelled since last_vertex and by the radius and add the forced extrusion
        e1 = round((math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) * e_m * r1), d) + w1
        # get the same result of the above for debugging without the radius or weight multipliers involved.
        e2 = round((math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) * e_m ), d)
        t2 = round(((t1 / 2) / math.pi) * 100) + 100
        # Write the g-code to move to the vertex
        if debug_g:
            f.write(f"G1 F{s1} X{x1} Y{y1} Z{z1} E{e1} (Extrude-{r1} Speed {t2}Percent Distance-{e2}mm)\n")
        else:
            if e1:
                if (z1 == z2):
                    f.write(f"G1 F{s1} X{x1} Y{y1} E{e1}\n")
                else:
                    f.write(f"G1 F{s1} X{x1} Y{y1} Z{z1} E{e1}\n")
            else:
                if (z1 == z2):
                    f.write(f"G0 F{s1} X{x1} Y{y1}\n")
                else:
                    f.write(f"G0 F{s1} X{x1} Y{y1} Z{z1}\n")
                    
        # Shift current vertex into last_vertex vars
        x2 = x1
        y2 = y1
        z2 = z1
    # Write the end gecode to the file and close.
    f.write(""";End GCode
M104 T0 S0
G91 ;Relative positioning
G1 E-2 F2700 ;Retract a bit
G1 E-2 Z0.2 F2400 ;Retract and raise Z
G1 X5 Y5 F3000 ;Wipe out
G1 Z10 ;Raise Z more
G90 ;Absolute positionning
G1 X0 Y600 ;Present print
M106 S0 ;Turn-off fan
M104 S0 ;Turn-off hotend
M140 S0 ;Turn-off bed
M84 X Y E ;Disable all steppers but Z
;End G-Code
""")
f.close()
