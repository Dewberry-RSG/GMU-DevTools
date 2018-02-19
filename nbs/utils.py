# -*- coding: utf-8 -*-
"""
@author: slawler
"""
import pandas as pd
import h5py
import requests
import json
from datetime import datetime
from collections import OrderedDict, defaultdict
import string
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import os
from pathlib import Path
import numpy as np
import os
from glob import glob
from IPython.display import Markdown, display, HTML
#from IPython.core.display import display, HTMLd

#-----------------------------------------------------------------------------#
#--Notebook Functions
#-----------------------------------------------------------------------------#

def printbold(string):
    # Jupyter Notebook function to print bold
    display(Markdown('**'+string+'**'))



#-----------------------------------------------------------------------------#
#--USGS API-like Functions
#-----------------------------------------------------------------------------#

def Get_USGS_Peaks(state, gage):  
    #--Get peaks for a gage, may be sensitive to skiprows value. (check if superceded by GetPKFQ below)
    data_url = 'https://nwis.waterdata.usgs.gov/{}/nwis/peak?site_no={}&agency_cd=USGS&format=rdb'.format(state, gage)
    plot_url = 'https://nwis.waterdata.usgs.gov/{}/nwis/peak/?site_no={}&agency_cd=USGS'.format(state, gage)
    stra = '<a href='
    strb = '>Raw Data</a>'
    strc = '>Static Plot</a>'
    
    display(HTML(stra + data_url + strb)) # Make link to State USGS Gages URL
    display(HTML(stra + plot_url + strc)) # Make link to State USGS Gages URL
    df = pd.read_csv(data_url, comment='#', sep = '\t' )
    df.drop(0, axis=0, inplace=True)
    y = df['peak_va'].astype(float)
    x = df['peak_dt']
    x = pd.to_datetime(x, format= '%Y-%m-%d',  errors='coerce')
    y.index = x
    return df, y 

    
def GotoUSGS(state):
    
    #--Pass state initials (e.g. 'NY'), function opens gage catalogue in browser
    #--URL stirng broken into parts for ease of reading in text editor
    part1 = 'https://waterdata.usgs.gov/nwis/uv?referred_module=sw&state_cd={}'.format(state)
    part2 = '&site_tp_cd=OC&site_tp_cd=OC-CO&site_tp_cd=ES&site_tp_cd=LK&site_tp_cd=ST&'
    part3 = 'site_tp_cd=ST-CA&site_tp_cd=ST-DCH&site_tp_cd=ST-TS&format=station_list'
    gages_url = part1 + part2 + part3
    map_link = 'https://maps.waterdata.usgs.gov/mapper/index.html'
    
    stra = '<a href='
    strb = '>USGS Gages: {}</a>'.format(state)
    strc = '>USGS Online Map </a>'

    display(HTML(stra + gages_url + strb)) # Make link to State USGS Gages URL
    display(HTML(stra + map_link + strc)) # Make link to USGS Gage Map
    
def Ping_USGS_API(gage, params):
    url = 'http://waterservices.usgs.gov/nwis/iv' # USGS API
    r   = requests.get(url, params = params) 
    print("\nRetrieved Data for USGS Gage: ", gage)
    data = r.content.decode()
    d = json.loads(data)
    mydict = dict(d['value']['timeSeries'][0])
    return d, mydict


def GrabData(gage, start, stop, parameter = 'flow'):
    if parameter == 'flow':
        obser = "StreamFlow"
        p = '00060'
    else:
        p = '00065'
        obser = "Stage"

    # Format Datetime Objects for USGS API
    first    =  datetime.date(start).strftime('%Y-%m-%d')
    last     =  datetime.date(stop).strftime('%Y-%m-%d') 
    
    # Ping the USGS API for data
    try:
        params = OrderedDict([('format','json'),('sites',gage),('startDT',first), 
                    ('endDT',last), ('parameterCD',p)])  
        d, mydict = Ping_USGS_API(gage,params)

        # Great, We can pull the station name, and assign to a variable for use later:
        SiteName = mydict['sourceInfo']['siteName']

        # After reveiwing the JSON Data structure, select only data we need: 
        tseries = d['value']['timeSeries'][0]['values'][0]['value'][:]

        # Create a Dataframe, format Datetime data,and assign numeric type to observations
        df = pd.DataFrame.from_dict(tseries)
        df.index = pd.to_datetime(df['dateTime'],format='%Y-%m-%d{}%H:%M:%S'.format('T'))

        df['UTC Offset'] = df['dateTime'].apply(lambda x: x.split('-')[3][1])
        df['UTC Offset'] = df['UTC Offset'].apply(lambda x: pd.to_timedelta('{} hours'.format(x)))

        df.index = df.index - df['UTC Offset']
        df.value = pd.to_numeric(df.value)

        # Get Rid of unwanted data, rename observed data
        df = df.drop('dateTime', 1)
        df.drop('qualifiers',axis = 1, inplace = True)
        df.drop('UTC Offset',axis = 1, inplace = True)
        df = df.rename(columns = {'value':obser})
    except:
        df=None
        print('Error Downloading {}, verify Data is Available'.format(parameter))

    # Plot the Results, and use the SiteName as a title!
    return df




