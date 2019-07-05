import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors
import numpy as np
import xarray as xr
from copy import deepcopy
import zarr
import logging
'''
For now this module only converts temperature, but the road to making it
dynamic and able to convert any unit to color indicators shouldn't be to rough.

    We have:
    * some value/rgb/hexa conversion functions
    * Ways for plotting a given range of RGB values

Original start and finish hexa values: start_hex="#012d6b", finish_hex="#ff5519".
The spectrum is displayed in "color_range.png".

Possible changes:
    - Hardcode a decided range, both for temperature and color
    - Find a better (more desired) color range, maybe find a 
        new algorithm for conversion?
'''


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')



# Declaring global varibles for color spectrum
START_SPECTRUM =  "#a7eed7" # Hot color
END_SPECTRUM = "#005ad8"    # Cold color
N = 10                      # Number of colors in between
# New global min/max values is found whenever new dataset is requested
MEAS_MAX = 281              
MEAS_MIN = 275


#-------------- value <-> RGB <-> hexadecimal --------------
def hex_to_RGB(hex):
    ''' "#FFFFFF" -> [255,255,255] '''
    # Pass 16 to the integer function for change of base
    return [int(hex[i:i+2], 16) for i in range(1,6,2)]


def RGB_to_hex(RGB):
    ''' [255,255,255] -> "#FFFFFF" '''
    # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "#"+"".join(["0{0:x}".format(v) if v < 16 else
                "{0:x}".format(v) for v in RGB])


def rgb_spectrum(start_hex=START_SPECTRUM, finish_hex=END_SPECTRUM, n=N):
    ''' returns a list of (n) colors between
        two hex colors. start_hex and finish_hex
        should be the full six-digit color string,
        inlcuding the number sign ("#FFFFFF") '''
    # Starting and ending colors in RGB form
    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)
    # Initilize a list of the output colors with the starting color
    RGB_list = [s]
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [int(s[j] + (float(t)/(n-1))*(f[j]-s[j])) 
                            for j in range(3)]
        # Add it to our list of output colors
        RGB_list.append(curr_vector)

    return RGB_list


def temp_to_rgb(T, start_hex=START_SPECTRUM, finish_hex=END_SPECTRUM, n=N):
    ''' performs a conversion of the input temperature in kelvin
        to a six-digit rgb color string '''
    if (T < meas_min) or (T > meas_max):
        print("'T' is outside of boundary: T_min < T < T_max")
        RGB_hex = RGB_to_hex((0,0,0))
    else:
        s = hex_to_RGB(start_hex)
        f = hex_to_RGB(finish_hex)

        # 0-100% for using RGB conversion algorithm
        T_percent = (float(T-meas_min)/(meas_max-meas_min))*100
        # find RGB value and create generator
        RGB = (int(s[i] + (T_percent/100)*(f[i]-s[i])) for i in range(3))
        
        RGB_hex = RGB_to_hex(list(RGB))
        return RGB_hex


#-------------- plotting colorspectrum --------------


def colormap(rgb): 
    ''' takes a list of rgb tuples and plots a color map '''
    # convert to np array [[]]
    colors = np.array(rgb)  
    # normalize rgb tuples (0-1)
    rgbnorm = colors/255.
    # create colormap
    my_cmap = mplcolors.ListedColormap(rgbnorm)
    plt.title('Color map')
    plt.pcolormesh(np.arange(my_cmap.N).reshape(1, -1), cmap=my_cmap)
    plt.gca().yaxis.set_visible(False)
    plt.gca().set_xlim(0, my_cmap.N)
    plt.show()

def plot_colormap(start_hex=START_SPECTRUM, finish_hex=END_SPECTRUM, n=N):
    ''' simple wrapper for getting spectrum and plotting it '''
    rgb_list = rgb_spectrum(start_hex, finish_hex, n)
    colormap(rgb_list)


#-------------- initialization stuff --------------

# hardcoded for now
# The netCDF file is available because volume is used to mount the fileto the container
# used the folllowing command in terminal: docker run -it -p 5000:5000 -v %cd%:/app -v C:\Users\marias\Documents\NetCDF_data:/data stratos /bin/bash
source_path = "/data/samples_NSEW_2013.03.11.nc"

# global variable for min/max measurement value, probably going to change this
def set_colormap_range():
    ''' simply finds the lowest and highest measured value in the 
        dataset and sets the globals for future color encodings of the same
        dataset '''
    global meas_max
    global meas_min
    
    #with xr.open_dataset(source_path) as source:
    #    temps = deepcopy(source['temperature'])
    #ZARR_PATH       = 'zarr_test/data/chunked.zarr'
    #source = zarr.open(ZARR_PATH, 'r')
    meas_min = 276
    #meas_min = float(source['temperature'].min())
    logging.info("::::: minimum measurement found: %f", meas_min)
    #meas_max = float(source['temperature'].max())
    meas_max = 282
    logging.info("::::: maximum measurement found: %f", meas_max)


# just set it when module is imported for now
set_colormap_range()
