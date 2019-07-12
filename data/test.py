import numpy as np

extrema_dict = {'min': np.nan, 'max': np.nan}

array = [np.nan, np.nan, np.nan, np.nan]

print np.nanmin(array)


'''
if any(np.isnan(val) for val in extrema_dict.values()):
    print "hello"

'''