"""
LC resonator generator - main function 
Author: Nicole Farias

This code was originally adapted from a C code for the 40mux PPC chip shred by Toki Suzuki.
 
It has been used to generate the fabrication layers of a 128mux chip. I tried making it modular so that it 
can be used for any type of chip, but that might need a little tweaking.

I wasn't extremelly clean when I made the code, so some parameters are pulled from a text file at the 
beginning of the code, while other parameters are set on the "Parameters_Classes_example_chip" python
file containing classes for different cells. 


"""

import gdspy
import numpy
import os
#from wafer_cad_lib import WaferCadLib
from WireBodingPadCode import *
from CheckerBoardCode_aligned import *
from Parameters_Classes_128mux_chip1 import *
from WiringCode import CreateWires
from ReadChipParameters import *
#from ID_capacitor_v5 import *

def main():
    print("\nWelcome to the resonator chip maker!")
    print("Note: default length unit is microns")
    # import chip parameters from text file
    directory = os.getcwd() + "/"
    filename = 'Parameters_128mux_example_chip.txt'
    chip, C = read_chip_parameters( directory, filename) # read general chip + capacitor parameters
    print("Chip parameters read sucessfully.")
    # Output location for gds file
    directory = 'C:/Users/nicol/Documents/00Research/L-Edit/Resonator Project/128 mux/output/'
    filename = 'test.gds'
    fileoutput = directory + filename
    view = 1 # 1 open gds visualizer gui, 0 doesn't
    
    
    # CREATE GDS LIBRARY
    lib = gdspy.GdsLibrary()
    
    # CREATE LAYERS
    GPLayer = {"layer": 1, "datatype": 1}
    DLayer = {"layer": 4, "datatype": 4}
    MSLayer = {"layer": 2, "datatype": 5}
    OxideLayer = {"layer": 10, "datatype": 10}
    TopLayer = {"layer": 11, "datatype": 11}


    # ---------------------- GLOBAL CONSTANTS --------------------------
    #GENERAL PARAMETERS
    font_size = 400
    x0 = 0
    y0 = 0
    via_pad_width = 40 # Size of via pads for capacitor and inductor to change metal plane 
    tolerance = 10 # * 1000
    boundary = BoundaryClass()
    num_layers = 1 # number of layers used in this design
    
    #WIRING PARAMETERS
    TL_width = chip.TL_width # width of transmission line
    wire2wire_space = chip.wire2wire_space # space between wires
    wiring_gap = chip.wiring_gap # for the corners
    
    # INDUCTOR PARAMETERS
    L = InductorClass(num_layers)
    
    # CAPACITOR PARAMETERS
    #C = CapacitorClass("IDC", num_layers) # capacitor type can be parallel plate ("PPC") or interdigitated ("IDC")
    freq_array = chip.frequency_schedule  # frequency schedule
    
    # LC PARAMETERS
    LC_height = 2*L.outer_diameter 
    if num_layers == 1:
        LC_height = LC_height + L.pad_gap + L.pad_width

    LC = ResonatorClass( LC_height, L.outer_diameter ) # Individual Resonator Parameters. (height, width)

    # WIREBOND PADS PARAMETERS
    pad = PadClass()
    num_pads = chip.num_LCs
      
    
    # ---------------- FUNCTION CALLS ---------------------    
    
    
    # Sort LC channels into checkerboard position
    #Get number of rows and columns in checkerboard  
    num_LC_rows = chip.num_LC_rows
    num_LC_cols = chip.num_LC_cols
    print("- Sorting Channels into Position")
    sorted_freq_array = sortChannels( chip, len(freq_array))
    
    #Generate Cells
    print("- Generating Cells ")
    main_cell = lib.new_cell('Main') # main cell
    pad_cell = GeneratePadCell(lib, pad, TL_width, wire2wire_space, GPLayer) # wirebonding pad cell
    inductor_cell = GenerateInductorCell( lib, GPLayer, TopLayer, OxideLayer, via_pad_width, L, tolerance ) # inductor cell
    labels_cell, labels_height = CreateLabelsCell(lib, GPLayer, font_size, chip)
    # note: capacitor cell is generated inside GenerateLCcell function because capacitor geometry changes for each channel.   
    
    # GENERATE LABELS - UPDATE POSITION DEPENDING ON DESIGN
    print("- Generating Labels")
    l_x0 = x0 + wiring_gap/2 + 50
    l_y0 = y0  + labels_height + wiring_gap
    ref_labels = gdspy.CellReference(labels_cell, (l_x0, l_y0))
    main_cell.add(ref_labels)
    
    print("Generate Checkerboard ")
    print("chip.lc2lc y gap: ", chip.LC2LC_y_gap)
    #checkerboard position
    CB_x0 = x0 + wiring_gap/2
    CB_y0 = y0 +  L.height + wiring_gap + pad.width
    # create cell with all LCs
    allLCs, C_wire_loc_array, L_wire_loc_array, C_param_arrays, = GenerateLCCheckerboard(lib, MSLayer, GPLayer, DLayer, OxideLayer, TopLayer, chip, 
                                                                                         sorted_freq_array, LC, inductor_cell, L, C,  via_pad_width, TL_width, tolerance, labels_height)
    if C.type == "IDC":
            CB_y0 = CB_y0 + C.small_freq_offset
    # send LCs to main cell
    ref_allLCs = gdspy.CellReference(allLCs , (CB_x0, CB_y0))
    main_cell.add(ref_allLCs)
    
    print("- Generating Pads")
    # GENERATE PAD TOP AND BOTTOM ARRAYS
    #total_LCs_y_gap = 43000 + 2 * wiring_gap  # space between pads devoted to LCs    
    total_LCs_y_gap = (LC.height + chip.LC2LC_y_gap[0]) * chip.num_LC_rows + 2 * chip.wiring_gap  # space between pads devoted to LCs
    total_LCs_x_gap = 1.5*wiring_gap + ( chip.LC2LC_x_gap + LC.width) * num_LC_cols - chip.LC2LC_x_gap
    if C.type == "IDC":
        total_LCs_y_gap = total_LCs_y_gap + 2 * C.small_freq_offset
    #make pads
    ref_pads, top_pads_loc_array, bot_pads_loc_array = GeneratePads(x0, y0, lib, pad_cell, pad, num_pads,  total_LCs_y_gap,
                                                                    total_LCs_x_gap , wire2wire_space)
    main_cell.add(ref_pads)
    

    
    # CREATE WIRING
    print("- Generating Wires")
    wires_cell = CreateWires(lib, GPLayer, x0, y0, CB_x0, CB_y0, wire2wire_space, TL_width, C_param_arrays, C_wire_loc_array, L_wire_loc_array, LC, L, pad, 
                             chip.num_LCs, num_LC_rows, num_LC_cols, top_pads_loc_array, bot_pads_loc_array, chip.LC2LC_x_gap)
    main_cell.add(wires_cell)
    
       
    #GENERATE BOUNDARY LINES
    print("- Generating Boundary Lines")
    total_chip_height = total_LCs_y_gap + 2 * pad.width
    total_chip_width = total_LCs_x_gap
    GenerateBoundaries( GPLayer, main_cell, x0, y0, boundary, total_chip_height, total_chip_width )
    
    # OUTPUTS
    
    print("LC height: ", LC.height ,"LC width: ", LC.width)
    print("Max LC gap: ", LC.total_height)
    print("Number of pads: ", num_pads)
    print("Total chip size: %d x %d microns." %(total_chip_width, total_chip_height))
    

    
    # ---------- END OF PROGRAM -----------------
    #Save the library in a file called 'first.gds'
    lib.write_gds(fileoutput)
    if view == 1:
        #Display all cells using the internal viewer.
        gdspy.LayoutViewer()
    print("The end!")

