import gdspy
    
def main():
    
    directory = 'C:/Users/nicol/Documents/00 - Research/L-Edit/Resonator Project/100 mux/output/'
    filename = 'Wafer_6in.gds'
    fileoutput = directory + filename
    view = 1
    
    # CREATE GDS LIBRARY
    lib = gdspy.GdsLibrary()
    
    # CREATE LAYERS
    GPLayer = {"layer": 1, "datatype": 1}
    
    #Create cells
    wafer_cell = lib.new_cell("Wafer")
    
    circle_cell = lib.new_cell("Circle_6in")
    
    chip1_cell = lib.new_cell("chip1")
    chip2_cell = lib.new_cell("chip2")
    chip3_cell = lib.new_cell("chip3")
    chip4_cell = lib.new_cell("chip4")
    
    #Create circle
    line_width = 10
    Radius_microns = 6/2 * 2.54/100 * 1e6 
    print("radius:  ", Radius_microns, " um" )
    circle = gdspy.Round((0, 0), Radius_microns + line_width, tolerance = 1, inner_radius = Radius_microns, **GPLayer)
    circle_cell.add(circle)
    
    #Create chips  
    space_between_chips = 0.25e3  
    l1 = 44300
    l2 = l1
    l3 = l1
    l4 = l2   
    
    w1 = 28850
    w2 = w1
    w3 = w1
    w4 = w2
    
    rectangle1 = gdspy.Rectangle( (0, 0), ( w1, l1), **GPLayer)
    rectangle2 = gdspy.Rectangle( (0, 0), ( w2, l2), **GPLayer)
    rectangle3 = gdspy.Rectangle( (0, 0), ( w3, l3), **GPLayer)
    rectangle4 = gdspy.Rectangle( (0, 0), ( w4, l4), **GPLayer)
    
    chip1_cell.add(rectangle1)
    chip2_cell.add(rectangle2)
    chip3_cell.add(rectangle3)
    chip4_cell.add(rectangle4)
    
    ref_chip1 = gdspy.CellReference( chip1_cell, (space_between_chips + 0, space_between_chips/2) ) 
    ref_chip2 = gdspy.CellReference( chip2_cell, (w1 + space_between_chips , space_between_chips/2) ) 
    ref_chip3 = gdspy.CellReference( chip3_cell, ( - w3 -space_between_chips , space_between_chips/2) )
    ref_chip4 = gdspy.CellReference( chip4_cell, ( - w3 - 2* space_between_chips - w4 , space_between_chips/2 ) )
    
    
    # Add everything to main cell
    wafer_cell.add( [ref_chip1, ref_chip2, ref_chip3, ref_chip4, circle] )
    
    # ---------- END OF PROGRAM -----------------
    #Save the library in a file called 'first.gds'
    lib.write_gds(fileoutput)
    if view == 1:
        #Display all cells using the internal viewer.
        gdspy.LayoutViewer()
    print("The end!")

if __name__ == "__main__":
    main()
    