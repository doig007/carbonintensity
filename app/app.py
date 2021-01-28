from datetime import date, time, datetime
import xml.etree.ElementTree as ET
import pandas as pd
import requests
from flask import Flask
from flask_restful import Resource, Api, reqparse
import os


elexonAPIKey = os.environ.get('elexonAPIKey')
elexonVersionNo = 'v1'
APIServiceType = 'XML'

fuelTypes = ['CCGT','OCGT','OIL','COAL','NUCLEAR','WIND',
             'PS','NPSHYD','OTHER','INTFR','INTIRL','INTNED',
             'INTEW','BIOMASS','INTNEM','INTIFA2','INTNSL']

# Provisional definitions of carbon intensity by generation fuel type (gCO2/kWh) [source: Rogers & Parson, GridCarbon (2019)]
carbonIntensityData = [['CCGT',394],['OCGT',651],['OIL',935],['COAL',937],
                       ['NUCLEAR',0],['WIND',0],['PS',0],['NPSHYD',0],['OTHER',300],
                       ['INTFR',48],['INTIRL',426],['INTNED',513],
                       ['INTEW',426],['BIOMASS',120],['INTNEM',132],
                       ['INTIFA2',48],['INTNSL',0]]                      
carbonIntensity = pd.DataFrame(carbonIntensityData,columns=['FuelType','CarbonIntensity'])

# Elexon API input URL [BMRS-API-Data-Push-User-Guide.pdf]
elexonURL = 'https://api.bmreports.com/BMRS/FUELINSTHHCUR/' + elexonVersionNo + '?APIKey=' + elexonAPIKey

app = Flask(__name__)
api = Api(app)

class CarbonIntensity():
    def get(self):
        # Call Elexon API and parse response into XML tree
        rawdata = requests.get(url=elexonURL,timeout=20).text
        root = ET.fromstring(rawdata)

        # Extract generation figures from XML tree
        responseCode = int(root[0][1].text)
        
        if responseCode != 200:
            return {'data': 'Error reaching current generation data'}, 200
        else:
            currentTotalMW = int(root[2][0][0].text)
            currentTotalPercentag = float(root[2][0][1].text)
            lastHalfHourTotalMW = int(root[2][0][2].text)

            currentMW = []

            for child in root[2][1]:
                currentMW.append(int(child[2].text))

            df = pd.DataFrame({'FuelType': fuelTypes, 'CurrentMW': currentMW})

            # Map carbon intensities onto generation figures by fuel type
            df = df.merge(carbonIntensity, left_on='FuelType', right_on='FuelType')

            df['CarbonEmissions'] = df.CurrentMW * df.CarbonIntensity
            df['CurrentPC'] = round(df.CurrentMW / df.CurrentMW.sum() * 100,1)

            averageCarbonIntensity = df.CarbonEmissions.sum() / df.CurrentMW.sum()


            returndata = {'averageCarbonIntensity':averageCarbonIntensity}
            
            return {'response': returndata}, 200


api.add_resource(CarbonIntensity, '/carbon')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