# --------------------------------    USER DEFINED FUNCTIONS     -----------------------------------------

# CREATE LABELS WITH INFORMATION ABOUT THE CHIP

def CreateLabelsCell(lib, layer, font_size, chip):
    labels_cell = lib.new_cell("Labels")
    #Generate Labels to identify chips
    author = "N. Farias "
    inst = "UCB - LBNL" # institution
    x0 = 0
    y0 = 0
    #channel_text = gdspy.Text(str(channel), LC.channel_text_size, (x_LC, y_LC + channel_y_offset ), **GPLayer ) 
    name_text = gdspy.Text( chip.name  , font_size, (x0, y0), **layer )
    date_text = gdspy.Text(chip.date, font_size, (x0, y0 - 1.5*font_size), **layer )
    author_text = gdspy.Text(author, font_size, (x0, y0 - 3*font_size), **layer )
    inst_text = gdspy.Text(inst, font_size, (x0, y0 - 4.5*font_size), **layer )
    
    labels_cell.add([name_text, date_text, author_text, inst_text])
    
    labels_height = font_size * 6
    
    return labels_cell, labels_height
    

def test( cell, layer):
    # a test function that makes a little rectangle appear
    x1 = 0
    x2 = 100
    y1 = 0
    y2 = 100
    testGeo = gdspy.Rectangle( (x1, y1), (x2, y2), **layer) # test geometry
    cell.add(testGeo)