#-----------------------------------------------------------------------------#
#--NOAA API-like Functions
#-----------------------------------------------------------------------------#


def GetHourlyObs(gage, start, stop):
    '''--NOAA API https://tidesandcurrents.noaa.gov/api/'''
    datum     = "msl"   #"NAVD"                   #Datum
    units     = "english"                         #Units
    time_zone = "gmt"                             #Time Zone
    fmt       = "json"                            #Format
    url       = 'http://tidesandcurrents.noaa.gov/api/datagetter'
    product   = 'hourly_height'                     #Product
    
    noaa = pd.DataFrame()
    gages = dict()
    
    t0     = start.strftime('%Y%m%d %H:%M')
    t1     = stop.strftime('%Y%m%d %H:%M')
    api_params = {'begin_date': t0, 'end_date': t1,
                'station': gage,'product':product,'datum':datum,
                'units':units,'time_zone':time_zone,'format':fmt,
                'application':'web_services' }
        
    pred=[];t=[]   
    
    r = requests.get(url, params = api_params)
    jdata =r.json()
    if 'error' in jdata:
        print(jdata)
    
    else:
        for j in jdata['data']:
            t.append(str(j['t']))
            pred.append(str(j['v']))

        colname = str(gage)    
        noaa[colname]= pred
        noaa[colname] = noaa[colname].astype(float)
        noaa['idx'] = pd.to_datetime(t)
        noaa = noaa.set_index('idx')
        
        del noaa.index.name
        #print('We have Observations ' , gage) 
        return noaa
    
def GetHourlyPreds(gage, start, stop):
    '''--NOAA API https://tidesandcurrents.noaa.gov/api/'''
    datum     = "msl"   #"NAVD"                   #Datum
    units     = "english"                         #Units
    time_zone = "gmt"                             #Time Zone
    fmt       = "json"                            #Format
    url       = 'http://tidesandcurrents.noaa.gov/api/datagetter'
    product   = 'predictions'                     #Product
    
    noaa_time_step = '6T'
    noaa = pd.DataFrame()
    gages = dict()
    
    t0     = start.strftime('%Y%m%d %H:%M')
    t1     = stop.strftime('%Y%m%d %H:%M')
    api_params = {'begin_date': t0, 'end_date': t1,
                'station': gage,'product':product,'datum':datum,
                'units':units,'time_zone':time_zone,'format':fmt,
                'application':'web_services' }
        
    pred=[];t=[]   
    
    r = requests.get(url, params = api_params)
    jdata =r.json()
    if 'error' in jdata:
        print(jdata)
    
    else:
        for j in jdata['predictions']:
            t.append(str(j['t']))
            pred.append(str(j['v']))

        colname = str(gage)  + '_tides'   
        noaa[colname]= pred
        noaa[colname] = noaa[colname].astype(float)

        noaa['idx'] = pd.to_datetime(t)
        noaa = noaa.set_index('idx')
        del noaa.index.name

        #print('We have Observations ' , gage) 
        noaa = noaa.resample('1H').last()
        return noaa
    
def GetEventWind(gage, start, stop, product, print_out=False):
    '''--NOAA API https://tidesandcurrents.noaa.gov/api/'''
    interval  = 'h'
    datum     = "msl"   #"NAVD"                   #Datum
    units     = "english"                         #Units
    time_zone = "gmt"                             #Time Zone
    fmt       = "json"                            #Format
    url       = 'http://tidesandcurrents.noaa.gov/api/datagetter'

    noaa = pd.DataFrame()
    df = pd.DataFrame()
    
    t0     = start.strftime('%Y%m%d %H:%M')
    t1     = stop.strftime('%Y%m%d %H:%M')
    api_params = {'begin_date': t0, 'end_date': t1,
                'station': gage,'product':product,'datum':datum,
                'units':units,'time_zone':time_zone,'format':fmt,
                'interval': interval, 'application':'web_services' }
    d = []
    dr = []
    f = []
    g = []
    s = []
    t = []

    r = requests.get(url, params = api_params)
    jdata =r.json()
    #print(url, api_params)
    if 'error' in jdata:
        print(start,'error code: ', r.status_code)

    else:
        for j in jdata['data']:
            t.append(str(j['t']))
            d.append(str(j['d']))
            dr.append(str(j['dr']))
            f.append(str(j['f']))
            g.append(str(j['g']))
            s.append(str(j['s']))
    df['d']= d
    df['dr']= dr
    df['f']= f
    df['g']= g
    df['s']= s
    df['idx'] = pd.to_datetime(t)
    df = df.set_index('idx') 
    noaa = pd.concat([noaa,df], ignore_index=False)
    if print_out:
        print("Adding {} to {}".format(start, stop)) 
    df = pd.DataFrame()
        
    noaa['g'] = pd.to_numeric(noaa['g'])
    noaa['s'] = pd.to_numeric(noaa['s'])
    noaa['d'] = pd.to_numeric(noaa['d'])

    return noaa