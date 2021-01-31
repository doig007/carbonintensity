from datetime import date, time, datetime
import time as t
import xml.etree.ElementTree as ET
import pandas as pd
import requests
import json
from flask import Flask
from flask_restful import Resource, Api, reqparse
import os
from sqlalchemy import create_engine
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

elexonAPIKey = os.environ.get('carbonintensity_elexonAPIKey')
elexonVersionNo = 'v1'
APIServiceType = 'XML'
elexonUpdateFrequency = 5 # number of minutes between updates for FUELINSTHHCUR series
elexonWaitTime = 75 # number of seconds to wait after each period for Elexon backend to update

fuelTypes = ['CCGT','OCGT','OIL','COAL','NUCLEAR','WIND',
             'PS','NPSHYD','OTHER','INTFR','INTIRL','INTNED',
             'INTEW','BIOMASS','INTNEM','INTIFA2','INTNSL']

# Provisional definitions of carbon intensity by generation fuel type (gCO2/kWh) [source: Rogers & Parson, GridCarbon (2019)]
carbonIntensityData = [['CCGT',394],['OCGT',651],['OIL',935],['COAL',937],
                       ['NUCLEAR',0],['WIND',0],['PS',0],['NPSHYD',0],['OTHER',300],
                       ['INTFR',48],['INTIRL',426],['INTNED',513],
                       ['INTEW',426],['BIOMASS',120],['INTNEM',132],
                       ['INTIFA2',48],['INTNSL',0]]                      
carbonIntensity = pd.DataFrame(carbonIntensityData,columns=['fuelType','carbonIntensity'])

# Elexon API input URL [BMRS-API-Data-Push-User-Guide.pdf]
elexonURL = 'https://api.bmreports.com/BMRS/FUELINSTHHCUR/' + elexonVersionNo + '?APIKey=' + elexonAPIKey



# Application configuration
if os.environ.get('carbonintensity_appUseDirectAPI') is not None:
    appUseDirectAPI = (os.environ.get('carbonintensity_appUseDirectAPI') == 'True') 
else: appUseDirectAPI = True

# SQL cache database config
if appUseDirectAPI == False:
    dbUser = os.environ.get('carbonintensity_dbUser')
    dbPassword = os.environ.get('carbonintensity_dbPassword')
    dbServer = os.environ.get('carbonintensity_dbServer')
    dbSchema = os.environ.get('carbonintensity_dbSchema')
    dbTable = os.environ.get('carbonintensity_dbTable')

app = Flask(__name__)
api = Api(app)


def fetch_elexon_data(URL,timeOutLimit):      
    try:
        return requests.get(url=URL,timeout=timeOutLimit).text
    except requests.exceptions.Timeout:
        return requests.get(url=URL,timeout=9999).text  # Need to add proper timeout handling
    except requests.exceptions.RequestException as e:
        # catastrophic error
        raise SystemExit(e)


def parse_elexon_data(rawdata):
    root = ET.fromstring(rawdata)

    data =[]; cols = []
    for i, child in enumerate(root[2][1]):
        data.append([subchild.text for subchild in child])        

    for child in root[2][1][0]:    
        cols.append(child.tag)    

    cols.append('biddingZone')    
    df = pd.DataFrame(data)
    df.columns = cols
    df.drop(columns=['recordType'],inplace=True)
    df = df.astype({'fuelType': 'str',
            'currentMW': 'int64', 
            'currentPercentage': 'float64',
            'lastHalfHourLocalStartTime': 'datetime64',
            'lastHalfHourLocalEndTime': 'datetime64',
            'lastHalfHourMW': 'int64', 
            'lastHalfHourPercentage': 'float64',
            'last24HourLocalStartTime': 'datetime64',
            'last24HourLocalEndTime': 'datetime64',
            'last24HourMWh': 'int64', 
            'last24HourPercentage': 'float64',
            'activeFlag': 'str',
            'biddingZone': 'str'})

    df['currentTotalMW'] = int(root[2][0][0].text)
    df['lastHalfHourTotalMW'] = int(root[2][0][2].text)
    df['last24HourTotalMWh'] = int(root[2][0][4].text)
    df['dataLastUpdated'] = datetime.strptime(root[2][3].text, '%Y-%m-%d %H:%M:%S')
    df['dataWritten'] = datetime.now().replace(microsecond=0)

    return df 


