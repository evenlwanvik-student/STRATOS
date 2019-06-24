import math
import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors
import numpy as np

# default range is from about 60 to 100 degrees celcius
def kelvin2rgb(temp, min=220, max=375):

    temp = temp/100
    #  calc red 
    if temp <= 66:
        r = 255
    else:
        # Note: the R-squared value for this approximation is .988
        tmpCalc = temp - 60
        r = 329.698727446 * (tmpCalc ** -0.1332047592)   
        if r < 0:   r = 0
        if r > 255: r = 255
    
    # calc green
    if temp <= 66:      
        # Note: the R-squared value for this approximation is .996
        tmpCalc = temp
        g = 99.4708025861 * math.log(tmpCalc ) - 161.1195681661
        if g < 0:   g = 0
        if g > 255: g = 255
    else:
        # Note: the R-squared value for this approximation is .987
        tmpCalc  = temp - 60
        g = 288.1221695283 * (tmpCalc  ** -0.0755148492)
        if g < 0:   g = 0
        if g > 255: g = 255
    
    # blue
    print temp
    if temp >= 66:
        b = 255
    else:
        if temp <= 19:
            b = 0
        # Note: the R-squared value for this approximation is .998
        else: 
            tmpCalc = temp - 10
            b = 138.5177312231 * math.log(tmpCalc) - 305.0447927307
            if b < 0:   g = 0
            if b > 255: g = 255

    return (int(r),int(g),int(b))

# todo: change this name
# create a color map depending on a given range (min-max) and resolution (n)
def generate_colors(min=220, max=400, n=100):
    resolution = int(max-min)/n
    rgb = []
    if not isinstance(resolution, int):
        raise ValueError("The resolution (max-min/n) must be an integer")
    for tempGradient in range(min,max,resolution):
        rgb.append( kelvin2rgb(min + tempGradient) )
    return rgb

# takes a list of rgb tuples and plots a color map
def colormap(rgb): 
    colors = np.array(rgb)  # convert to np array [[]]
    rgbnorm = colors/255.   # normalize rgb tuples (0-1)
    my_cmap = mplcolors.ListedColormap(rgbnorm)
    plt.title('Color map')
    plt.pcolormesh(np.arange(my_cmap.N).reshape(1, -1), cmap=my_cmap)
    plt.gca().yaxis.set_visible(False)
    plt.gca().set_xlim(0, my_cmap.N)
    plt.show()

#rgb = generate_colors(220,400,100)
#colormap(rgb)


# ------------- maybe a better method? ------------- 

def normalize_input(min=220, max=400, n=100):
    ''' Converts a unit of choice into a value between 0-1 to be used when
      encoding a color between a given hexadecimal range later '''
    gradient = (max - min) / n
    if not isinstance(gradient, int):
        raise ValueError("The resolution (max-min/n) must be an integer")
    else: 
        return gradient


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


def color_dict(RGB_list):
  ''' Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on '''
  return {"hex":[RGB_to_hex(RGB) for RGB in RGB_list],
      "r":[RGB[0] for RGB in RGB_list],
      "g":[RGB[1] for RGB in RGB_list],
      "b":[RGB[2] for RGB in RGB_list]}


def unit_to_rgb():
  ''' performs a conversion of a single given unit of choice
      to a six-digit rgb color string
      Not implemented.. yet? '''  
  return RGB

def temp_to_rgb(T, start_hex="#4682B4", finish_hex="#FFB347", n=100):
  ''' performs a conversion of the input temperature in kelvin
      to a six-digit rgb color string '''
  T0 = hex_to_RGB(start_hex)
  T1 = hex_to_RGB(finish_hex)
  print T0
  print T1
  
  #RGB = T0[0] + float(T)/(n-1)#(T1[0]-T0[0])
  #x =     ((T0[i] + float(T)/(n-1)(T1[i]-T0[i])) for i in range(3))
  RGB = ((T0[i] + (float(T)/(n-1))*(T1[i]-T0[i])) for i in range(3))
  print list(RGB)
  return RGB_to_hex(RGB)

def rgb_spectrum(start_hex="#4682B4", finish_hex="#FFB347", n=100):
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
    curr_vector = [
      int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
      for j in range(3)
    ]
    # Add it to our list of output colors
    RGB_list.append(curr_vector)

  print color_dict(RGB_list)
  return RGB_list

#gradient = calc_gradient()
#x = rgb_spectrum("#4682B4", "#FFB347")
#colormap(x)
print temp_to_rgb(273)
