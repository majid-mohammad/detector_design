import os
import logging
import pathlib
from pathlib import Path
import numpy as np
import pysonnet as ps
from Resonator import feedline, capacitor, inductor
import gdstk
import loopfit as lf
import matplotlib.pyplot as plt

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def simulation(name, epsilon=9.3, inductor_kwargs=None, capacitor_kwargs=None,
               feedline_kwargs=None, **kwargs):
    if inductor_kwargs is None:
        inductor_kwargs = {}
    if capacitor_kwargs is None:
        capacitor_kwargs = {}
    if feedline_kwargs is None:
        feedline_kwargs = {}

    dx = kwargs.get('dx', 0.5)  # grid size
    dy = kwargs.get('dy', 0.5)
    f1 = kwargs.get('f1', 4)  # starting and ending freq
    f2 = kwargs.get('f2', 8)
    overwrite = kwargs.get('overwrite', False)
    height = kwargs.get("height", 200)  # pixel height in the y axis
    center_width = kwargs.get("center_width", 8)  # feedline width in x axis
    gap = kwargs.get("gap", 3)  # gap between the ground plane and center strip
    ground1_width = 50 * center_width  # left side of center strip

    feed_geom = feedline(**feedline_kwargs)
    cap_geom = capacitor(**capacitor_kwargs)
    ind_geom = inductor(**inductor_kwargs)
    bbox = feed_geom.bounding_box()  # box around the feedline cells
    box_x = bbox[1][0] - bbox[0][0]
    box_y = bbox[1][1] - bbox[0][1]

    project = ps.GeometryProject()  # creates a project using the GeometryProject function in pysonnet
    project.setup_box(box_x, box_y, box_x / dx, box_y / dy)  # x width, y width, x cells, y cells
    project.set_units(length='um')
    project.set_box_cover("free space", top=True)
    project.set_box_cover("free space", bottom=True)

    # Define the dielectrics.
    project.add_dielectric("air", level=0, thickness=5000, epsilon=1)
    project.add_dielectric("sapphire", level=1, thickness=525, epsilon=epsilon,
                           dielectric_loss=1e-9, conductivity=0)

    # Set up the sweep.
    project.set_options(q_accuracy=True, resonance_detection=True,
                        current_density=True)
    project.add_frequency_sweep("abs", f1=f1, f2=f2)
    project.set_analysis("frequency sweep")
    project['control']['speed'] = 1  # medium memory

    # Define the metal layers.
    project.define_metal("general", "Hf", ls=13, r_dc=0)
    project.define_metal("general", "Nb", ls=0.1, r_dc=0)
    project.define_technology_layer("metal", "inductor", 0, "Hf",
                                    fill_type="diagonal")
    project.define_technology_layer("metal", "capacitor", 0, "Nb",
                                    fill_type="diagonal")
    project.define_technology_layer("metal", "feedline", 0, "Nb",
                                    fill_type="diagonal")

    # Add the geometry
    project.add_gdstk_cell("metal", cap_geom, layer=0, tech_layer="capacitor")
    project.add_gdstk_cell("metal", ind_geom, layer=0, tech_layer="inductor")
    project.add_gdstk_cell("metal", feed_geom, layer=0, tech_layer="feedline")

    # Add ports
    project.add_port("standard", 1, x=ground1_width + gap + center_width / 2, y=0,
                     resistance=50)
    project.add_port("standard", 2, x=ground1_width + gap + center_width / 2, y=height,
                     resistance=50)
    project.add_output_file("touchstone2")

    # Create the file name and raise an error if it's already been simulated.
    directory = pathlib.Path(__file__).parent.absolute()
    simulation_name = directory / f"sonnet/testing/{name}.son"
    output_name = simulation_name.parent / f"{name}.ts"
    log.info(f"Simulating {simulation_name}")
    if os.path.isfile(output_name) and not overwrite:
        raise IOError(f"{output_name} already exists")

    # Create the sonnet file and run.
    project.make_sonnet_file(simulation_name)
    project.run()

    # fit the touchstone file
    folder = pathlib.Path(directory / 'sonnet/testing')
    f, i, q = lf.load_touchstone(folder / f"{name}.ts")  # grab file from folder
    guess = lf.guess(f, i, q, phase0=0, phase1=0)
    result = lf.fit(f, i, q, **guess)
    print(result['summary'])
    model = lf.model(f, **result)
    plt.plot(i, q, 'o', markersize=2, label='data')
    plt.plot(model.real, model.imag, label='fit')
    plt.legend()
    plt.axis('equal')
    keys = ["f0", "qi", "qc"]
    print(*[key + f": {result[key]:g}" for key in keys])

    return simulation_name


