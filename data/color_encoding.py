import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors
import numpy as np
import xarray as xr
from copy import deepcopy
import logging

import config
#from .. import config

#-------------- initialization --------------

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.WARNING,
    datefmt='%Y-%m-%d %H:%M:%S')


'''
old rgb values:
    "hot": "#a7eed7",
    "cold": "#005ad8",
'''

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


def rgb_spectrum():
    ''' returns a list of (n) colors between
        two hex colors. start_hex and finish_hex
        should be the full six-digit color string,
        inlcuding the number sign ("#FFFFFF") '''
    # Starting and ending colors in RGB form
    # start (s) and finish (f) hexa range for color map
    if color_range == 'temperature_range':
        s = hex_to_RGB(config.color_enc['temperature_range']['hot'])
        f = hex_to_RGB(config.color_enc['temperature_range']['cold'])
        n = config.color_enc['temperature_range']['nColors']
    else:
        s = hex_to_RGB(config.color_enc['oscar_range']['hot'])
        f = hex_to_RGB(config.color_enc['oscar_range']['cold'])
        n = config.color_enc['oscar_range']['nColors']
    # Initialize a list of the output colors with the starting color
    RGB_list = [s]
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [int(s[j] + (float(t)/(n-1))*(f[j]-s[j])) 
                            for j in range(3)]
        # Add it to our list of output colors
        RGB_list.append(curr_vector)

    return RGB_list


def temp_to_rgb(val, val_type, dataset):
    ''' performs a conversion of the input temperature in kelvin to a six-digit 
    rgb color string. The range is fetched from config.json, value is saturated if outside
    of range. The warning should be an indicator of that the range should be adjusted
    
    Parameters
    ----------
    val : float
        the depth of the grid to be computed
    val_type : string
        what type of measurement, e.g. 'temperature', 'concentration', etc 
    dataset : string
        name of the current dataset
    '''
    
    val_min = config.color_enc[dataset][val_type]['min']
    val_max = config.color_enc[dataset][val_type]['max']

    if (val < val_min) or (val > val_max):
        logging.warning(f"val: {val} is outside of boundary: val_min: {val_min} & val_max: {val_max}")
        # saturate the measurement value
        if (val < val_min): val = val_min
        else:               val = val_max 

    # start (s) and finish (f) hexa range for color map
    if val_type == 'temperature':
        s = hex_to_RGB(config.color_enc['temperature_range']['hot'])
        f = hex_to_RGB(config.color_enc['temperature_range']['cold'])
        n = config.color_enc['temperature_range']['nColors']
    else:
        s = hex_to_RGB(config.color_enc['oscar_range']['hot'])
        f = hex_to_RGB(config.color_enc['oscar_range']['cold'])
        n = config.color_enc['oscar_range']['nColors']

    # 0-100% for using RGB conversion algorithm
    val_percent = (float(val-val_min)/(val_max-val_min))*100
    # find RGB value and create generator
    RGB = (int(s[i] + (val_percent/100)*(f[i]-s[i])) for i in range(3))
    
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

def plot_colormap():
    ''' simple wrapper for getting spectrum and plotting it '''
    rgb_list = rgb_spectrum()
    colormap(rgb_list)
