# THIS FILE CONTAINS THE FUNCTIONS NECESSARY FOR THE GENERATION OF THE PADS
import numpy
import gdspy
# function to generate pad cell
def GeneratePadCell(lib, pad, TL_width, wire2wire_space, TopLayer):
    pad_cell = lib.new_cell("Pad")
    x1 = 0
    x2 = pad.width
    y1 = 0
    y2 = pad.width
    square = gdspy.Rectangle( (x1, y1), (x2, y2), **TopLayer) 
    wire = gdspy.Rectangle( ( (x1+x2)/2 - TL_width/2, y2), ( (x1+x2)/2 + TL_width/2, y2 + wire2wire_space) , **TopLayer) 
    pad_cell.add(square)
    pad_cell.add(wire)
    return pad_cell

def GeneratePads(x0, y0, lib, pad_cell, pad, num_pads, total_LCs_y_gap, total_LCs_x_gap, wire2wire_space):
    
    pad_arrays = lib.new_cell("PadArray")
    #arrays to save positions of pads
    top_pads_loc_array = numpy.ones((num_pads, 2)) * (-3.14159)
    bot_pads_loc_array = numpy.ones((num_pads, 2)) * (-3.14159)
    x = x0
    y = y0
    
    # bottom pads
    for p in range(num_pads): 
        ref_pad = gdspy.CellReference( pad_cell, (x, y))
        #save location
        bot_pads_loc_array[p, :] = [x + pad.width/2, y + pad.width + wire2wire_space]
        #add reference to cell
        pad_arrays.add(ref_pad)
        x = x + pad.width + pad.spacing # update location
        
    
    # top pads
    #x = x0 + pad.width + 1 * (pad.width + pad.spacing)
    x = x0 + total_LCs_x_gap - (num_pads - 1) *(pad.width + pad.spacing)
    y = y0 + total_LCs_y_gap + 2 * pad.width # when pad rotates, it needs an extra y offset
    
    for p in range(num_pads):
        ref_pad = gdspy.CellReference(pad_cell, (x, y), rotation = 180 )
        #save location
        top_pads_loc_array[p, :] = [x - pad.width/2, y - pad.width - wire2wire_space ]
        #add reference to cell
        pad_arrays.add(ref_pad)
        x = x + pad.width + pad.spacing # update location
        
    
    ref_pads = gdspy.CellReference( pad_arrays,  (x0, y0) ) # reference to the pad arrays
    return ref_pads, top_pads_loc_array, bot_pads_loc_array