import re

# function to translate the movement commands
def translate_gcode(gcode_file, x_value, y_value, z_value):
    # read the gcode file
    with open(gcode_file, 'r') as f:
        gcode = f.read()

    # translate the x, y, and z values
    gcode = re.sub(r'(?i)X(-?\d+(\.\d+)?)', lambda m: 'X' + str(float(m.group(1)) + x_value), gcode)
    gcode = re.sub(r'(?i)Y(-?\d+(\.\d+)?)', lambda m: 'Y' + str(float(m.group(1)) + y_value), gcode)
    gcode = re.sub(r'(?i)Z(-?\d+(\.\d+)?)', lambda m: 'Z' + str(float(m.group(1)) + z_value), gcode)

    # write the modified gcode to a new file
    with open(gcode_file[:-6] + '_translated.gcode', 'w') as f:
        f.write(gcode)

# example usage
translate_gcode('example.gcode', 0.5, -0.5, 0.2)
