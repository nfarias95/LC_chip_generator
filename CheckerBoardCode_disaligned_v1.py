# This is the LC Library Code
import gdspy
import numpy
from InductorCode import GenerateInductorCell
from CapacitorCode import *
from WiringCode import GetLCWiringPositions

def GenerateLCCheckerboard(lib, MSLayer, GPLayer, DLayer, OxideLayer, TopLayer, chip, 
                           freq_array, LC, inductor_cell, L, C,  via_pad_width, TL_width, tolerance, labels_height):


    allLCs_cell = lib.new_cell("All_LCs")
    x_LC = 0 # start at origin, it's a cell
    y_LC = 0
    channel = 0
    num_spots = chip.num_LC_rows * chip.num_LC_cols
    spot = 0 # spot in checkerboard. Note number of spots (108) is different from number of channels (100)
    
    #VARIABLES TO SAVE LOCATION OF CAPACITORS AND INDUCTORS
    C_wire_loc_array = numpy.ones([num_spots, 2]) * (-3.14159)
    L_wire_loc_array = numpy.ones([num_spots, 2]) * (-3.14159)
    C_param_arrays = CapacitorMemoryClass(num_spots) 
    
    #VARIABLE TO SAVE LC HEIGHT OF EACH PREVIOUS COLUMN - annoying because I read row-> col instead of col->row
    LC_heights = numpy.zeros(chip.num_LC_cols)
    y_LC = numpy.zeros(chip.num_LC_cols)
    # add offset for even columns
    for col in range(chip.num_LC_cols):
        if col % 2 == 0:
            y_LC[col] = y_LC[col] - 2 * L.outer_diameter - chip.LC2LC_y_gap[col]
    #make space for the labels                
    y_LC[0] = y_LC[0] + labels_height
    
    for row in range(chip.num_LC_rows):
        x_LC = 0 # go back to first column location
        for col in range(chip.num_LC_cols):
            
            #create LC cell
            if spot < len(freq_array):
               freq = freq_array[spot]
            else:
                freq = -2
                LC.height = 0
                
            
            if freq > 0:
                #find channel number
                channel = chip.channel_order[spot]
                                      
                #create LC cell
                LC_cell = GenerateLCCell(lib, freq, channel, MSLayer, GPLayer, DLayer, OxideLayer, TopLayer, inductor_cell, L,
                        C, via_pad_width, TL_width, LC, tolerance)
                
                #save height of LC:
                LC.height = L.outer_diameter + LC.gap + C.height
                if L.num_layers == 1:
                    LC.height = LC.height + L.pad_gap + L.pad_width
                
                
                   
                # check column for orientation                    
                if col % 2 == 0 : 
                    # find y_LC
                    #print("Channel: ", channel, "y_LC: ", y_LC[col], "LC height: ", LC.height)
                    y_LC[col] = y_LC[col] + chip.LC2LC_y_gap[col] + LC.height
                    
                    #insert LC
                    ref_LC_x = x_LC 
                    ref_LC_y = y_LC[col] 
                    ref_LC = gdspy.CellReference( LC_cell, (ref_LC_x, ref_LC_y))
                    #insert channel number on top of inductor
                    channel_y_offset = + L.height + LC.channel_text_gap
                    #create channel label
                    channel_text = gdspy.Text(str(channel), LC.channel_text_size, 
                                          (x_LC  , y_LC[col] + channel_y_offset ),  horizontal = True, **GPLayer ) 
                    
                else:
                    #insert LC with rotation
                    ref_LC_x = x_LC + L.outer_diameter 
                    ref_LC_y = y_LC[col] 
                    ref_LC = gdspy.CellReference( LC_cell, (ref_LC_x, ref_LC_y), rotation=180)
                    #insert channel number at the bottom of inductor
                    channel_y_offset =  - (L.height + LC.channel_text_gap + LC.channel_text_size) 
                    
                    #create channel label
                    channel_text = gdspy.Text(str(channel), LC.channel_text_size, 
                                          (x_LC  , y_LC[col] + channel_y_offset ),  horizontal = True, **GPLayer ) 
                    #update y location
                    LC_heights[col]  = LC.height
                    y_LC[col] = y_LC[col] + LC_heights[col] + chip.LC2LC_y_gap[col]
                    

                
                
                
                # SAVE POSITION OF LC FOR WIRING PUROPSES
                C_wire_loc_array[spot, :], L_wire_loc_array[spot, :] = GetLCWiringPositions(LC, L, C, col, ref_LC_x , ref_LC_y)
                C_param_arrays.width[spot] = C.width
                C_param_arrays.height[spot] = C.height
                
                #add LC cell and label to all LCs cell    
                allLCs_cell.add([channel_text, ref_LC])
                
                #END OF IF STATEMENT
            else:
                LC.height = 0
                    

            #update x location
            x_LC = x_LC + LC.width + chip.LC2LC_x_gap


            #update counter
            spot = spot + 1
    
    LC.total_height = max(y_LC)
        
    

    return allLCs_cell, C_wire_loc_array, L_wire_loc_array, C_param_arrays

def GenerateLCCell(lib, freq, channel, MSLayer, GPLayer, DLayer, OxideLayer, TopLayer, inductor_cell, L,
                    C, via_pad_width, TL_width, LC, tolerance):
    LC_name = "LC" + str(channel)
    LC_cell = lib.new_cell(LC_name) 
    
    # pick capacitor  depending on its type
    if C.type == "PPC":   
        
        #calculate capacitor size based on frequency
        C.length = 4000 # a placeholder
        #generate capacitor cell specific to this capacitor length
        capacitor_cell = GeneratePPCapacitorCell(lib, channel, MSLayer, GPLayer, DLayer, OxideLayer, TopLayer, 
                                             C.length, via_pad_width, TL_width, tolerance)
        C.height = C.length + 2 * tolerance
        
    elif C.type == "IDC":
        #generate capacitor cell
        capacitor_cell = GenerateInterdigitatedCapacitorCell(lib, channel, GPLayer, TopLayer, OxideLayer, freq, L, C, 
                                        via_pad_width, TL_width, tolerance)
        
    L_x0 = 0
    L_y0 = 0
    C_x0 = 0
    C_y0 = L_y0 -(LC.gap  +C.height)
    
    
    
    #connect capactor and inductor
    x1 = L_x0
    x2 = x1 + L.line_width
    y1 = L_y0
    y2 = y1 - LC.gap
    LC_connect = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
    LC_cell.add(LC_connect)
    
    #position capacitor and inductor
    ref_L = gdspy.CellReference( inductor_cell, (L_x0, L_y0))
    ref_C = gdspy.CellReference( capacitor_cell, (C_x0, C_y0))
    
    LC_cell.add([ref_L, ref_C])
    
    return LC_cell