def sortChannels( chip, nfreq):
    nrows = chip.num_LC_rows
    ncols = chip.num_LC_cols
    nspots = nrows * ncols
    #print("Number of spots: " , nspots)
    sorted_freq_array = numpy.zeros(nspots)
    
    for i in range(nspots):
        channel = chip.channel_order[i]
        if channel >= 0:
            sorted_freq_array[i] = chip.freq_schedule[channel]
        else:
            sorted_freq_array[i] = -1 # for the blanck spots    
    
    return sorted_freq_array

def CalculateNumberOfRowsColumns( num_pads, num_LCs, LC, y_wiring_gap, pad):
    #calculate number of LC rows and columns in chip 
    total_chip_width = (pad.width + pad.spacing) * num_pads # total width of the chip is based only on number and geometry of wirebonding pads
    num_LC_columns = int( total_chip_width / (LC.width + y_wiring_gap) )
    num_LC_rows = int( num_LCs / num_LC_columns )
    
    return (num_LC_rows, num_LC_columns)
    

def GenerateBoundaries( Layer, main_cell, x0, y0, boundary, total_chip_height, total_chip_width ):
    # this function draws boundaries around the chip
    #bottom line
    x1 = x0 - boundary.gap
    x2 = x1 + total_chip_width + 2 * boundary.gap
    y1 = y0 - boundary.gap
    y2 = y1 - boundary.line_width
    bot = gdspy.Rectangle( (x1, y1), (x2, y2), **Layer) # test geometry

    # left line
    x1 = x0 - boundary.gap - boundary.line_width
    x2 = x1 + boundary.line_width
    y1 = y0 - boundary.gap - boundary.line_width
    y2 = y1 + 2 * boundary.gap + 2 * boundary.line_width + total_chip_height
    left = gdspy.Rectangle( (x1, y1), (x2, y2), **Layer) # test geometry
    
    #right line
    x1 = x0 + boundary.gap + total_chip_width
    x2 = x1 + boundary.line_width
    y1 = y0 - boundary.gap - boundary.line_width 
    y2 = y1 + 2 * boundary.gap + 2 * boundary.line_width + total_chip_height
    right = gdspy.Rectangle( (x1, y1), (x2, y2), **Layer) # test geometry
    
    #top line
    x1 = x0 - boundary.gap
    x2 = x1 + total_chip_width + 2 * boundary.gap
    y1 = y0 + boundary.gap + boundary.line_width + total_chip_height
    y2 = y1 - boundary.line_width
    top = gdspy.Rectangle( (x1, y1), (x2, y2), **Layer) # test geometry

    main_cell.add([bot, left, right, top])


    

if __name__ == "__main__":
    main()