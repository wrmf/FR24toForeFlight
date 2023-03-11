import numpy as np
import pandas
import pandas as pd
import xarray as xr
from urllib.request import urlopen
import re
import os
import sys

if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    csv = pd.read_csv('template.csv')
    fr24 = pd.read_csv(sys.argv[1])

    url = f'https://registry.faa.gov/AircraftInquiry/Search/NNumberResult?nNumberTxt={fr24["Callsign"][2][1:]}'
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    start_index = html.find('"Model">')
    end_index = html.find('<td data-label="">Expiration Date</td>')

    output_list = re.split('<|>| ', html[start_index:end_index])
    output_list = [s for s in output_list if s]  # remove empty strings

    airframe = 'airframe_name="UNKNOWN"'
    if len(output_list) > 1:
        airframe = f'airframe_name="{output_list[1]}"'

    csv.rename(columns={f'airframe_name="Cessna 172SP"': f'{airframe}'}, inplace=True)

    columns = csv.columns

    tempDF = pd.DataFrame(np.nan, index=pd.RangeIndex((len(fr24['UTC']))-1), columns=csv.columns)
    csv = pandas.concat([csv, tempDF])
    csv.reset_index(drop=True, inplace=True)

    i = 2
    while i <= (len(fr24['UTC'])):
        tempstring = fr24['UTC'][i-2].split('T')
        tempstring[1] = tempstring[1][:-1]

        csv['#airframe_info'][i] = str(tempstring[0])
        csv['log_version="1.00"'][i] = str(tempstring[1])
        csv[airframe][i] = '+00:00'

        tempstring2 = fr24['Position'][i-2].split(',')
        csv['unit_software_version="12.03"'][i] = str(tempstring2[0])
        csv['system_software_part_number="006-B0563-26"'][i] = str(tempstring2[1])
        csv['Unnamed: 8'][i] = fr24['Altitude'][i-2]
        csv['Unnamed: 11'][i] = fr24['Speed'][i-2]
        csv['Unnamed: 18'][i] = fr24['Direction'][i-2]

        i+=1

    i = 8
    while i <= 69:
        csv.rename(columns={f'Unnamed: {i}': ''}, inplace=True)
        i+=1

    csv.set_index('#airframe_info', inplace=True)



    csv.to_csv(f'{fr24["Callsign"][2]}{fr24["UTC"][1]}.csv')
    print(f'Saved {fr24["Callsign"][2]}{fr24["UTC"][1]}.csv')
else:
    print(f'ERROR, that is not a valid file')