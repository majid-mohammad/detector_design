import gdstk
import warnings

def feedline(**kwargs):

    cell = gdstk.Cell(kwargs.get("name", "feedline")) # cell for feedline
    # Feedline parameters
    center_width = kwargs.get("center_width", 8)  # x axis
    gap = kwargs.get("gap", 3) # between center strip and ground planes
    height = kwargs.get("height", 150)  # y axis
    ground2_width = kwargs.get("ground2_width", 1)  # right side of center strip
    bottom_ground_height = kwargs.get("bottom_ground_height", 10)  # bottom right of the center strip
    cavity_height = kwargs.get("cavity_height", 130)  # this is where the resonator lives
    ground1_width = 50 * center_width  # left side of center strip
    top_ground_start = bottom_ground_height + cavity_height  # top right of center strip
    origin = (0, 0)

    # Capacitor parameters
    bar_width = kwargs.get("bar_width", 400)  # this is the length of the bottom bar
    coupling_bar_gap = kwargs.get("coupling_bar_gap", 0.5)
    coupling_bar_width = kwargs.get("coupling_bar_width", 10)
    bar_height = kwargs.get("bar_height", 10)  # sets the height of the three boundry bars to the capacitor

    # Ground Parameters
    ground_width = coupling_bar_gap + coupling_bar_width + bar_width + bar_height + 50

    # ground metal cell definition
    ground1 = gdstk.rectangle(origin, (ground1_width, height))
    center = gdstk.rectangle((ground1_width + gap, 0),
                             (ground1_width + gap + center_width, height))
    ground2 = gdstk.rectangle((ground1_width + 2 * gap + center_width, 0),
                              (ground1_width + 2 * gap + center_width + ground2_width, height))

    bottom_ground = gdstk.rectangle((ground1_width + 2 * gap + center_width + ground2_width, 0),
                                    (ground1_width + 2 * gap + center_width + ground2_width + ground_width,
                                     bottom_ground_height))
    top_ground = gdstk.rectangle((ground1_width + 2 * gap + center_width + ground2_width, top_ground_start),
                                 (ground1_width + 2 * gap + center_width + ground2_width + ground_width, height))

    poly = gdstk.boolean([ground1, ground2], center, 'or')
    cell.add(bottom_ground, top_ground)
    cell.add(*poly)

    return cell


def capacitor(**kwargs):

    cell = gdstk.Cell(kwargs.get("name", "capacitor"))
    # Feedline parameters
    center_width = kwargs.get("center_width", 8)  # x axis
    gap = kwargs.get("gap", 3)
    ground2_width = kwargs.get("ground2_width", 1)  # right side of center strip
    bottom_ground_height = kwargs.get("bottom_ground_height", 10)  # bottom right of the center strip
    cavity_height = kwargs.get("cavity_height", 130)  # this is where the resonator lives
    ground1_width = 50 * center_width  # left side of center strip
    # inductor parameters
    spacing_between_inductor_waveguide = kwargs.get("spacing_between_inductor_waveguide", 7)
    inductor_width = kwargs.get("inductor_width", 2)

    # Capacitor parameters
    finger_pairs = 7
    fingers = 2 * finger_pairs
    finger_gap = kwargs.get("finger_gap", 2)
    finger_width = kwargs.get("finger_width", 2)
    coupling_bar_gap = kwargs.get("coupling_bar_gap", 0.5)
    coupling_bar_width = kwargs.get("coupling_bar_width", 10)
    left_bar_width = kwargs.get("left_bar_width", 41.5)
    bar_gap = kwargs.get("bar_gap", 7)  # gap between
    bar_height = kwargs.get("bar_height", 10)  # sets the height of the three boundry bars to the capacitor
    bar_width = kwargs.get("bar_width", 400)  # this is the length of the bottom bar
    coupling_bar_height_max = cavity_height - 2 * coupling_bar_gap  # sets the height of the coupling bar within the cavity in the feedline
    coupling_bar_height = kwargs.get('coupling_bar_height',0)
    right_bar_width = bar_width - left_bar_width - bar_gap

    #### capacitor geometry ####
    # this is the coupling bar at the origin
    coupling_bar = gdstk.rectangle((ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap,
                                    bottom_ground_height + coupling_bar_gap + coupling_bar_height_max),
                                   (
                                       ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width,
                                       bottom_ground_height + coupling_bar_gap + coupling_bar_height))
    cell.add(coupling_bar)

    # this is the left bar that forms the partial boundry of the interdigited capacitor
    path = gdstk.FlexPath(
        (ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width,
         bottom_ground_height + coupling_bar_gap + coupling_bar_height_max / 2 - bar_height / 2), bar_height)
    path = path.horizontal(
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width,
        bar_height)
    cell.add(path)

    # #right capacitor bar
    path = gdstk.FlexPath((
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + bar_gap,
        bottom_ground_height + coupling_bar_gap + coupling_bar_height_max / 2 - bar_height / 2),
        bar_height)
    path = path.horizontal(
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + bar_gap + right_bar_width + bar_height / 2,
        bar_height)
    path = path.vertical(
        bottom_ground_height + coupling_bar_gap + coupling_bar_height_max / 2 + fingers * (finger_gap + finger_width))
    cell.add(path)

    # these rectangles are used to transition into the inductor
    patch1 = gdstk.rectangle((
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width,
        bottom_ground_height + coupling_bar_gap + coupling_bar_height_max / 2 - bar_height),
        (
            ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width - bar_height,
            bottom_ground_height + coupling_bar_gap + coupling_bar_height_max / 2 - bar_height - spacing_between_inductor_waveguide - inductor_width))

    patch2 = gdstk.rectangle((
        ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + bar_gap,
        bottom_ground_height + coupling_bar_gap + coupling_bar_height_max / 2 - bar_height),
        (
            ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + left_bar_width + bar_gap + bar_height,
            bottom_ground_height + coupling_bar_gap + coupling_bar_height_max / 2 - bar_height - spacing_between_inductor_waveguide - inductor_width))
    cell.add(patch1)
    cell.add(patch2)

    # Define capacitor fingers
    used_fill = 0
    total_fill = (bar_width - finger_gap) * finger_pairs # sets the fill we want the sum of our fingers to have
    fill = kwargs.get('fill', total_fill)

    # shrink = kwargs.get("shrink", None)  # overrides fill

    base_fill = (bar_width/2 + bar_width/6) # minimum fill we want our individual finger
    max_fill = (bar_width - finger_gap) # max fill of an individual finger

    # if shrink is not None:
    #     fill = max_fill * finger_pairs - shrink
    # if fill > max_fill * finger_pairs:
    #     if shrink is None:
    #         message = ("The 'fill' parameter is larger than the maximum value "
    #                    "possible for the current geometry: "
    #                    f"{max_fill * finger_pairs:g}.")
    #     else:
    #         message = "The 'shrink' parameter should be positive."
    #     warnings.warn(message, RuntimeWarning)
    # if fill < 0 and shrink is not None:
    #     if shrink is not None:
    #         message = ("The 'shrink' parameter is larger than the maximum "
    #                    "value possible for the current geometry: "
    #                    f"{max_fill * finger_pairs:g}.")
    #     else:
    #         message = "The 'fill' parameter should be positive."
    #     warnings.warn(message, RuntimeWarning)

    direction = -1
    position = bottom_ground_height + coupling_bar_gap + coupling_bar_height_max/2 + finger_gap
    finger_space = finger_width
    fingerss = []
    for _ in range(finger_pairs):
        added_fill = min(max_fill, fill - used_fill)
        if added_fill < base_fill:
            added_fill = base_fill
        used_fill += added_fill
        for i in range(2):
            direction *= -1
            start = ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width \
                if i % 2 == 0 else ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + bar_width
            stop = start + direction * added_fill if i % 2 == 0 \
                else ground1_width + gap + center_width + gap + ground2_width + coupling_bar_gap + coupling_bar_width + bar_width + direction * added_fill
            fingerss.append(gdstk.rectangle(
                (start, position), (stop - finger_space, position + finger_width)))
            position += (finger_gap + finger_width)
            finger_space *= -1

    cell.add(*fingerss)

    return cell

