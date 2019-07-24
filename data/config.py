''' Pythonic configuration file '''

color_enc = {
    "_comment": "holds the range for each measurement type and is used to create the colormap. The ranges were found by min/max operations on the whole 3 to 4-D array.",
    "hexa_range": {
        "_comment": "hot to cold color encoding and the resolution (nColors)",
        "hot": "#a7eed7",
        "cold": "#005ad8",
        "nColors": 100
    },
    "Franfjorden32m": {
        "temperature": {
            "min": 268,
            "max": 295      
        },
        "salinity": {
            "min": 14,
            "max": 36
        },
        "u_east": "", 
        "v_north": "", 
        "w_east": "", 
        "w_north": "",
        "w_velocity": ""
    },
    "norsok": {
        "temperature": {
            "min": 271,
            "max": 285
        },
        "salinity": {
            "min": 11.00,
            "max": 38.00
        }
    },
    "OSCAR": {
    }
}