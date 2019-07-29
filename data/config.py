''' Pythonic configuration file '''
import numpy as np 

fill_values = (np.nan, -32768, 3.0000000054977558e+38)

color_enc = {
    "_comment": "holds the range for each measurement type and is used to create the colormap. The ranges were found by min/max operations on the whole 3 to 4-D array.",
    "hexa_range": {
        "_comment": "hot to cold color encoding and the resolution (nColors)",
        "hot": "#ffff2d",
        "cold": "#ef3c42",
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
        "u_east": {
            "min": -6,
            "max": 6
        },
        "v_north": {
            "min": -6,
            "max": 6
        }
        "w_east": "", 
        "w_north": "-10",
        "w_velocity": ""
    },
    "norsok": {
        "temperature": {
            "min": 20000,
            "max": 30000
        },

        "salinity": {
            "min": -25000,
            "max": -9000
        },


        "u_east": "", 
        "v_north": "",  
        "w_east": "", 
        "w_north": "",
        "w_velocity": ""
    },
    "OSCAR": {
        "comment": "only values from the zarr blob TEST3MEMWX.XNordlandVI_surface.zarr",
        "concentration": {
            "min": 0.0,
            "max": 20000.0
        },
        "total_concentration": {
            "min": 0.0,
            "max": 4000.0
        },
        "cell_coverage": {
            "min": 0.0,
            "max": 4000.0
        },
        "dispersability": {
            "min": 0.0,
            "max": 1.0
        },
        "emulsion_viscosity": {
            "min": 290.0,
            "max": 2000000.0
        },
        "flashpoint": {
            "min": 50.0,
            "max": 54.0
        },
        "pourpoint": {
            "min": 0.0,
            "max": 95.0
        },
        "surface_avg_coverage_distribution_by_thickness": {
            "min": 0.0,
            "max": 100.0
        },
        "surface_avg_flashpoint_distribution_by_thickness": {
            "min": 0.0,
            "max": 100.0
        },
        "surface_avg_asphaltene_fraction_distribution_by_thickness": {
            "min": -0.02,
            "max": 0.0
        },
        "surface_avg_viscosity_distribution_by_thickness": {
            "min": 0.0,
            "max": 2000000.0
        },
        "surface_avg_water_content_distribution_by_thickness": {
            "min": 0.0,
            "max": 100.0
        },
        "surface_avg_wax_fraction_distribution_by_thickness": {
            "min": -0.02,
            "max": 0.0
        },
        "surface_mass_distribution_by_thickness": {
            "min": 0.0,
            "max": 1.0
        },
        "surface_oil_thickness": {
            "min": 0.0,
            "max": 800
        },
        "water_content": {
            "min": 0.0,
            "max": 100.0
        },
        "wax_fraction": {
            "comment": "this one originally gave 0.0 for both min and max",
            "min": 0.0,
            "max": 1.0
        }
    }
}

