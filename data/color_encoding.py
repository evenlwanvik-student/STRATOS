import math
import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors
import numpy as np


'''
For now this module only converts temperature, but the road to making it
dynamic and able to convert any unit to color indicators shouldn't be to rough.

    We have:
    * some value/rgb/hexa conversion functions
    * Ways for plotting a given range of RGB values

Original start and finish hexa values: start_hex="#4bf0dc", finish_hex="#ff5519".
The spectrum is displayed in "color_range.png".

Possible changes:
    - Hardcode a decided range, both for temperature and color
    - Find a better (more desired) color range, maybe find a 
        new algorithm for conversion?
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


def rgb_spectrum(start_hex="#4bf0dc", finish_hex="#ff5519", n=100):
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


def temp_to_rgb(T, T_min=250, T_max=320, start_hex="#4bf0dc", finish_hex="#ff5519", n=100):
    ''' performs a conversion of the input temperature in kelvin
        to a six-digit rgb color string '''
    if (T < T_min) or (T > T_max):
        raise ValueError("'T' is outside of boundary: T_min < T < T_max")
    else:
        s = hex_to_RGB(start_hex)
        f = hex_to_RGB(finish_hex)

        # 0-100% for using RGB conversion algorithm
        T_percent = (float(T-T_min)/(T_max-T_min))*100
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

def plot_colormap(start_hex="#4bf0dc", finish_hex="#ff5519", n=100):
    ''' simple wrapper for getting spectrum and plotting it '''
    rgb_list = rgb_spectrum(start_hex, finish_hex, n)
    colormap(rgb_list)



