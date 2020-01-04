#!/usr/bin/env python3

import logging
import numpy as np # matmul

from solid import *
from math import pi, sin, cos
from pprint import pprint

logger = logging.getLogger(__name__)

logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.DEBUG)


def deg2rad(degrees):
    return (degrees / 180) * pi

def rad2deg(rad):
    return (rad * 180) / pi

# shape parameters
nrows = 5
ncols = 6
alpha = pi / 12         # curvature of the columns
beta = pi / 36          # curvature of the rows
centerrow = nrows - 3   # controls front-back tilt
# controls left-right tilt / tenting (higher number is more tenting)
centercol = 2
tenting_angle = pi / 12  # or, change this for more precise tenting control
# options include :standard, :orthographic, and :fixed
column_styles = ["orthographic", "standard", "fixed"]
if nrows > 5:
    column_style = "orthographic"
else:
    column_style = "standard"
#column_style = "fixed"


def column_offset(column):
    if column == 2:
        return [0, 2.82, -4.5]
    elif column >= 4:
        return [0, -12, 5.64]
    else:
        return [0, 0, 0]


thumb_offsets = [6, -3, 7]
# controls overall height; original=9 with centercol=3; use 16 for centercol=2
keyboard_z_offset = 19
extra_width = 2.5       # extra space between the base of keys; original= 2
extra_height = 1.0      # original= 0.5

# length of the first downward-sloping part of the wall (negative)
wall_z_offset = -5
# offset in the x and/or y direction for the first downward-sloping part
# of the wall (negative)
wall_xy_offset = 5
wall_thickness = 2      # wall thickness parameter; originally 5

# General variables
lastrow = nrows -1
cornerrow = lastrow-1
lastcol = ncols-1

# Switch hole
keyswitch_width = 14.4
keyswitch_height = 14.4

sa_profile_key_height = 12.7

plate_thickness = 4
mount_width = keyswitch_width + 3
mount_height = keyswitch_height + 3
logger.debug('mount_width: %f', mount_width)
logger.debug('mount_height: %f', mount_height)


def single_plate():
    top_wall = translate([0,
                          (1.5 / 2) + (keyswitch_height / 2),
                          plate_thickness / 2])(cube([keyswitch_width + 3,
                                                      1.5,
                                                      plate_thickness],
                                                     True))
    left_wall = translate([(1.5 / 2) + (keyswitch_width / 2),
                           0,
                           plate_thickness / 2])(cube([1.5,
                                                       keyswitch_height + 3,
                                                       plate_thickness],
                                                      True))
    # side_nub

    plate_half = top_wall + left_wall
    return mirror([1, 0, 0])(plate_half) + mirror([0, 1, 0])(plate_half)


def sa_cap(cap_type):
    sa_length = 18.25
    sa_double_length = 37.5

    if cap_type == 1:
        #
        bl2 = 18.5 / 2
        keycap_01 = translate([0, 0, 0.05])(
            linear_extrude(height=0.1, twist=0, convexity=0)(
                polygon([[bl2, bl2], [bl2, (- bl2)],
                         [(- bl2), (- bl2)], [(- bl2), bl2]])
            )
        )
        m = 17 / 2
        keycap_02 = translate([0, 0, 6])(
            linear_extrude(height=0.1, twist=0, convexity=0)(
                polygon([[m, m], [m, (- m)], [(- m), (- m)], [(- m), m]])
            )
        )

        m = 6
        keycap_03 = translate([0, 0, 12])(
            linear_extrude(height=0.1, twist=0, convexity=0)(
                polygon([[m, m], [m, (- m)],
                         [(- m), (- m)], [(- m), m]])
            )
        )
        keycap = color([220 / 255, 163 / 255, 163 / 255, 1])(
            translate([0, 0, (5 + plate_thickness)])(
                hull()([keycap_01, keycap_02, keycap_03])
            )
        )
    elif cap_type == 2:
        #
        bl2 = sa_double_length / 2
        bw2 = 18.25 / 2
        keycap_01 = translate([0, 0, 0.05])(
            linear_extrude(height=0.1, twist=0, convexity=0)(
                polygon([[bw2, bl2], [bw2, (- bl2)],
                         [(- bw2), (- bl2)], [(- bw2), bl2]])
            )
        )
        keycap_02 = translate([0, 0, 12])(
            linear_extrude(height=0.1, twist=0, convexity=0)(
                polygon([[6, 16], [6, -16], [-6, -16], [-6, 16]])
            )
        )
        keycap = color([127 / 255, 159 / 255, 127 / 255, 1])(
            translate([0, 0, (5 + plate_thickness)])(
                hull()([keycap_01, keycap_02])
            )
        )
    elif cap_type == 1.5:
        #
        bl2 = 18.25 / 2
        bw2 = 28 / 2
        keycap_01 = translate([0, 0, 0.05])(
            linear_extrude(height=0.1, twist=0, convexity=0)(
                polygon([[bw2, bl2], [bw2, (- bl2)],
                         [(- bw2), (- bl2)], [(- bw2), bl2]])
            )
        )
        keycap_02 = translate([0, 0, 12])(
            linear_extrude(height=0.1, twist=0, convexity=0)(
                polygon([[11, 6], [-11, 6], [-11, -6], [11, -6]])
            )
        )
        keycap = color([240 / 255, 223 / 255, 175 / 255, 1])(
            translate([0, 0, (5 + plate_thickness)])(
                hull()([keycap_01, keycap_02])
            )
        )
    else:
        logging.exception.ValueError('Wrong cap type')

    return keycap
    # return keycap


