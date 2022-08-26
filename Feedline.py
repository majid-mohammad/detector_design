import gdstk
import pathlib
import numpy as np


def feedline(**kwargs):

    cell = gdstk.Cell(kwargs.get("name", "feedline"))
    # Feedline parameters
    center_width = kwargs.get("center_width", 8)  # x axis
    gap = kwargs.get("gap", 3)
    height = kwargs.get("height", 200)  # y axis
    ground2_width = kwargs.get("ground2_width", 0.5)  # right side of center strip
    bottom_ground_height = kwargs.get("bottom_ground_height", 24)  # bottom right of the center strip
    cavity_height = kwargs.get("cavity_height", 115)  # this is where the resonator lives
    ground1_width = 50 * center_width  # left side of center strip
    top_ground_height = bottom_ground_height + cavity_height  # top right of center strip
    origin = (0, 0)
    # inductor parameters
    inductor_length = kwargs.get("inductor_length", 900)  # coupling length
    # Capacitor parameters
    coupling_bar_gap = kwargs.get("coupling_bar_gap", 0.5)
    coupling_bar_width = kwargs.get("coupling_bar_width", 10)
    left_bar_width = kwargs.get("left_bar_width", 41.5)
    # Ground Parameters
    bottom_ground_width = coupling_bar_gap + coupling_bar_width + left_bar_width + inductor_length + 150
    top_ground_width = bottom_ground_width

    ground1 = gdstk.rectangle(origin, (ground1_width, height))
    center = gdstk.rectangle((ground1_width + gap, 0),
                             (ground1_width + gap + center_width, height))
    ground2 = gdstk.rectangle((ground1_width + 2 * gap + center_width, 0),
                              (ground1_width + 2 * gap + center_width + ground2_width, height))

    bottom_ground = gdstk.rectangle((ground1_width + 2 * gap + center_width + ground2_width, 0),
                                    (ground1_width + 2 * gap + center_width + ground2_width + bottom_ground_width,
                                     bottom_ground_height))
    top_ground = gdstk.rectangle((ground1_width + 2 * gap + center_width + ground2_width, top_ground_height),
                                 (ground1_width + 2 * gap + center_width + ground2_width + top_ground_width, height))

    poly = gdstk.boolean([ground1, ground2], center, 'or')
    cell.add(bottom_ground, top_ground)
    cell.add(*poly)

    return cell


def capacitor(**kwargs):

    cell = gdstk.Cell(kwargs.get("name", "capacitor"))
    # Feedline parameters
    center_width = kwargs.get("center_width", 8)  # x axis
    gap = kwargs.get("gap", 3)
    ground2_width = kwargs.get("ground2_width", 0.5)  # right side of center strip
    bottom_ground_height = kwargs.get("bottom_ground_height", 24)  # bottom right of the center strip
    cavity_height = kwargs.get("cavity_height", 115)  # this is where the resonator lives
    ground1_width = 50 * center_width  # left side of center strip
    # inductor parameters
    spacing_between_inductor_waveguide = kwargs.get("spacing_between_inductor_waveguide", 7)
    inductor_width = kwargs.get("inductor_width", 2)
    # Capacitor parameters
    fingers = kwargs.get("fingers", 6)
    finger_gap = kwargs.get("finger_gap", 3)
    finger_width = kwargs.get("finger_width", 1)
    coupling_bar_gap = kwargs.get("coupling_bar_gap", 0.5)
    coupling_bar_width = kwargs.get("coupling_bar_width", 10)
    left_bar_width = kwargs.get("left_bar_width", 41.5)
    bar_gap = kwargs.get("bar_gap", 7)  # gap between
    bar_height = kwargs.get("bar_height", 10)  # sets the height of the three boundry bars to the capacitor
    bar_width = kwargs.get("bar_width", 325)  # this is the length of the bottom bar
    coupling_bar_height = cavity_height - 3 * coupling_bar_gap  # sets the height of the coupling bar within the cavity in the feedline
    right_bar_width = bar_width - left_bar_width - bar_gap


    #### capacitor geometry ####

    # this is the coupling bar at the origin
    coupling_bar = gdstk.rectangle((ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap,
                                    bottom_ground_height + coupling_bar_gap),
                                   (
                                       ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width,
                                       bottom_ground_height + coupling_bar_gap + coupling_bar_height))
    cell.add(coupling_bar)

    # this is the left bar that forms the partial boundry of the interdigited capacitor
    path = gdstk.FlexPath(
        (ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width,
         bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height / 2), bar_height)
    path = path.horizontal(
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width,
        bar_height)
    cell.add(path)

    # #right capacitor bar
    path = gdstk.FlexPath((
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + bar_gap,
        bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height / 2),
        bar_height)
    path = path.horizontal(
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + bar_gap + right_bar_width + bar_height / 2,
        bar_height)
    path = path.vertical(
        bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 + fingers * (finger_gap + finger_width))
    cell.add(path)

    # these rectangles are used to transition into the inductor
    patch1 = gdstk.rectangle((
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width,
        bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height),
        (
            ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width - bar_height,
            bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height - spacing_between_inductor_waveguide - inductor_width))

    patch2 = gdstk.rectangle((
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + bar_gap,
        bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height),
        (
            ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + bar_gap + bar_height,
            bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height - spacing_between_inductor_waveguide - inductor_width))
    cell.add(patch1)
    cell.add(patch2)

    ####Fingers###
    for fing in range(fingers):
        f = gdstk.rectangle((
            ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + 0 if fing % 2 == 0
            else ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + bar_width,
            bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 + finger_gap + fing * (
                    finger_width + finger_gap)),
            (
                ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + bar_width - finger_gap if fing % 2 == 0
                else ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + finger_gap,
                bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 + finger_gap + fing * finger_gap + (
                        fing + 1) * finger_width))
        cell.add(f)

    cell.flatten()

    return cell

