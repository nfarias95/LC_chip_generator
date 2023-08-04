#this script is used to read chip parameters from a text file
import numpy
import re
from Parameters_Classes import *

def read_chip_parameters( directory: str , filename: str):
    chip = Chip()
    file = open(directory + filename , 'r')
    lines = file.readlines()
    #save chip info
    lc = 1
    chip.name = str( lines[lc] )
    lc = lc + 1
    chip.date = str(lines[lc])

    # save number of rows and columns
    lc = lc + 2
    nr , nc =  lines[lc].split() 
    chip.num_LC_rows = int(nr)
    chip.num_LC_cols = int(nc)
    
    # save spacing parameters
    lc = lc + 3
    LC2LC_y_gap = re.findall(r'-?\d+', lines[lc])
    chip.LC2LC_y_gap = list(map(int, LC2LC_y_gap))
    
    lc = lc + 2
    chip.LC2LC_x_gap = int(lines[lc])
    
    # save wiring parameters
    lc = lc + 3
    tl_width, wiring_gap, wire2wire = lines[lc].split()
    chip.TL_width = int(tl_width) # width of transmission line
    chip.wiring_gap = int(wiring_gap) # gap between wires and edge of chip
    chip.wire2wire_space = int(wire2wire) # space between wires

    #save channel order
    lc = lc + 2
    temp = re.findall(r'-?\d+', lines[lc])
    chip.channel_order = list(map(int, temp))    
    # count number of resonators
    count_LCs(chip)

    #save frequency schedule
    lc = lc + 2
    num_freq =  int(lines[lc])
    print("number of frequencies: ", num_freq)
    f = 0
    chip.freq_schedule = numpy.zeros( num_freq ) 
    lc = lc + 2

    for l in range(lc, lc + num_freq):
        chip.freq_schedule[f] = float( lines[l]  )
        f = f+1
        
    lc = lc + num_freq
    C = read_capacitor_parameters(lc, lines)

    file.close()
    
    return chip, C

def read_capacitor_parameters(lc, lines):
#            self.gap_width = 4
#            self.line_width = 4
#            self.base_height = 100 
#            self.width = 100
#            self.line_height = 100
#            self.er = 11.7 # dielectric constant, using Silicon = 11.7
#            self.h = 675   # [microns] thickness of substrate 
#            self.height = self.base_height * 2 + self.line_height + self.gap_width # total height of capacitor
#            self.small_freq_offset =  0 #6150 - (3850) + 500

    # Read Capacitor type
    lc = lc + 3
    #capacitor_type = str( lines[lc] )
    capacitor_type = str.rstrip( lines[lc] )    
    # Read number of etched layers 
    lc = lc + 2
    numLayers = int( lines[lc])
    #Initialize capacitor class
    C = CapacitorClass(capacitor_type, numLayers) 
    # Read dielectric constant and thickness of substrate
    lc = lc + 2
    er , h =  lines[lc].split() 
    C.er = float(er)
    C.h = int(h)
    #Read frequency range to set line width, height and gap width
    lc = lc + 2
    finger_freq_range = re.findall(r'-?\d+', lines[lc])
    C.finger_freq_range = list(map(float, finger_freq_range))
    # read line width and height
    lc = lc + 2
    line_width = re.findall(r'-?\d+', lines[lc])
    C.line_width_list = list(map(int,line_width))
    lc = lc + 2
    gap_width = re.findall(r'-?\d+', lines[lc])
    C.gap_width_list = list(map(int, gap_width))
    # read line height list
    lc = lc + 2
    line_height_list = re.findall(r'-?\d+', lines[lc])
    C.line_height_list = list(map(int, line_height_list))

    #print("\n\n C.finger freq range: ", C.finger_freq_range, "\n\n")

    return C

def count_LCs(chip):
    num_spots = len(chip.channel_order)
    chip.num_LCs = 0
    for i in range(num_spots):
        if chip.channel_order[i] >= 0:
            chip.num_LCs = chip.num_LCs + 1
            
    return 0