# Placement functions
columns = list(range(ncols))
rows = list(range(nrows))

cap_top_height = plate_thickness + sa_profile_key_height
row_radius = (((mount_height + extra_height) / 2) /
              (sin(alpha / 2))) + cap_top_height
column_radius = (((mount_width + extra_width) / 2) /
                 (sin(beta / 2))) + cap_top_height
column_x_delta = -1 - column_radius * sin(beta)
column_base_angle = (centercol - 2) * beta
logger.debug('row_radius: %f', row_radius)
logger.debug('column_radius: %f', column_radius)
logger.debug('column_x_delta: %f', column_x_delta)
logger.debug('column_base_angle: %f', column_base_angle)


def apply_key_geometry(
        translate_fn,
        rotate_x_fn, rotate_y_fn,
        column, row,
        shape):
    
    #print(column, row)
    column_angle = (centercol - column) * beta
    if column_style == "orthographic":
        #print('ortho')
        column_z_delta = (1 - cos(column_angle)) * column_radius              
        placed_shape = translate_fn(column_offset(column))(
            translate_fn([-(column - centercol) * column_x_delta, 0, column_z_delta])(
                rotate_y_fn(column_angle)(
                    translate_fn([0, 0, row_radius])(
                        rotate_x_fn(alpha * (centerrow - row))(
                            translate_fn([0, 0, (-row_radius)])(shape)
                            )
                        )
                    )
                )
            )                   
    elif column_style == "fixed":
        #print('fixed')
        logging.exception.BaseException('Not implemented')
    elif column_style == "standard":
        #print('standard')
        placed_shape = translate_fn(column_offset(column))(
            translate_fn([0, 0, column_radius])(
                rotate_y_fn(column_angle)(
                    translate_fn([0, 0, (- column_radius)])(
                        translate_fn([0, 0, row_radius])(
                            rotate_x_fn((centerrow - row) * alpha)(
                                translate_fn([0, 0, -row_radius])(shape)
                                )
                            )
                        )
                    )
                )
            )
    else:
        raise ValueError(column_style)

    return rotate_y_fn(tenting_angle)(
        translate_fn([0, 0, keyboard_z_offset])(placed_shape)
    )


def key_place(column, row, shape):
    def func1(angle):
        return rotate(rad2deg(angle), [1, 0, 0])

    def func2(angle):
        return rotate(rad2deg(angle), [0, 1, 0])
    return apply_key_geometry(translate, func1, func2, column, row, shape)


def rotate_around_x(angle, position):
    ret = np.matmul(
            np.array(position),
            np.array([[1,          0, 0],
                      [0, cos(angle), -sin(angle)],
                      [0, sin(angle), cos(angle)]])
        )
    return ret

def rotate_around_y(angle, position):
    ret = np.matmul(
            np.array(position),
            np.array([[ cos(angle), 0, sin(angle)],
                      [ 0,          1, 0         ],
                      [-sin(angle), 0, cos(angle)]])
        )
    return ret

def key_position(column, row, position):
    return apply_key_geometry(sum, rotate_around_x, rotate_around_y, column, row, position)


def key_holes():
    First = True
    for column in columns:
        for row in rows:
            if (column in [2, 3]) or (row != lastrow):
                if First:
                    kholes = key_place(column, row, single_plate())
                    First = False
                else:
                    kholes += key_place(column, row, single_plate())
    return kholes

def caps():
    First = True
    for column in columns:
        for row in rows:
            if (column in [2, 3]) or (row != lastrow):
                if First:
                    kcaps = key_place(column, row, sa_cap(1))
                    First = False
                else:
                    kcaps += key_place(column, row, sa_cap(1))
    return kcaps

# Web connectors
web_thickness = 3.5
post_size = 0.1
web_post = translate([0, 0, plate_thickness-(web_thickness/2)])(cube([post_size, post_size, web_thickness]))

pprint(part()(web_post))

#def triangle_hulls(shapes):
    #return hull()


def main():
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)
    logger.info("START")

    def func1(angle):
        return rotate(angle, [1, 0, 0])

    def func2(angle):
        return rotate(angle, [0, 1, 0])

    #b = apply_key_geometry(translate, func1, func2, 4, 4, single_plate())
    #b = key_place(0, 0, single_plate())
    b = key_holes() + caps()

    scad_render_to_file(b, 'out_file.scad')


if __name__ == "__main__":
    main()
