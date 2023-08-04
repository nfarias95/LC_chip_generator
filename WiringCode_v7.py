
#WIRING CODE!
import gdspy
import numpy

def GetLCWiringPositions(LC, L, C, col, x0, y0 ):
    
    # inside LC cell:
    L_x = L.outer_diameter/2
    
    if (col % 2 == 0):
        # capacitor is at the bottom, connection to capacitor is on the left
        if C.type == "IDC":
            C_y =  - (LC.gap + C.height )
            C_x = C.width/2
            
        if L.type == "with_pads":
            L_y = L.outer_diameter + L.pad_width + L.pad_gap
    
    else : # capacitor is at the top
        if C.type == "IDC":
            C_y = (LC.gap + C.height )
            C_x =  - C.width/2
        
        if L.type == "with_pads":
            L_y = - (L.outer_diameter + L.pad_width + L.pad_gap)
        
    #add LC position in checkerboard
    
    C_wire_loc = [x0 + C_x, y0 + C_y]
    L_wire_loc = [x0 + L_x, y0 + L_y]
    
    return C_wire_loc, L_wire_loc

def CreateWires(lib, layer, x0, y0, CB_x0, CB_y0, wire2wire_space, TL_width, C_param_arrays, C_wire_loc_array, L_wire_loc_array, LC, L,
                 pad, num_LCs, num_LC_rows, num_LC_cols, top_pads_loc_array, bot_pads_loc_array, LC2LC_x_gap):
    
    wires_cell = lib.new_cell("Wires")
    
    num_spots = num_LC_rows * num_LC_cols
    
    C_wire_end = numpy.ones([num_spots, 2]) * (-1) # capacitors wire end location  (always do +- 1/2 TL_width from the (x, y) location)
    L_wire_end = numpy.ones([num_spots, 2]) * (-1) # same, for the inductors
    
    # FIRST, FIND WHERE THE INDUCTORS AND CAPACITORS ARE LOCATED
    
    spot = 0
    for row in range(num_LC_rows):
        
        for col in range(num_LC_cols):
            
            if ( C_wire_loc_array[spot, 1] ) != -3.14159: # check that there is a LC there
            
                # localize capacitor and inductor wiring locations
                C_x = C_wire_loc_array[spot, 0] + CB_x0
                C_y = C_wire_loc_array[spot, 1] + CB_y0
                L_x = L_wire_loc_array[spot, 0] + CB_x0
                L_y = L_wire_loc_array[spot, 1] + CB_y0
                
               
                # insert little wire for capacitor               
                y1_c = C_y
                if col % 2 == 0: # capacitor is at the bottom, connection to capacitor is on the left
                    y2_c = y1_c - wire2wire_space
                    x1_c = C_x - TL_width/2
                else: # capacitor is on top, inductor is at the bottom
                    y2_c = y1_c + wire2wire_space 
                    x1_c = C_x - TL_width/2 #- L.outer_diameter
                x2_c = x1_c + TL_width
                C_wire = gdspy.Rectangle( (x1_c, y1_c), (x2_c, y2_c), **layer)

                # insert little wire for inductor               
                y1_l = L_y
                if col % 2 == 0: # capacitor is at the bottom, connection to capacitor is on the left
                    y2_l = y1_l + wire2wire_space
                    x1_l = L_x - TL_width/2
                else: # inductor is at the bottom
                    y2_l = y1_l - wire2wire_space 
                    x1_l = L_x - TL_width/2 - L.outer_diameter
                x2_l = x1_l + TL_width
                L_wire = gdspy.Rectangle( (x1_l, y1_l), (x2_l, y2_l), **layer)               
                               
                #add wires to cell
                wires_cell.add([C_wire, L_wire])
                
                #Save wire end position for each spot
                C_wire_end[spot,:] =  [ (x1_c + x2_c)/2 , y2_c]
                L_wire_end[spot,:] = [ (x1_l + x2_l)/2 , y2_l ]
    
            #update spot
            spot = spot + 1
            
            
            
    # START WIRES FROM PADS - COULD BE IN THE SAME FOR LOOP, BUT THAT'S OK THIS WILL BE EASIER TO ORGANIZE
    
    # --------------------------------   BOTTOM PADS   ----------------------------------------------------------
    pad_counter = 0
    
    # we have to do this differently now
    for col in range(num_LC_cols):
        
        #for row in range(num_LC_rows):
        for row in range(num_LC_rows-1, -1, -1) :   
            # I am inverting rows and columns here, so the spot counting is different
            
            spot = row * num_LC_cols + col
            #print("Spot: ", spot)
            
            if ( C_wire_loc_array[spot, 1] ) != -3.14159: # check that there is a LC there
                
                LC_x_origin = L_wire_end[spot, 0] - L.outer_diameter/2 # this is correct.
                
                # BOTTOM WIRING -- goes to capacitor 
                #starting from pad, first we need to go up
                x_b_pad = x0 + bot_pads_loc_array[pad_counter, 0]
                y_b_pad = y0 + bot_pads_loc_array[pad_counter, 1]
                x1_cs = x_b_pad - 0.5 * TL_width # cs: capacitor start
                x2_cs = x1_cs + TL_width
                y1_cs = y_b_pad
                
                # wire goes up depending on which row we are at, and where the wiring gap is
                next_x2_cs =  LC_x_origin - (wire2wire_space * (num_LC_rows + 2 )) + wire2wire_space * ( num_LC_rows - row)
                if next_x2_cs < x2_cs:
                    y2_cs = y1_cs + wire2wire_space * (num_LC_rows - row + 1) # the plus 1 is so that the 1st pad wire doesn't intercept the other pads when it goes left
                else:
                    y2_cs = y1_cs + wire2wire_space * (row + 1) # the plus 1 is so that the 1st pad wire doesn't intercept the other pads when it goes left
                
                start_wire_c = gdspy.Rectangle( (x1_cs, y1_cs), (x2_cs, y2_cs), **layer)
                #add wires to cell
                wires_cell.add(start_wire_c)
                
                # -------   THEN LEFT   ------- 
                # go left all the way to inductor origin on that row - LC to LC x gap
                x1_cs = x2_cs
                y1_cs = y2_cs - TL_width
                y2_cs = y2_cs #y1_cs + TL_width
                #go back left
                x2_cs =  LC_x_origin - (wire2wire_space * (num_LC_rows + 2 )) + wire2wire_space * ( num_LC_rows - row)
                #make wire
                start_wire_c = gdspy.Rectangle( (x1_cs, y1_cs), (x2_cs, y2_cs), **layer)
                #add wires to cell
                wires_cell.add(start_wire_c)
           
           
                # --- THEN GO UP UNTIL REACHES CAPACITOR ---- 
                x1_cs = x2_cs
                x2_cs = x1_cs + TL_width
                y1_cs = y1_cs
                
                y2_cs = C_wire_end[spot, 1]
                #make wire
                start_wire_c = gdspy.Rectangle( (x1_cs, y1_cs), (x2_cs, y2_cs), **layer)
                #add wires to cell
                wires_cell.add(start_wire_c)

                # --------- FINALLY, GO RIGHT UNTIL WEE REACH THE CAPACITOR WIRE
                x1_cs = x1_cs
                x2_cs = C_wire_end[spot, 0] + TL_width/2
                y1_cs = y2_cs
                y2_cs = y1_cs + TL_width
                #make wire
                wire_c = gdspy.Rectangle( (x1_cs, y1_cs), (x2_cs, y2_cs), **layer)
                #add wires to cell
                wires_cell.add(wire_c)
                
           
                #UPDATE PAD COUNTER 
                pad_counter = pad_counter + 1
    
    
    
    
    # -----------------------------------
    # TOP WIRING FOR INDUCTOR
    # -----------------------------------
    pad_counter = 0
    
    for col in range(num_LC_cols):
        
        for row in range(num_LC_rows-1, -1, -1) :  
            
            # I am inverting rows and columns here, so the spot counting is different
            spot = row * num_LC_cols + col
            
            if ( C_wire_loc_array[spot, 1] ) != -3.14159: # check that there is a LC there            
                LC_x_origin = L_wire_end[spot, 0] + L.outer_diameter/2 # this is correct.
                
                # TOP WIRING -- goes to inductor
                #starting from pad, just go down
                x_t_pad = x0 + top_pads_loc_array[pad_counter, 0]
                y_t_pad = y0 + top_pads_loc_array[pad_counter, 1]
                x1_ls = x_t_pad - 0.5 * TL_width # ls: inductor wiring start
                x2_ls = x1_ls + TL_width
                y1_ls = y_t_pad
                #wire goes down by amount that depends on the row and location of inductor
                next_x2_l2 = LC_x_origin + (wire2wire_space * (num_LC_rows + 2 )) + wire2wire_space * ( num_LC_rows -  row) #how far it will go in the future
                if (next_x2_l2 > x2_ls):
                    y2_ls = y1_ls - wire2wire_space * ( row + 1)
                else:
                    y2_ls = y1_ls - wire2wire_space * (num_LC_rows - row + 1)    
                
                start_wire_l = gdspy.Rectangle( (x1_ls, y1_ls), (x2_ls, y2_ls), **layer)
                #add wires to cell
                wires_cell.add(start_wire_l)
                
                # THEN GO RIGHT            
                # go right all the way to inductor end on that row - ( LC to LC x gap)
                x1_ls = x2_ls
                y1_ls = y2_ls
                y2_ls = y1_ls + TL_width
                x2_ls =  LC_x_origin + (wire2wire_space * (num_LC_rows + 2 )) + wire2wire_space * ( num_LC_rows -  row)
                #make wire
                start_wire_l = gdspy.Rectangle( (x1_ls, y1_ls), (x2_ls, y2_ls), **layer)
                #add wires to cell
                wires_cell.add(start_wire_l)
                
                # THEN GO DOWN UNTIL WE REACH INDUCTOR
                x1_ls = x2_ls
                x2_ls = x1_ls + TL_width
                y1_ls = y2_ls       
                y2_ls = L_wire_end[spot, 1]
                #make wire
                start_wire_l = gdspy.Rectangle( (x1_ls, y1_ls), (x2_ls, y2_ls), **layer)
                #add wires to cell
                wires_cell.add(start_wire_l)
                
                # FINALLY, GO LEFT
                x1_ls = x2_ls
                x2_ls = L_wire_end[spot, 0] - TL_width/2
                y1_ls = y2_ls
                y2_ls = y1_ls + TL_width
                #make wire
                wire_l = gdspy.Rectangle( (x1_ls, y1_ls), (x2_ls, y2_ls), **layer)
                #add wires to cell
                wires_cell.add(wire_l)                
                
                
                #UPDATE PAD COUNTER 
                pad_counter = pad_counter + 1
    
    
    return wires_cell