def inductor(**kwargs):

    cell = gdstk.Cell(kwargs.get("name", "inductor"))
    # Feedline parameters
    center_width = kwargs.get("center_width", 8)  # x axis
    gap = kwargs.get("gap", 3)
    ground2_width = kwargs.get("ground2_width", 0.5)  # right side of center strip
    bottom_ground_height = kwargs.get("bottom_ground_height", 24)  # bottom right of the center strip
    cavity_height = kwargs.get("cavity_height", 115)  # this is where the resonator lives
    ground1_width = 50 * center_width  # left side of center strip
    # inductor parameters
    spacing_between_inductor_waveguide = kwargs.get("spacing_between_inductor_waveguide", 7)
    inductor_width = kwargs.get("inductor_width", 2)
    inductor_overlap = kwargs.get("inductor_overlap",
                                  6)  # overlap of the non photosensitive and photosensitve inductor material
    inductor_length = kwargs.get("inductor_length", 900)  # coupling length
    # Capacitor parameters
    coupling_bar_gap = kwargs.get("coupling_bar_gap", 0.5)
    coupling_bar_width = kwargs.get("coupling_bar_width", 10)
    left_bar_width = kwargs.get("left_bar_width", 41.5)
    bar_gap = kwargs.get("bar_gap", 7)  # gap between
    bar_height = kwargs.get("bar_height", 10)  # sets the height of the three boundry bars to the capacitor
    bar_width = kwargs.get("bar_width", 325)  # this is the length of the bottom bar
    coupling_bar_height = cavity_height - 3 * coupling_bar_gap  # sets the height of the coupling bar within the cavity in the feedline

    #### inductor geometry ####

    overlapped_inductor = gdstk.rectangle((
                                          ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width,
                                          bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height - spacing_between_inductor_waveguide - inductor_width + inductor_overlap),
                                          (
                                          ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width - bar_height,
                                          bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height - 2 * spacing_between_inductor_waveguide - 2 * inductor_width))
    cell.add(overlapped_inductor)

    # The inductor_width/2 is to offset the central position of the width of the flex path
    path = gdstk.FlexPath((
                          ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width,
                          bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height - 2 * spacing_between_inductor_waveguide - 2 * inductor_width + inductor_width / 2),
                          inductor_width)
    path = path.horizontal(
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + inductor_length - bar_height - inductor_width / 2,
        inductor_width)
    path = path.vertical(
        bottom_ground_height + coupling_bar_gap + coupling_bar_height / 2 - bar_height - spacing_between_inductor_waveguide - inductor_width + inductor_width / 2,
        inductor_width)
    path = path.horizontal(
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + bar_gap,
        inductor_width)
    cell.add(path)


    return cell




if __name__ == '__main__':



    library = gdstk.Library()

    feed = dict(center_width = 8, gap = 3, height = 200,ground2_width = 0.5,bottom_ground_height = 24,cavity_height = 115)
    cap = dict(fingers = 10,finger_gap = 3,finger_width = 1, coupling_bar_gap = 0.5,coupling_bar_width = 10,bar_height = 10,bar_width = 325,left_bar_width = 41.5,bar_gap = 7)
    ind = dict(spacing_between_inductor_waveguide = 7,inductor_width = 2,inductor_overlap = 7,inductor_length = 900)
    library.add(feedline(**feed))
    library.add(capacitor(**cap))
    library.add(inductor(**ind))
    library.write_gds('/Users/majidmohammad/Desktop/Grad School/Python/test_gds/Feedline.gds')