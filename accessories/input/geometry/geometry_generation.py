# import required modules
import gmsh
import sys
import numpy as np
import matplotlib.pyplot as plt

# predefine some functions
def surface_function(x_0, length, a, lambd, phi, delta_x):
    """
    Function to define the surface of the critical part of the geometry.

    x_0: initial x value (m)
    length: length of the central part (m)
    a: amplitude of the sine wave (m)
    lambd: wavelength of the sine wave (m)
    phi: phase shift of the sine wave (rad)
    delta_x: spacing between points along the x-axis (m)
    """

    x = np.arange(0, length, delta_x)
    y = a * np.sin(2*np.pi/lambd * x + 2*np.pi*phi)
    x = x + x_0  # shift x values to start from x_0

    return x, y

# set parameters
# set general geometry parameters
x_upstream_min = 0
length_upstream = 2.5
length_center = 1
length_downstream = 2.5
y_base = 0
height_channel = 2
# surface function parameters
x_0 = x_upstream_max
a = 0.1
lambd = 0.5
phi = 0
delta_x = 0.01

# generate surface points in central part of geometry
surface_center = np.array(surface_function(x_0, x_0 + length, a, lambd, phi, delta_x))

breakpoint = 1

# initialize gmsh
gmsh.initialize()



# cube points:
lc = 1e-2
point1 = gmsh.model.geo.add_point(0, 0, 0, lc)
point2 = gmsh.model.geo.add_point(1, 0, 0, lc)
point3 = gmsh.model.geo.add_point(1, 1, 0, lc)
point4 = gmsh.model.geo.add_point(0, 1, 0, lc)
point5 = gmsh.model.geo.add_point(0, 1, 1, lc)
point6 = gmsh.model.geo.add_point(0, 0, 1, lc)
point7 = gmsh.model.geo.add_point(1, 0, 1, lc)
point8 = gmsh.model.geo.add_point(1, 1, 1, lc)

# Edge of cube:
line1 = gmsh.model.geo.add_line(point1, point2)
line2 = gmsh.model.geo.add_line(point2, point3)
line3 = gmsh.model.geo.add_line(point3, point4)
line4 = gmsh.model.geo.add_line(point4, point1)
line5 = gmsh.model.geo.add_line(point5, point6)
line6 = gmsh.model.geo.add_line(point6, point7)
line7 = gmsh.model.geo.add_line(point7, point8)
line8 = gmsh.model.geo.add_line(point8, point5)
line9 = gmsh.model.geo.add_line(point4, point5)
line10 = gmsh.model.geo.add_line(point6, point1)
line11 = gmsh.model.geo.add_line(point7, point2)
line12 = gmsh.model.geo.add_line(point3, point8)

# faces of cube:
face1 = gmsh.model.geo.add_curve_loop([line1, line2, line3, line4])
face2 = gmsh.model.geo.add_curve_loop([line5, line6, line7, line8])
face3 = gmsh.model.geo.add_curve_loop([line9, line5, line10, -line4])
face4 = gmsh.model.geo.add_curve_loop([line9, -line8, -line12, line3])
face5 = gmsh.model.geo.add_curve_loop([line6, line11, -line1, -line10])
face6 = gmsh.model.geo.add_curve_loop([line11, line2, line12, -line7])

# surfaces of cube:
gmsh.model.geo.add_plane_surface([face1])
gmsh.model.geo.add_plane_surface([face3])
gmsh.model.geo.add_plane_surface([face4])
gmsh.model.geo.add_plane_surface([face5, face6])

# Create the relevant Gmsh data structures 
# from Gmsh model.
gmsh.model.geo.synchronize()

# Generate mesh:
gmsh.model.mesh.generate()

# Write mesh data:
gmsh.write("GFG.msh")

# Creates  graphical user interface
if 'close' not in sys.argv:
    gmsh.fltk.run()

# It finalize the Gmsh API
gmsh.finalize()


# final output to verify that script completed successfully
print("script successfully run")