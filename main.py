import numpy as np
import pandas
import pandas as pd
import xarray as xr
from urllib.request import urlopen
import re
import os
import sys

if len(sys.argv) > 1 and os.path.exists(sys.argv[1]): #Make sure an input file was given
    csv = pd.read_csv('template.csv') #Read template
    fr24 = pd.read_csv(sys.argv[1]) #Read input file

    url = f'https://registry.faa.gov/AircraftInquiry/Search/NNumberResult?nNumberTxt={fr24["Callsign"][2][1:]}' #Set link to FAA website for tail number
    page = urlopen(url) #Open FAA website
    html_bytes = page.read() #Read html from website
    html = html_bytes.decode("utf-8") #Decode html to UTF-8
    start_index = html.find('"Model">') #Find model
    end_index = html.find('<td data-label="">Expiration Date</td>') #End of model
    output_list = re.split('<|>| ', html[start_index:end_index]) #Split on characters
    output_list = [s for s in output_list if s]  # remove empty strings
    airframe = 'airframe_name="UNKNOWN"' #Create airframe type variable
    if len(output_list) > 1: #Make sure tail number was valid
        airframe = f'airframe_name="{output_list[1]}"' #Set type
    csv.rename(columns={f'airframe_name="Cessna 172SP"': f'{airframe}'}, inplace=True) #Rename column from template

    columns = csv.columns #Get columns
    tempDF = pd.DataFrame(np.nan, index=pd.RangeIndex((len(fr24['UTC']))-1), columns=csv.columns) #Create temp dataframe
    csv = pandas.concat([csv, tempDF]) #Add to original dataframe
    csv.reset_index(drop=True, inplace=True) #Reset index

    i = 2
    while i <= (len(fr24['UTC'])):
        tempstring = fr24['UTC'][i-2].split('T') #Get datetime data
        tempstring[1] = tempstring[1][:-1] #Remove last character from time
        csv['#airframe_info'][i] = str(tempstring[0]) #Add date
        csv['log_version="1.00"'][i] = str(tempstring[1]) #Add time
        csv[airframe][i] = '+00:00' #Add local to UTC conversion (always 0 right now)

        tempstring2 = fr24['Position'][i-2].split(',') #Get lat/lon
        csv['unit_software_version="12.03"'][i] = str(tempstring2[0]) #Set lat
        csv['system_software_part_number="006-B0563-26"'][i] = str(tempstring2[1]) #Set lon
        csv['Unnamed: 8'][i] = fr24['Altitude'][i-2] #Set altitude
        csv['Unnamed: 11'][i] = fr24['Speed'][i-2] #Set ground speed
        csv['Unnamed: 18'][i] = fr24['Direction'][i-2] #Set direction

        i+=1

    i = 8
    while i <= 69: #Clear Pandas formatting error with blank inputs
        csv.rename(columns={f'Unnamed: {i}': ''}, inplace=True)
        i+=1

    csv.set_index('#airframe_info', inplace=True) #Reset index to fit foreflight formatting
    csv.to_csv(f'{fr24["Callsign"][2]}{fr24["UTC"][1]}.csv') #Save new CSV
    print(f'Saved {fr24["Callsign"][2]}{fr24["UTC"][1]}.csv') #Print success

else:
    print(f'ERROR, that is not a valid file') #Error if there was no valid file