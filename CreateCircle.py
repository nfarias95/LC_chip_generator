import gdspy
    
def main():
    
    directory = 'C:/Users/nicol/Documents/00 - Research/L-Edit/Resonator Project/100 mux/output/'
    filename = 'Circle_6in.gds'
    fileoutput = directory + filename
    view = 1
    
    # CREATE GDS LIBRARY
    lib = gdspy.GdsLibrary()
    
    # CREATE LAYERS
    GPLayer = {"layer": 1, "datatype": 1}
    
    #Create cell
    circle_cell = lib.new_cell("Circle_6in")
    
    #Create circle
    line_width = 10
    Radius_microns = 6/2 * 2.54/100 * 1e6 
    
    circle = gdspy.Round((0, 0), Radius_microns + line_width, tolerance = 1, inner_radius = Radius_microns, **GPLayer)
    
    circle_cell.add(circle)
    
    
        # ---------- END OF PROGRAM -----------------
    #Save the library in a file called 'first.gds'
    lib.write_gds(fileoutput)
    if view == 1:
        #Display all cells using the internal viewer.
        gdspy.LayoutViewer()
    print("The end!")

if __name__ == "__main__":
    main()
    