def inductor(**kwargs):

    cell = gdstk.Cell(kwargs.get("name", "inductor"))
    # Feedline parameters
    center_width = kwargs.get("center_width", 8)  # x axis
    gap = kwargs.get("gap", 3)
    ground2_width = kwargs.get("ground2_width", 1)  # right side of center strip
    bottom_ground_height = kwargs.get("bottom_ground_height", 10)  # bottom right of the center strip
    cavity_height = kwargs.get("cavity_height", 130)  # this is where the resonator lives
    ground1_width = 50 * center_width  # left side of center strip
    # inductor parameters
    spacing_between_inductor_waveguide = kwargs.get("spacing_between_inductor_waveguide", 7)
    inductor_width = kwargs.get("inductor_width", 2)
    inductor_overlap = kwargs.get("inductor_overlap", 6)  # overlap of the non photosensitive and photosensitve inductor material
    inductor_length = kwargs.get("inductor_length", 250)  # coupling length
    # Capacitor parameters
    coupling_bar_gap = kwargs.get("coupling_bar_gap", 0.5)
    coupling_bar_width = kwargs.get("coupling_bar_width", 10)
    left_bar_width = kwargs.get("left_bar_width", 41.5)
    bar_gap = kwargs.get("bar_gap", 7)  # gap between
    bar_height = kwargs.get("bar_height", 10)  # sets the height of the three boundry bars to the capacitor
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

def resonator(**kwargs):
    cell = gdstk.Cell(kwargs.get("name", "resonator"))
    induct = inductor(**kwargs)
    capac = capacitor(**kwargs)
    cell.add(gdstk.Reference(induct))
    cell.add(gdstk.Reference(capac))
    cell.flatten()
    return cell

def geometry(**kwargs):
    cell = gdstk.Cell(kwargs.get('name', 'geometry'))
    induct = inductor(**kwargs)
    capac = capacitor(**kwargs)
    fl = feedline(**kwargs)
    cell.add(gdstk.Reference(induct))
    cell.add(gdstk.Reference(capac))
    cell.add(gdstk.Reference(fl))
    cell.flatten()
    return cell


if __name__ == '__main__':

    library = gdstk.Library()
    cap_low_freq = dict(coupling_bar_height=54.5)
    cap_high_freq = dict(fill=0, coupling_bar_height=0)
    library.add(feedline())
    library.add(capacitor(**cap_high_freq))
    library.add(inductor())
    library.add(resonator(**cap_high_freq))
    library.add(geometry(**cap_high_freq))
    library.write_gds('/Users/majidmohammad/Desktop/Grad School/Python/test_gds/resonator.gds')
