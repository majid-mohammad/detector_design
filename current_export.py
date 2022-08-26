from typing import List
import xml.etree.ElementTree as ET
from xml.dom import minidom
import psutil
import os
import subprocess
import logging
import pathlib

log = logging.getLogger(__name__)

class JXYPort:
    capacitance: int
    inductance: int
    number: int
    phase: int
    reactance: int
    resistance: int
    voltage: str

    def __init__(self, capacitance: int, inductance: int, number: int, phase: int, reactance: int, resistance: int, voltage: str) -> None:
        self.capacitance = capacitance
        self.inductance = inductance
        self.number = number
        self.phase = phase
        self.reactance = reactance
        self.resistance = resistance
        self.voltage = voltage


class Drive:
    jxy_port: List[JXYPort]

    def __init__(self, jxy_port: List[JXYPort]) -> None:
        self.jxy_port = jxy_port


class Grid:
    x_step: int
    y_step: int

    def __init__(self, x_step: int, y_step: int) -> None:
        self.x_step = x_step
        self.y_step = y_step


class Levels:
    stop: int
    range: str
    start: int

    def __init__(self, stop: int, range: str, start: int) -> None:
        self.stop = stop
        self.range = range
        self.start = start


class Frequency:
    value: str

    def __init__(self, value: str) -> None:
        self.value = value


class Locator:
    frequency: List[Frequency]

    def __init__(self, frequency: List[Frequency]) -> None:
        self.frequency = frequency


class Measurement:
    complex: str
    type: str

    def __init__(self, complex: str, type: str) -> None:
        self.complex = complex
        self.type = type


class Region:
    style: str

    def __init__(self, style: str) -> None:
        self.style = style


class JXYExport:
    region: Region
    levels: Levels
    grid: Grid
    measurement: Measurement
    drive: Drive
    locator: Locator
    filename: str
    label: str

    def __init__(self, region: Region, levels: Levels, grid: Grid, measurement: Measurement, drive: Drive, locator: Locator, filename: str, label: str) -> None:
        self.region = region
        self.levels = levels
        self.grid = grid
        self.measurement = measurement
        self.drive = drive
        self.locator = locator
        self.filename = filename
        self.label = label


class JXYExportSet:
    jxy_export: JXYExport

    def __init__(self, jxy_export: JXYExport) -> None:
        self.jxy_export = jxy_export


class Welcome4:
    jxy_export_set: JXYExportSet

    def __init__(self, jxy_export_set: JXYExportSet) -> None:
        self.jxy_export_set = jxy_export_set


def current_export_xml_test():

    #define filename to be exported
    JXYExport.filename = "current1.csv"

    # defien the sonnet file whise data we want to access
    JXYExport.label = "current1.son"

    # entire sonnet bounding box = "Whole"
    Region.style = "Whole"

    # current density level
    Levels.stop = "0"
    Levels.range = "Some"
    Levels.start = "0"

    # grid size for each cell
    Grid.x_step = "10"
    Grid.y_step = "10"

    # measurement type
    Measurement.complex = "No"
    Measurement.type = "jxy"

    # Port parameters
    JXYPort.capacitance = "O"
    JXYPort.inductance = "O"
    JXYPort.number = "1"
    JXYPort.phase = "O"
    JXYPort.reactance = "O"
    JXYPort.resistance = "5O"
    JXYPort.voltage = "1"

    #Freq of interest
    Frequency.value = "1000000000"


    # xml file generation

    JXY_Export_Set = ET.Element("JXY_Export_Set")

    JXY_Export = ET.SubElement(JXY_Export_Set, "JXY_Export", Filename=JXYExport.filename, Label=JXYExport.label)

    ET.SubElement(JXY_Export, "Region", Style= Region.style)
    ET.SubElement(JXY_Export, "Levels", Stop=Levels.stop, Range=Levels.range, Start=Levels.start)
    ET.SubElement(JXY_Export, "Grid", XStep=Grid.x_step, YStep=Grid.y_step)
    ET.SubElement(JXY_Export, "Measurement", Complex=Measurement.complex, Type=Measurement.type)

    Drive = ET.SubElement(JXY_Export, "Drive")


    ET.SubElement(Drive, "JXYPort", Capacitance=JXYPort.capacitance, Inductance=JXYPort.inductance, Number=JXYPort.number,
                  Phase=JXYPort.phase, Reactance=JXYPort.reactance, Resistance=JXYPort.resistance, Voltage=JXYPort.voltage)

    # notice below that i defined the number and voltage without using the class. Honestly im not sure what the class is doing
    # i could jsut hard code the data in each variable without the Class. Perhaps you have some intuition on how to incorperate
    # the classes that are defined above.

    ET.SubElement(Drive, "JXYPort", Capacitance=JXYPort.capacitance, Inductance=JXYPort.inductance,
                  Number="2",
                  Phase=JXYPort.phase, Reactance=JXYPort.reactance, Resistance=JXYPort.resistance,
                  Voltage="0")

    Locator = ET.SubElement(JXY_Export, "Locator")

    ET.SubElement(Locator, "Frequency", Value=Frequency.value)

    tree = ET.ElementTree(JXY_Export_Set)
    tree.write("test.xml", encoding='utf-8', xml_declaration=True)

    #turns the xml file into the prettyprint format needed for sonnet
    xmlstr = minidom.parseString(ET.tostring(JXY_Export_Set)).toprettyxml(indent="\t", encoding='utf-8')
    with open("test.xml", "wb") as f:
        f.write(xmlstr)

# this runs the command in the terminal
def export_command(sonnet_path,xml,sonnet_file):

    # path to soncmd
    soncmd_path = os.path.join(sonnet_path, 'bin', 'soncmd')

    # collect the command to run
    command = [soncmd_path,'-JXYExport', xml, sonnet_file]

    with psutil.Popen(command, stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE) as process:
        while True:
            output = process.stdout.readline().decode('utf-8')
            if output == '' and process.poll() is not None:
                break
            if output.strip():
                log.info(output.strip())


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
    frequency = kwargs.get('frequency', "1000000000")


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

# current_export_xml_test()
# export_current_density(folder='sonnet/fine', xml_name='pixel_0_0', csv_name="pixel_6d56912_11841d9.csv", son_label="pixel_6d56912_11841d9.son", frequency=str(int(6.5691*10**9)))

# export_current_density('sonnet')
# export_command(sonnet_path="/opt/sonnet", xml='test.xml', sonnet_file='current1.son')