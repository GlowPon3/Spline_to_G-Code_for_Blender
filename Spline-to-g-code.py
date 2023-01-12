import bpy
import math

class GOperator(bpy.types.Operator):
    
    bl_idname = "gcode.operator"
    bl_label = "Generate G Code"
    
    def invoke(self, context, event):
        self.curve_object= bpy.data.objects['BezierCurve']
        self.e_m= round(context.scene.gi_extrusion, context.scene.gi_quality)
        self.d= round(context.scene.gi_quality)
        self.f_r= round(context.scene.gi_speed)
        self.debug_g= context.scene.gi_debug
        self.f_e= round(context.scene.gi_xextrusion, context.scene.gi_quality)
        self.g_file= context.scene.gi_file
        self.temp_b= round(context.scene.gi_bed)
        self.temp_e= round(context.scene.gi_e1)
        return self.execute(context)
    
    def execute(self, context):
        # Open g-code file for output
        with open(self.g_file, 'w') as f:
            # write the start gcode to the file
            f.write(f""";start g-code
M221 T0 S100.00
M140 S{self.temp_b}
M190 S{self.temp_b}
M104 T0 S{self.temp_e}
M109 T0 S{self.temp_e}
T0
G28 ;Home
G92 E0 ;Reset Extruder
G1 Z2.0 F3000 ;Move Z Axis up
G90 ;Set absolute position mode
M83 ;Set extruder to relative mode
;start g-code
;Begin drawing spline by drawing to the first point
""")
            #set the last_vertex vars to the object's location
            x2 = round(self.curve_object.location.x, self.d)
            y2 = round(self.curve_object.location.y, self.d)
            z2 = round(self.curve_object.location.z, self.d)
            # Iterate over the vertices of the mesh rounding where needed
            for point in self.curve_object.data.splines.active.bezier_points:
                x1 = round(point.co.x, self.d)
                y1 = round(point.co.y, self.d)
                z1 = round(point.co.z, self.d)
                w1 = round(point.weight_softbody, self.d) * self.f_e # let weight add a percentage of f_e to the extrusion when approaching this point even with no motion
                r1 = round(point.radius, self.d) # let radius control the amount of extrustion when approcaching this point
                t1 = round(point.tilt, self.d) # let tilt control the speed the nozzle's movement when approching this point
                s1 = round(((t1 / (math.pi * 2))*self.f_r) + self.f_r) # Let the tilt add a multiple of the feedrate back to the feedrate
                # multiply the flow by the distance travelled since last_vertex and by the radius and add the forced extrusion
                e1 = round((math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) * self.e_m * r1), self.d) + w1
                # get the same result of the above for debugging without the radius or weight multipliers involved.
                e2 = round((math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2) * self.e_m ), self.d)
                t2 = round(((t1 / 2) / math.pi) * 100) + 100
                # Write the g-code to move to the vertex
                if (self.debug_g):
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
            f.write(f""";End GCode
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
;End G-Code""")
            if (self.debug_g):
                f.write(f"""
;Debug info
;        {self.curve_object} = bpy.data.objects['BezierCurve'] # Get a reference to the curve object
;        {self.e_m} = 0.1 # Set the extrusion multiplier (mm3 per cm idk)
;        {self.d} = 4 # Set the signifigance value (Default 3 decimal places)
;        {self.f_r} = 1200 # Set the feedrate (Print speed)
;        {self.debug_g} = debug toggle
;        {self.f_e} = 1 # Set f_e as the maximum amount of extrusion that can be added per point.
;        {self.g_file} =  # Set filename and location
;        {self.temp_b} = 55.00 # Bed temperature in C
;        {self.temp_e} = 215.00 # Extruder temperature in C
;end debug""")
            f.close()
        
        
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(GOperator.bl_idname, text="Generate G")


class GPanel(bpy.types.Panel):
    
    bl_label = "GPanel"
    bl_idname = "OBJECT_PT_gpanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gcode'

    def draw(self, context):
        layout = self.layout
        scene = context.scene


        row = layout.row()
        row.prop(scene, "gi_debug")
        # create a text input box linked to the variable 'my_string'
        row = layout.row()
        row.prop(scene, "gi_file")
        # create a text input box linked to the variable 'my_float'
        row = layout.row()
        row.prop(scene, "gi_quality")
        # create a text input box linked to the variable 'my_int'
        row = layout.row()
        row.prop(scene, "gi_extrusion")
        # create a text input box linked to the variable 'my_bool'
        row = layout.row()
        row.prop(scene, "gi_speed")
        # create a text input box linked to the variable 'my_bool'
        row = layout.row()
        row.prop(scene, "gi_xextrusion")
        # create a text input box linked to the variable 'my_bool'
        row = layout.row()
        row.prop(scene, "gi_bed")
        # create a text input box linked to the variable 'my_bool'
        row = layout.row()
        row.prop(scene, "gi_e1")

def register():
    bpy.utils.register_class(GPanel)
    bpy.types.Scene.gi_debug = bpy.props.BoolProperty(name="Debug") # add a debug toggle
    bpy.types.Scene.gi_file = bpy.props.StringProperty(name="File", default="C:/Directory/goes/here/spline.gcode") # set filename and location
    bpy.types.Scene.gi_quality = bpy.props.IntProperty(name="Significance", default=3) # set the amount of decimal places to work with
    bpy.types.Scene.gi_extrusion = bpy.props.FloatProperty(name="Extrusion per cm", default=0.1) # set the extrusion amount per cm
    bpy.types.Scene.gi_speed = bpy.props.IntProperty(name="Feedrate", default=1200) # set the base speed
    bpy.types.Scene.gi_xextrusion = bpy.props.FloatProperty(name="Max Extrusion per point", default=1) # set the maximum extrusion that can be manually added per point
    bpy.types.Scene.gi_bed = bpy.props.IntProperty(name="Bed Temp (C)", default=55) # set the bed temperature
    bpy.types.Scene.gi_e1 = bpy.props.IntProperty(name="Nozzle Temp (C)", default=215) # set the nozzle temperature
    bpy.utils.register_class(GOperator)
    bpy.types.OBJECT_PT_gpanel.append(menu_func)


def unregister():
    bpy.utils.unregister_class(GPanel)
    del bpy.types.Scene.gi_debug
    del bpy.types.Scene.gi_file
    del bpy.types.Scene.gi_quality
    del bpy.types.Scene.gi_extrusion
    del bpy.types.Scene.gi_speed
    del bpy.types.Scene.gi_xextrusion
    del bpy.types.Scene.gi_bed
    del bpy.types.Scene.gi_e1

if __name__ == "__main__":
    register()
