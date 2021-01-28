from datetime import date, time, datetime
import xml.etree.ElementTree as ET
import pandas as pd
import requests

APIKey = ${{ secrets.APIKey }}
VersionNo = 'v1'
APIServiceType = 'XML'

FuelTypes = ['CCGT','OCGT','OIL','COAL','NUCLEAR','WIND',
             'PS','NPSHYD','OTHER','INTFR','INTIRL','INTNED',
             'INTEW','BIOMASS','INTNEM','INTIFA2','INTNSL']

# Provisional definitions of carbon intensity by generation fuel type (gCO2/kWh) [source: Rogers & Parson, GridCarbon (2019)]
CarbonIntensityData = [['CCGT',394],['OCGT',651],['OIL',935],['COAL',937],
                       ['NUCLEAR',0],['WIND',0],['PS',0],['NPSHYD',0],['OTHER',300],
                       ['INTFR',48],['INTIRL',426],['INTNED',513],
                       ['INTEW',426],['BIOMASS',120],['INTNEM',132],
                       ['INTIFA2',48],['INTNSL',0]]                      
CarbonIntensity = pd.DataFrame(CarbonIntensityData,columns=['FuelType','CarbonIntensity'])

# Elexon API input URL [BMRS-API-Data-Push-User-Guide.pdf]
ElexonURL = 'https://api.bmreports.com/BMRS/FUELINSTHHCUR/' + VersionNo + '?APIKey=' + APIKey

# Call Elexon API and parse response into XML tree
rawdata = requests.get(url=ElexonURL).text
root = ET.fromstring(rawdata)

# Extract generation figures from XML tree
ResponseCode = root[0][1].text
currentTotalMW = int(root[2][0][0].text)
currentTotalPercentag = float(root[2][0][1].text)
lastHalfHourTotalMW = int(root[2][0][2].text)

CurrentMW = []

for child in root[2][1]:
    CurrentMW.append(int(child[2].text))

df = pd.DataFrame({'FuelType': FuelTypes, 'CurrentMW': CurrentMW})

# Map carbon intensities onto generation figures by fuel type
df = df.merge(CarbonIntensity, left_on='FuelType', right_on='FuelType')

df['CarbonEmissions'] = df.CurrentMW * df.CarbonIntensity
df['CurrentPC'] = round(df.CurrentMW / df.CurrentMW.sum() * 100,1)

AverageCarbonIntensity = df.CarbonEmissions.sum() / df.CurrentMW.sum()
