import logging
import pathlib
import numpy as np
from pysonnet import outputs
import xml.etree.ElementTree as ET
from xml.dom import minidom
import psutil
import os
import subprocess

log = logging.getLogger(__name__)


def export_current_density(folder, **kwargs):

    directory = pathlib.Path(__file__).parent.absolute()

    # xml file name
    xml_name = kwargs.get('xml_name', 'test')

    # define csv filename to be exported
    csv_name = kwargs.get('csv_name', "current1.csv")

    # define the sonnet file whose data we want to access
    son_label = kwargs.get('son_label', "current1.son")

    # entire sonnet bounding box = "Whole"
    region_style = kwargs.get('region_style', "Rect")
    # box dimensions for 900um inductor
    left = kwargs.get('left', '457')
    right = kwargs.get('right', '1357')
    top = kwargs.get('top', '41')
    bottom = kwargs.get('bottom', '39')

    # current density level
    levels_stop = kwargs.get('levels_stop', "0")
    levels_range = kwargs.get('levels_range', "Some")
    levels_start = kwargs.get('levels_start', "0")

    # grid size for each cell
    grid_x_step = kwargs.get('grid_x_step', "0.25")
    grid_y_step = kwargs.get('grid_y_step', "0.25")

    # measurement type
    measurement_complex = kwargs.get('measurement_complex', "No")
    measurement_type = kwargs.get('measurement_type', "jxy")

    # Port1 parameters
    capacitance = kwargs.get('capacitance', "O")
    inductance = kwargs.get('inductance', "O")
    number1 = kwargs.get('number1', "1")
    phase = kwargs.get('phase', "O")
    reactance = kwargs.get('reactance', "O")
    resistance = kwargs.get('resistance', "5O")
    voltage1 = kwargs.get('voltage1', "1")

    # Port2 parameters
    number2 = kwargs.get('number2', "2")
    voltage2 = kwargs.get('voltage2', "0")

    # Freq of interest
    frequency = kwargs.get('frequency', "6000000000") # freq must be in Hz


    # xml file generation

    JXY_Export_Set = ET.Element("JXY_Export_Set")

    JXY_Export = ET.SubElement(JXY_Export_Set, "JXY_Export", Filename=csv_name, Label=son_label)

    ET.SubElement(JXY_Export, "Region", Style=region_style, Left=left, Right=right, Top=top, bottom=bottom)
    ET.SubElement(JXY_Export, "Levels", Stop=levels_stop, Range=levels_range, Start=levels_start)
    ET.SubElement(JXY_Export, "Grid", XStep=grid_x_step, YStep=grid_y_step)
    ET.SubElement(JXY_Export, "Measurement", Complex=measurement_complex, Type=measurement_type)

    Drive = ET.SubElement(JXY_Export, "Drive")


    ET.SubElement(Drive, "JXYPort", Capacitance=capacitance, Inductance=inductance, Number=number1,
                  Phase=phase, Reactance=reactance, Resistance=resistance, Voltage=voltage1)

    ET.SubElement(Drive, "JXYPort", Capacitance=capacitance, Inductance=inductance,
                  Number=number2,
                  Phase=phase, Reactance=reactance, Resistance=resistance,
                  Voltage=voltage2)

    Locator = ET.SubElement(JXY_Export, "Locator")

    ET.SubElement(Locator, "Frequency", Value=frequency)

    tree = ET.ElementTree(JXY_Export_Set)
    tree.write(xml_name + '.xml', encoding='utf-8', xml_declaration=True)

    #turns the xml file into the prettyprint format needed for sonnet
    xmlstr = minidom.parseString(ET.tostring(JXY_Export_Set)).toprettyxml(indent="\t", encoding='utf-8')

    # move to the folder with .son file.
    # One problem is that the original tree.write file also exists so I need to delete that one in the process
    directed_xml = os.path.join(directory / folder, xml_name + '.xml')
    with open(directed_xml, "wb") as f:
        f.write(xmlstr)

    # path to soncmd
    soncmd_path = os.path.join('/opt/sonnet', 'bin', 'soncmd')

    # specify where the sonnet file lives
    son_label = os.path.join(directory / folder / son_label)
    # collect the command to run
    command = [soncmd_path, '-JXYExport', directed_xml, son_label]

    with psutil.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        while True:
            output = process.stdout.readline().decode('utf-8').strip()
            error = process.stderr.readline().decode('utf-8').strip()
            if not output and not error and process.poll() is not None:
                break
            if output:
                log.info(output)
            if error:
                log.error(error)

    # remove the original xml file
    os.remove(xml_name + '.xml')



def compute_uniformity_single(name):

    # the width w(x) is proportional to J(x)
    # we want to solve for a constant 'a' that equates w(x) = a J(x)
    # Inductance per square is L = Ls * l/w.
    # inital inductance per square is L0 = Ls * l/w0
    # Therefore the total inductance can be written as dL = Ls * dl/w(x)
    # the new inductance divided by the original L is equal to 1
    # L0/L = 1 = (l/w0) / (integral[dl/w(x)])
    # 1 = (l*a) / (w0 * integral[dl/J(x)])
    # a = (w0 * integral[dl/J(x)]) / l
    # w(x) = (w0 * J(x) * integral[dx/J(x)]) / l

    directory = pathlib.Path(__file__).parent.absolute()
    cd = outputs.CurrentDensity(directory / (name + ".csv"))  # creates an object with the current desnity file
    jd = cd.current_density()  # Outputs current density
    mean_jd = np.mean(jd, axis=0)  # finds the mean along the width of inductor
    integral = np.trapz(1/mean_jd)
    w0 = 2 / cd.dy #um
    l = 800 / cd.dx #um
    w = (w0 * mean_jd * integral) / l # new width
    w_new = w * cd.dy
    w_new = np.round_(w_new,2)
    return w_new


# def compute_uniformity_array(name, folder='uniformity'):
#     directory = pathlib.Path(__file__).parent.absolute()
#     folder = pathlib.Path(folder)
#
#     # load npz file
#     npz = np.load('results.npz')
#
#     cd = outputs.CurrentDensity(directory / folder / (name + ".csv")) # creates an object with the current desnity file
#
#     # Set the boundry of the inductor region to be tapered
#     top = int(53 / cd.dy)  # Manually setting inductor location (could change)
#     bottom = int(55 / cd.dy)
#     left = int(500 / cd.dx)
#     right = int(1300 / cd.dx)
#     jd = cd.current_density()[top:bottom,left:right] # Outputs current density
#     mean_jd = np.mean(jd,axis=0) # finds the mean along the width of inductor
#
#     # the width w(x) is proportional to J(x)
#     # we want to solve for a constant 'a' that equates w(x) = a J(x)
#     # Inductance per square is L = Ls * l/w.
#     # inital inductance per square is L0 = Ls * l/w0
#     # Therefore the total inductance can be written as dL = Ls * dl/w(x)
#     # the new inductance divided by the original L is equal to 1
#     # L0/L = 1 = (l/w0) / (integral[dl/w(x)])
#     # 1 = (l*a) / (w0 * integral[dl/J(x)])
#     # a = (w0 * integral[dl/J(x)]) / l
#     # w(x) = (w0 * J(x) * integral[dx/J(x)]) / l
#
#     integral = np.trapz(1/mean_jd)
#     w0 = 2 / cd.dy #um
#     l = 800 / cd.dx #um
#     w = (w0 * mean_jd * integral) / l # new width
#     print(w)
#     return w


# compute_uniformity_single('pixel_6d56912_11841d9')
