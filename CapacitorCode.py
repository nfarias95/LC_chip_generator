# this code generates the geometry of parallel plate and interdigitated capacitors
# based on book "Lumped elements for RF and microwave circuits "
# Nicole Farias 2020 - nfarias@berkeley.edu
import math
import numpy 
import gdspy

# CLASS TO SAVE ALL CAPACITOR PARAMETERS, USEFUL FOR WIRING 
class CapacitorMemoryClass():
    
    def __init__(self, num_capacitors):
        self.width = numpy.ones(num_capacitors) * (-1)
        self.height = numpy.ones(num_capacitors) * (-1)
        

    
# -------------------------------------------------------
#               Generate Paralell Plate  Capacitor Code
# -------------------------------------------------------

def GeneratePPCapacitorCell(lib, channel, MSLayer, GPLayer, DLayer, OxideLayer, TopLayer, C_length, via_pad_width, TL_width, tolerance):
    # this function generates a parallel plate capacitor cell
    PPC_cell_name = "PPC" + str(channel)
    PPC_cell = lib.new_cell(PPC_cell_name)
    #GROUND PLANE
    x1 = 0
    x2 = x1 + C_length + 2 * tolerance
    y1 = 0
    y2 = y1 + (C_length + 2 * tolerance)
    gp = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
    PPC_cell.add(gp)
    
    #TOP METAL IN CAPACITOR
    x1 = tolerance
    y1 = tolerance
    x2 = C_length + tolerance
    y2 = C_length + tolerance
    ms = gdspy.Rectangle( (x1, y1), (x2, y2), **MSLayer) 
    PPC_cell.add(ms)
    
    #VIA IN SI02 LAYER
    x1_pad = (x1 + x2)/2 - via_pad_width/2
    x2_pad = x1_pad + via_pad_width
    y1_pad = y1 +  (10*tolerance)
    y2_pad = y1_pad + (via_pad_width)
    via = gdspy.Rectangle( (x1_pad, y1_pad), (x2_pad, y2_pad), **OxideLayer) 
    PPC_cell.add(via)
    
    #WIRING LAYER (MICROSTRIP)
    #square pad
    x1_pad = x1_pad - 2*tolerance
    x2_pad = x2_pad + 2*tolerance
    y1_pad = y1_pad + (-2*tolerance)
    y2_pad = y2_pad + (2*tolerance)
    square = gdspy.Rectangle( (x1_pad, y1_pad), (x2_pad, y2_pad), **TopLayer) 
    PPC_cell.add(square)
    
    #wire
    x1 = (x1_pad + x2_pad)/2 - TL_width/2
    x2 = x1 + TL_width
    y1 = 0
    y2 = y1_pad
    wire = gdspy.Rectangle( (x1, y1), (x2, y2), **TopLayer) 
    PPC_cell.add(wire)
    
    
    
    return PPC_cell 
    