def write_data_to_sql(df):
    engine = create_engine('mysql://' + dbUser + ':' + dbPassword + '@' + dbServer + '/' + dbSchema)
    df.to_sql(dbTable,con=engine,if_exists='append',index=False)


def fetch_cache_data():
    engine = create_engine('mysql://' + dbUser + ':' + dbPassword + '@' + dbServer + '/' + dbSchema)
    querySQL = 'SELECT * FROM ' + dbTable + '.fuelinsthhcur WHERE dataLastUpdated in (SELECT max(dataLastUpdated) FROM ' + dbTable + '.fuelinsthhcur);'
    return pd.read_sql(con=engine)


def periodic_update(waitTime):    
    while True:
        t.sleep(waitTime)
        print('Fetching latest data...' + datetime.now().replace(microsecond=0).strftime("%d/%m/%Y %H:%M:%S") + '\n')
        rawdata = fetch_elexon_data(elexonURL,20)
        df = parse_elexon_data(rawdata)
        dataLastUpdatedReturn = df['dataLastUpdated'].values[0]
        ageDataLastUpdated = pd.Timestamp.now() - dataLastUpdatedReturn
        print('Age of data:' + str(ageDataLastUpdated.total_seconds() / 60) + '\n')
        if (ageDataLastUpdated.total_seconds() / 60 - elexonUpdateFrequency < 0 ):
            print ('Passed test \n')
            break

    df = df.merge(carbonIntensity, left_on='fuelType', right_on='fuelType')
    df['carbonAmount'] = df.currentMW * df.carbonIntensity
    df['averageTotalCarbonIntensity'] = df.carbonAmount.sum() / df.currentMW.sum()

    write_data_to_sql(df)


class SimpleCarbonIntensity(Resource):
    # This class fetches the Elexon generation data when a get request is made, calculates the average carbon intensity and returns it.

    def get(self):
        # Call Elexon API and parse response into XML tree
        rawdata = fetch_elexon_data(elexonURL,20)
        root = ET.fromstring(rawdata)

        # Extract generation figures from XML tree
        responseCode = int(root[0][0].text)
        dataLastUpdatedDB = root[2][3].text
               
        if responseCode != 200:
            return {'data': 'Error reaching current generation data'}, responseCode
        else:
            # currentTotalMW = int(root[2][0][0].text)
            # currentTotalPercentage = float(root[2][0][1].text)
            # lastHalfHourTotalMW = int(root[2][0][2].text)

            currentMW = []

            for child in root[2][1]:
                currentMW.append(int(child[2].text))

            df = pd.DataFrame({'fuelType': fuelTypes, 'currentMW': currentMW})

            # Map carbon intensities onto generation figures by fuel type
            df = df.merge(carbonIntensity, left_on='fuelType', right_on='fuelType')

            df['carbonEmissions'] = df.currentMW * df.carbonIntensity
            df['currentPC'] = round(df.currentMW / df.currentMW.sum() * 100,1)

            averageCarbonIntensity = round(df.carbonEmissions.sum() / df.currentMW.sum(),1)
            returndata = {'Average Carbon Intensity (gCO2/kWh)':averageCarbonIntensity, 'Data Last Updated': dataLastUpdatedDB}
            
            return {'response': returndata}, 200


class CacheCarbonIntensity(Resource):
    #def __init__(self):
        
    def get(self):
        rawdata = fetch_elexon_data(elexonURL,20)
        root = ET.fromstring(rawdata)

        df = fetch_cache_data()

        averageCarbonIntensity = df.averageTotalCarbonIntensity.iloc[0]
        dataLastUpdatedDB = df.dataLastUpdated.iloc[0]

        returndata = {'Average Carbon Intensity (gCO2/kWh)':averageCarbonIntensity, 'Data Last Updated': dataLastUpdatedDB}

        return {'response': returndata}, 200






if (appUseDirectAPI):
    api.add_resource(SimpleCarbonIntensity, '/carbon')

else:
    scheduler = BackgroundScheduler()
    scheduler.start()
    periodic_update(0) # fetch the latest data immediately on first run
    scheduler.add_job(periodic_update, args=[elexonWaitTime], trigger=CronTrigger.from_crontab('*/5 * * * *')) # set up the scheduled jobs, tell job to wait a specified time to allow Elexon backend to update



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=int(os.environ.get('carbonintensity_port', 8812)))
