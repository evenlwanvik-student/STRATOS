import json
import os

# open template
template_path = "templates/colorgrid.json"
with open(template_path, "r") as template:
    data = json.load(template)

# start writing to output geojson file, remove if exists
output_path = "outputs/grid.json"
if os.path.isfile(output_path):
    os.remove(output_path)
with open(output_path, "w") as output:  
    data['features'][0]['geometry']['coordinates'][0][0][0] = 0
    json.dump(data, output, indent=4)