# --------------------------------------------------------------------------
# ------------------  INTERDIGITATED CAPACITOR CODE ------------------------
# --------------------------------------------------------------------------
def GenerateInterdigitatedCapacitorCell(lib, channel, GPLayer, TopLayer, OxideLayer, frequency, L, C, 
                                        via_pad_width, TL_width, tolerance):    
    IDC_name = "IDC_" + str(channel)
    IDC_cell = lib.new_cell(IDC_name)
       
    # CALCULATE CAPACITOR SIZE 
    num_lines, C.line_height = CalculateIDCapacitorParameters(C, frequency, L.inductance, C.h, C.line_width, C.er)
    C.width = num_lines * (C.line_width + C.gap_width)
    C.height = C.base_height * 2 + C.line_height + C.gap_width # total height of capacitor
    # CREATE BASE
    x1 = 0
    y1 = 0
    x2 = C.width
    y2 = C.base_height
    bot = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
    IDC_cell.add(bot)
    
    # CREATE TOP 
    x1 = 0
    x2 = C.width
    y1 = C.base_height + C.gap_width + C.line_height
    y2 = y1 + C.base_height
    top = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
    IDC_cell.add(top)
    
    
    # IF USING 3 LAYERS, CREATE VIAS
    if C.num_layers == 3:
        #CREATE VIA ON BOTTOM RECTANGLE
        x1 = C.width/2 - via_pad_width/2
        x2 = x1 + via_pad_width
        y1 =  via_pad_width 
        y2 = y1 + via_pad_width
        via_pad = gdspy.Rectangle( (x1, y1), (x2, y2) , **TopLayer)
        # create hole in silicon oxide layer
        via_hole = gdspy.Rectangle( (x1 + tolerance, y1 + tolerance), (x2-tolerance, y2 - tolerance), **OxideLayer)
        #ADD VIA WIRE
        x1 = C.width/2 - TL_width/2
        x2 = x1 + TL_width
        y1 = 0
        y2 = via_pad_width
        via_wire = gdspy.Rectangle( (x1, y1), (x2, y2) , **TopLayer)
        #add via to cell
        IDC_cell.add([via_pad, via_hole, via_wire])
    
    # CREATE LINES
    x1 = 0
    x2 = x1 + C.line_width
    
    for i in range(num_lines):
        #alternate where lines begin (top or bottom of capacitor)
        if ( i % 2 == 0 ):
            y1 = C.base_height + C.gap_width
        else:
            y1 = C.base_height
        y2 = y1 + C.line_height
        
        # ADD GEOMETRY
        line = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
        IDC_cell.add(line)
        
        #update x position
        x1 = x1 + C.gap_width + C.line_width
        x2 = x1 + C.line_width
    return(IDC_cell)


def CalculateIDCapacitorParameters(C, freq, L_lumped, h, W, er):
    #Calculate capacitance
    Cap = CalculateCapacitanceFromFrequency( L_lumped, freq, 1) # desired capacitance
    #print("Capacitance = %.2E Farads" %(Cap))        
        
    #SELECT LINE WIDTH, HEIGHT AND GAP WIDTH BASED ON FREQUENCY
    f = 0
    C.line_width = C.line_width_list[0]
    C.gap_width = C.gap_width_list[0]
    l_um = C.line_height_list[0]
    while freq > C.finger_freq_range[f] :
        if freq > C.finger_freq_range[ len(C.finger_freq_range) -1]:
            print("\nError!!! Frequency is out of range!\n")
            break 
        C.line_width = C.line_width_list[f]
        C.gap_width = C.gap_width_list[f]
        l_um = C.line_height_list[f]
        f = f + 1    
    
    #print(" l_um: ", l_um, "line width" ,C.line_width)    
        
    # calculate N   
    A1 = 4.409 * numpy.tanh( 0.55 * (h/W) ** (0.45)) * 1e-6 # (pF/um)
    A2 = 9.92 * numpy.tanh(0.52 * (h/W) ** (0.5)) * 1e-6   # (pF/um)

    C_picoF = Cap * 1e12 # go from farad to pico farad
    #C = (er + 1) * l * ( (N-3) * A1 + A2)
    # C / (  (er + 1) * l) = (N-3) * A1 + A2
    # ( C / ( (er + 1) * l ) - A2 ) / A1 = N -3
    # N = 3 + ( C / ( (er + 1) * l ) - A2 ) / A1
    
    N = int ( 3 + ( C_picoF / ( (er + 1) * l_um ) - A2 ) / A1 )
        
    #print("N = %d , l = %.2E (um) " %(N, l_um))    
    return N, l_um # number of fingers, length of finger

