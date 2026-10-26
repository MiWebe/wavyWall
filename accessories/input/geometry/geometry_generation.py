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
length_center = 6
length_downstream = 2.5
y_base = 0
height_channel = 2
delta_z = 0.01
# derived general geometry parameters
x_upstream_max = x_upstream_min + length_upstream
x_center_min = x_upstream_max
x_center_max = x_center_min + length_center
x_downstream_min = x_center_max
x_downstream_max = x_downstream_min + length_downstream
# surface function parameters
x_0 = x_center_min
length = length_center
a = 0.1
lambd = 0.5
phi = 0
delta_x = 0.01
# mesh parameters
lc_bottom = 0.01
lc_bulk = 0.1
extrusion_depth = 0.1
num_layers = 1
recombine = True  # Optional: tries to make structured prism/hex elements if possible
# script execution parameters
plot_bottom_control = False
plot_full_control = False



### ----- generate geometry coordinates ----- ###

### bottom surface ###
# generate surface points in central part of geometry
surface_center = np.array(surface_function(x_0, length, a, lambd, phi, delta_x))

# make coordinate array for bottom surface of geometry
bottom_coordinates = np.array([[x_upstream_min, y_base], [x_upstream_max, y_base]])

bottom_coordinates = np.append(bottom_coordinates, surface_center.T[1:, :], axis=0)
bottom_coordinates = np.append(bottom_coordinates, [[x_downstream_min, y_base], [x_downstream_max, y_base]], axis=0)

# plot the geometry to verify that it is correct
if plot_bottom_control == True:
    plt.plot(bottom_coordinates.T[0, :], bottom_coordinates.T[1, :], linestyle='--', linewidth=0.6, marker='+', markersize=4)
    plt.xlim(x_upstream_min - 0.5, x_downstream_max + 0.5)
    plt.ylim(y_base - a - 0.5, y_base + a + 0.5)
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.title('Bottom surface of geometry')
    plt.show()

### inlet ###
inlet_coordinates = np.array([[x_upstream_min, y_base], [x_upstream_min, y_base + height_channel]])

### outlet ###
outlet_coordinates = np.array([[x_downstream_max, y_base], [x_downstream_max, y_base + height_channel]])

### top surface ###
top_coordinates = np.array([[x_upstream_min, y_base + height_channel], [x_downstream_max, y_base + height_channel]])

### plot the geometry to verify that it is correct ###
if plot_full_control == True:
    # plot bottom
    plt.plot(bottom_coordinates.T[0, :], bottom_coordinates.T[1, :], linestyle='--', linewidth=1, marker='+', markersize=4, label='bottom')
    # plot inlet
    plt.plot(inlet_coordinates.T[0, :], inlet_coordinates.T[1, :], linestyle='--', linewidth=1, marker='+', markersize=4, label='inlet')
    # plot outlet
    plt.plot(outlet_coordinates.T[0, :], outlet_coordinates.T[1, :], linestyle='--', linewidth=1, marker='+', markersize=4, label='outlet')
    # plot top
    plt.plot(top_coordinates.T[0, :], top_coordinates.T[1, :], linestyle='--', linewidth=1, marker='+', markersize=4, label='top')

    # set plot limits and aspect ratio
    plt.xlim(x_upstream_min - 0.5, x_downstream_max + 0.5)
    plt.ylim(y_base - a - 0.5, y_base + height_channel + 0.5)
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    # set labels and title
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.legend()
    plt.title('Bottom surface of geometry')
    plt.show()



### ----- generate geometry in Gmsh ----- ###

### initialize gmsh
gmsh.initialize()

###  make point tags
# bottom surface points
point_tags_bottom = []
for x,y in bottom_coordinates:
    pt = gmsh.model.geo.addPoint(x, y, 0, lc_bottom)
    point_tags_bottom.append(pt)
# inlet points
point_tags_inlet = []
for x,y in inlet_coordinates:
    pt = gmsh.model.geo.addPoint(x, y, 0, lc_bulk)
    point_tags_inlet.append(pt)
# outlet points
point_tags_outlet = []
for x,y in outlet_coordinates:
    pt = gmsh.model.geo.addPoint(x, y, 0, lc_bulk)
    point_tags_outlet.append(pt)
# top surface points
point_tags_top = []
for x,y in top_coordinates:
    pt = gmsh.model.geo.addPoint(x, y, 0, lc_bulk)
    point_tags_top.append(pt)

### make edge tags
# bottom lines
line_bottom = gmsh.model.geo.addBSpline(point_tags_bottom)
# inlet lines
line_inlet = gmsh.model.geo.addLine(point_tags_bottom[0], point_tags_top[0])
# outlet lines
line_outlet = gmsh.model.geo.addLine(point_tags_bottom[-1], point_tags_top[-1])
# top lines
line_top = gmsh.model.geo.addLine(point_tags_top[0], point_tags_top[1])

### create surface
curve_loop = gmsh.model.geo.addCurveLoop([
    line_inlet, 
    line_top, 
    -line_outlet, 
    -line_bottom
])
domain_surface = gmsh.model.geo.addPlaneSurface([curve_loop])

gmsh.model.geo.synchronize()

### extrude 2D surface to 3D volume
extrude_out = gmsh.model.geo.extrude(
    [(2, domain_surface)],
    0, 0, extrusion_depth,
    numElements=[num_layers],
    recombine=recombine
)

gmsh.model.geo.synchronize()

breakpoint = 1

gmsh.fltk.run()

### make face tags
# bottom faces
# inlet faces
# outlet faces
# top faces

### make surface tags
# bottom surfaces
# inlet surfaces
# outlet surfaces
# top surfaces



breakpoint = 1

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