def single_pixel(name, epsilon=None, inductor_kwargs=None, capacitor_kwargs=None,
                 feedline_kwargs=None, **kwargs):

    # epsilon for silicon is 11.2, for sapphire it is 9.3
    if inductor_kwargs is None:
        inductor_kwargs = {}
    if capacitor_kwargs is None:
        capacitor_kwargs = {}
    if feedline_kwargs is None:
        feedline_kwargs = {}

    save = kwargs.get('save', True)
    run = kwargs.get('run', True)
    folder = pathlib.Path(kwargs.get("folder", "sonnet/testing/"))
    single_freq = kwargs.get('single_freq', False) # sets the initial condition for single freq simulation

    dx = kwargs.get('dx', 0.5)  # grid size
    dy = kwargs.get('dy', 0.5)
    f1 = kwargs.get('f1', 4)  # starting freq
    f2 = kwargs.get('f2', 8)  # ending freq
    overwrite = kwargs.get('overwrite', False)
    height = kwargs.get("height", 200)  # pixel height in the y axis
    center_width = kwargs.get("center_width", 8)  # center strip width in x axis
    gap = kwargs.get("gap", 3)  # gap from ground planes
    ground1_width = 50 * center_width  # left side of center strip

    feed_geom = feedline(**feedline_kwargs)
    cap_geom = capacitor(**capacitor_kwargs)
    ind_geom = inductor(**inductor_kwargs)
    bbox = feed_geom.bounding_box()
    box_x = bbox[1][0] - bbox[0][0]
    box_y = bbox[1][1] - bbox[0][1]

    project = ps.GeometryProject()  # creates a project using the GeometryProject function in pysonnet
    project.setup_box(box_x, box_y, box_x / dx, box_y / dy)  # x width, y width, x cells, y cells
    project.set_units(length='um')
    project.set_box_cover("free space", top=True)
    project.set_box_cover("free space", bottom=True)

    # Define the dielectrics.
    project.add_dielectric("air", level=0, thickness=5000, epsilon=1)
    project.add_dielectric("sapphire", level=1, thickness=525, epsilon=epsilon,
                           dielectric_loss=1e-9, conductivity=0)

    # Set up the sweep.
    project.set_options(q_accuracy=True, resonance_detection=True,
                        current_density=True)
    # determine which sweep to use
    if single_freq == True:
        project.add_frequency_sweep("single", f1=f1)
    else:
        project.add_frequency_sweep("abs", f1=f1, f2=f2)
    project.set_analysis("frequency sweep")
    project['control']['speed'] = 1  # medium memory

    # Define the metal layers.
    project.define_metal("general", "Hf", ls=13, r_dc=0)
    project.define_metal("general", "Nb", ls=0.1, r_dc=0)
    project.define_technology_layer("metal", "inductor", 0, "Hf",
                                    fill_type="diagonal")
    project.define_technology_layer("metal", "capacitor", 0, "Nb",
                                    fill_type="diagonal")
    project.define_technology_layer("metal", "feedline", 0, "Nb",
                                    fill_type="diagonal")

    # Add the geometry
    project.add_gdstk_cell("metal", cap_geom, layer=0, tech_layer="capacitor")
    project.add_gdstk_cell("metal", ind_geom, layer=0, tech_layer="inductor")
    project.add_gdstk_cell("metal", feed_geom, layer=0, tech_layer="feedline")

    # Add ports
    project.add_port("standard", 1, x=ground1_width + gap + center_width / 2, y=0,
                     resistance=50)
    project.add_port("standard", 2, x=ground1_width + gap + center_width / 2, y=height,
                     resistance=50)
    project.add_output_file("touchstone2")

    # Create the file name and raise an error if it's already been simulated.

    if save:
        directory = Path(__file__).parent.absolute()
        simulation_file = directory / folder / f"{name}.son"
        output_file = Path(simulation_file.parent
                           / (simulation_file.stem + ".ts"))
        log.info(f"Simulating {simulation_file}")
        if output_file.is_file() and not overwrite:
            raise IOError(f"{output_file} already exists")

        # Create the sonnet file and run.
        project.make_sonnet_file(simulation_file)
        if run:
            project.run()

    return project, simulation_file


# if __name__ == "__main__":
#     logging.basicConfig(level='INFO')  # spits information out into the terminal
#
#     library = gdstk.Library()
#
#     feed = dict(center_width=8, gap=3, height=200, ground2_width=0.5, bottom_ground_height=24, cavity_height=115)
#     cap = dict(fingers=10, finger_gap=3, finger_width=1, coupling_bar_gap=0.5, coupling_bar_width=10, bar_height=10,
#                bar_width=325, left_bar_width=41.5, bar_gap=7)
#     ind = dict(spacing_between_inductor_waveguide=7, inductor_width=2, inductor_overlap=7, inductor_length=400)
#
#     # simulation('trial', epsilon=9, inductor_kwargs=ind, capacitor_kwargs=cap, feedline_kwargs=feed, overwrite='True')
#     single_pixel('pixel_l', epsilon=9.3, inductor_kwargs=ind, capacitor_kwargs=cap, feedline_kwargs=feed,
#                  overwrite='True')