def CompareFrequencies(L_lumped, freq_array, N_array, l_um_array, h, W, N, er):
    
    # CALCULATE DESIRED CAPACITANCE BASED ON FREQUENCY SCHEDULE
    desired_C_array = CalculateCapacitanceFromFrequency( L_lumped, freq_array, len(freq_array) ) 
    
    print("-------------------------------------------------------------------------------------------------")
    print("|     Desired     |        Desired     |   Capacitance based  |    Resulting   |    Error in    |")
    print("| Frequency [Hz]  |    Capacitance [F] |    on equation [F]   | Frequency [Hz] | Frequency [%]  |" )
    print("-------------------------------------------------------------------------------------------------")
    # COMPARE DIFFERENT FREQUENCY RESULTS
    for f in range(len(freq_array)):
        freq = freq_array[f]
        #print("Desired Frequency: %.2E" % (freq))
        #print("Desired Capacitance = %.2E " %( desired_C_array[f]) )
    
        # CALCULATE CAPACITANCE BASED ON GEOMETRY
        N = N_array[f]
        l_um = l_um_array[f]
        CapL = CalculateIDCapacitanceLowFreq( er, l_um, h, W, N)
        #print( 'Calculated Capacitance = %.2E' %(CapL) )
    
        # "Error" in resonance frequency
        Fcalc = 1/(2*math.pi * math.sqrt(L_lumped * CapL)) # frequency calculated based on ID capacitor equations
        error = (freq-Fcalc)/freq * 100
        #print( "Frequencies: %.2E %.2E    Error: %.2f per cent \n" %(freq, Fcalc, error ))

        print("    %.2E      |       %.2E     |        %.2E      |     %.2E   |     %.2f      |" 
              %(freq, desired_C_array[f], CapL, Fcalc, error) )
    

# FUNCTION TO CALCULATE CAPACITANCE BASED ON GEOMETRY AASUMING LOW FREQUENCY
def CalculateIDCapacitanceLowFreq( er, l, h, W, N):
    # er = dielectric constant
    # l = length of the interdigital capcitor finger. must be in um
    # N = number of fingers
    # h = height of the substrate material
    # W = width of the conductor
    
    A1 = 4.409 * numpy.tanh( 0.55 * (h/W) ** (0.45)) * 1e-6 # (pF/um)
    A2 = 9.92 * numpy.tanh(0.52 * (h/W) ** (0.5)) * 1e-6   # (pF/um)

    C = (er + 1) * l * ( (N-3) * A1 + A2)

    C = C * 1e-12 # from pico farad to farad
    return C # in Farads



def CalculateCapacitanceFromFrequency( L, freq_array, nfreq):
    
    if nfreq == 1:
        desired_C = ( 1 / (2*math.pi * freq_array) ) ** 2 / L
        return desired_C
    
    else:
    
        #nfreq = len(freq_array)
        desired_C_array = numpy.zeros(nfreq)
    
        for f in range(nfreq):
            freq = freq_array[f]
            desired_C_array[f] = ( 1 / (2*math.pi * freq) ) ** 2 / L
    
    return desired_C_array
    



# FUNCTION TO CALCULATE CAPACITANCE BASED ON GEOMETRY AASUMING HIGH FREQUENCY
# NOT QUITE WORKING, DON'T USE THIS AS REFERENCE
def CalculateIDCapacitanceHighFreq( er, l, h, W, N, S):
    
    ere = er # WRONG, WHAT IS IT???
    
    a = W/2
    b = (W+S)/2
    k = math.tan(a * math.pi/(4*b)) **2
        
    k_prime = math.sqrt( 1 - k ** 2)
    
    if (k> 0.707 and k < 1):
        K_over_Kprime = 1/(math.pi) * math.log( 2 * (1 + math.sqrt(k)) / (1 - math.sqrt(k) ) ) # for 0.707 < k < 1 
    elif (k>0 and k<=0.707):
        K_over_Kprime = math.pi / ( 2 * (1 + math.sqrt(k_prime) ) / (1 - math.sqrt(k_prime) ) ) # for 0<k<0.707
    else:
        print("Something is wrong. k = ", k)
        
    CapH = ere * 1e-3 / (18*math.pi) * K_over_Kprime * (N - 1) * l # picofarads
    
    return CapH


