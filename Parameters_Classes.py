# THIS SCRIPT CONTAINS THE CLASSES USED IN THE GENERATION OF THE RESONATOR CHIP
import numpy
class Chip:
    def __init__(self):
        #general information
        self.name = "CHIP NAME"
        self.date = "DATE"
        #geometry
        self.num_LC_rows = 5 #dummy value
        self.num_LC_cols = 5 #dummy value
        #frequency information
        self.frequency_schedule = numpy.zeros(self.num_LC_rows * self.num_LC_cols)
        self.channel_order = numpy.zeros(self.num_LC_rows * self.num_LC_cols)
        self.num_LCs = 0 #dummy value
        #WIRING PARAMETERS
        self.TL_width = 10 # width of transmission line
        self.wire2wire_space = 20 # space between wires
        self.wiring_gap = 500 # wiring gap for the corners of the chip
        self.LC2LC_y_gap = 180
        self.LC2LC_x_gap = 1000
        
class PadClass:
    
    def __init__(self):
        self.width = 500
        self.spacing = 300
        
        
class InductorClass:
# numLayers : number of etched layers    
    def __init__(self, numLayers):
        self.num_layers = numLayers # number of etched layers
        self.gap_width = 4 #microns 
        self.line_width = 4 # microns
        self.num_turns = 154 # number of turns in coil
        self.outer_diameter = 3850 # size of inductor
        self.inductance = 60e-6 # inductance [Henry]
        
        if numLayers == 1:
            self.type = "with_pads"
            self.pad_gap = 20
            self.pad_width = 400
            self.pad_length = 3850
            self.height = self.pad_width + self.pad_gap +  self.outer_diameter
        else:
            self.type == "without_pads"
            self.height = self.outer_diameter
        
class CapacitorClass:
    def __init__(self, Ctype, numLayers):
    # numLayers : number of etched layers
        
        self.type = Ctype # save this information
        self.num_layers = numLayers
        if Ctype == "PPC":  # parallel plate capacitor
            #used in parallel plate capacitor -- maybe create this?
            self.length = 0
            self.height = 0
        if Ctype == "IDC": #interdigital capacitor
            #used in interdigitated capacitor
            self.gap_width = 4
            self.line_width = 4
            self.base_height = 100 
            self.width = 100
            self.line_height = 100
            self.er = 11.7 # dielectric constant, using Silicon = 11.7
            self.h = 675   # [microns] thickness of substrate 
            self.height = self.base_height * 2 + self.line_height + self.gap_width # total height of capacitor
            self.small_freq_offset =  0 #6150 - (3850) + 500
        
class ResonatorClass:
    def __init__(self, height, width):
        self.height = height 
        self.width = width
        self.gap = 50 # space between capacitor and inductor
        self.channel_text_size = 80
        self.channel_text_gap = 10
        self.total_height = height

class BoundaryClass:
    def __init__(self):
        self.gap = 100
        self.line_width = 50