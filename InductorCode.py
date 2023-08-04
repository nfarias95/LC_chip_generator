# This is the LC Library Code
import gdspy
import numpy
   
# --------------------------------------------------
#               Generate Inductor
# --------------------------------------------------


def GenerateInductorCell( lib, GPLayer, TopLayer, OxideLayer, via_pad_width, L, tolerance ):
    #this function generates an inductor cell    

    inductor_cell = lib.new_cell("Inductor")
    
    pitch = L.line_width + L.gap_width
    L_pad_gap = via_pad_width/2 + pitch #offset to create via
    
    for i in range(L.num_turns):
        # Draw Left Side
        x1 = (i*pitch)
        x2 = (i * pitch + L.line_width)
        y1 = (i* pitch)
        y2 = (L.outer_diameter - i*pitch)
        left = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
        inductor_cell.add(left)
        
        #Draw top side
        x1 = L.line_width + i * pitch
        x2 = L.outer_diameter - i * pitch
        y1 = (L.outer_diameter - L.line_width - i * pitch)
        y2 = (L.outer_diameter - i * pitch)
        top = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
        inductor_cell.add(top)
        
        #Draw Right Side
        x1 = L.outer_diameter - L.line_width - i * pitch
        x2 = L.outer_diameter - i*pitch
        y1 = (L.gap_width + i* pitch)
        y2 = (L.outer_diameter - L.line_width - i * pitch)
        right = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
        inductor_cell.add(right)
        
        #Draw Bottom side
        x1 = (i+1)*pitch
        x2 = L.outer_diameter - L.line_width - i*pitch
        y1 = (L.gap_width + i*pitch)
        y2 = ( (i+1) * pitch)
        bottom = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
        inductor_cell.add(bottom)
        
    # Draw Wiring out of inductor
    i = i + 1
    
       
    # IF NUMBER OF LAYERS TO BE ETCHED IS 3, CREATE VIAS:    
    if L.num_layers == 3:
        #Draw Vertical strip
        x1 = i*pitch
        x2 = i*pitch + L.line_width
        y1 = (i*pitch)
        y2 = ( ( L.outer_diameter - L.line_width - i*pitch) - L_pad_gap )
        up = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
        inductor_cell.add(up)
        #Draw Small horizaontal strip
        x1 = i*pitch
        x2 = i*pitch + 5 * L.line_width
        y1 = ( (L.outer_diameter - L.line_width - i* pitch) - L_pad_gap)
        y2 = (( L.outer_diameter - L.line_width - i*pitch) - L_pad_gap + L.line_width)
        hor = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
        inductor_cell.add(hor) 
        # DRAW VIA PADS
        x1 = i*pitch + 5 * L.line_width
        x2 = x1 + via_pad_width
        y1 = ( (L.outer_diameter - L.line_width - i*pitch) - L_pad_gap + L.line_width/2 - via_pad_width/2) 
        y2 = y1 + via_pad_width
        gp_pad = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
        top_pad = gdspy.Rectangle( (x1, y1), (x2, y2), **TopLayer) 
        inductor_cell.add(gp_pad)    
        inductor_cell.add(top_pad)    
        # OXIDE LAYER (NEGATIVE!)
        x1_d = x1 + tolerance
        x2_d = x2 - tolerance
        y1_d = y1 + (tolerance)
        y2_d = y2 + (-tolerance)
        hole = gdspy.Rectangle( (x1_d, y1_d), (x2_d, y2_d), **OxideLayer) 
        inductor_cell.add(hole) 
        # DRAW WIRE ON TOP LAYER
        x1_w =  ( ( i*pitch + 5 * L.line_width + ( i*pitch + 5 * L.line_width + via_pad_width ) ) /2 - L.line_width/2 )
        x2_w = x1_w + L.line_width
        y1_w = (y2)
        y2_w =  ( L.outer_diameter)
        wire = gdspy.Rectangle( (x1_w, y1_w), (x2_w, y2_w), **TopLayer)
        inductor_cell.add(wire)
        
    elif L.num_layers == 1: # only one layer, needs to wire bond.
        # create wire_bonding pad in middle and outside of inductor
        # bring left side halfway up
        x1 = i*pitch
        y1 = i*pitch
        x2 = i*pitch + L.line_width
        y2 = (L.outer_diameter - 1.5 * i * pitch)
        up = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer) 
        #draw inside pad
        x1 = i*pitch
        x2 = L.outer_diameter - L.line_width - i*pitch + pitch/2
        y1 = L.outer_diameter - 1.5 * i* pitch
        y2 = L.outer_diameter - i*pitch
        inside_pad = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer)
        #draw_outside_pad
        x1 = (L.outer_diameter - L.pad_length)/2
        x2 = x1 + L.pad_length
        y1 = L.outer_diameter + L.pad_gap
        y2 = y1 + L.pad_width
        outside_pad = gdspy.Rectangle( (x1, y1), (x2, y2), **GPLayer)
        inductor_cell.add([up, inside_pad, outside_pad])
        
        
        
        
    
    return inductor_cell