import xarray as xr
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import numpy as np
import h5py
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()



def read_TCCCON_data():
    dset = xr.open_dataset('ci20120920_20191202.public.nc', decode_times=False)
    timeInSec = dset.time.values*24*60*60
    time = pd.to_datetime(timeInSec,yearfirst=True, unit='s')
    dset = dset.assign_coords({"time" :time})
    df = dset.xco2_ppm.to_dataframe().resample('D').mean()
    df['xco2_ppm_error'] = dset.xco2_ppm_error.to_dataframe().resample('D').mean()
    df['xch4_ppm'] = dset.xch4_ppm.to_dataframe().resample('D').mean()
    df['xch4_ppm_error'] = dset.xch4_ppm_error.to_dataframe().resample('D').mean()
    

    return df, dset.long_deg.values[0], dset.lat_deg.values[0]

def readGOSat(fileName, lat0,lon0, extentLat = 5, 
                    extentLon = 10, out_file=None):

    f = h5py.File(fileName,'r')
    keys = list(f.keys())
    lat = f['lat'][:]
    lon = f['lon'][:]
    sounding_id = f['sounding_id']
    time = f['time']
    xco2_biascorr = f[keys[4]]
    xco2_uncert = f[keys[5]]

    latLow = lat0 - extentLat
    latTop = lat0 + extentLat
    lonLow = lon0 - extentLon
    lonTop = lon0 + extentLon

    lonSlice = np.argwhere((lonTop >= lon )&  (lon>= lonLow))
    latSlice = np.argwhere((latTop >= lat )&  (lat>= latLow))
    regionSlice =  np.concatenate((lonSlice,latSlice))

    dfGO = pd.DataFrame(time[:][regionSlice])
    dfGO['time'] = dfGO[0]
    dfGO = dfGO.drop(0, axis=1)

    dfGO[keys[4]] = xco2_biascorr[:][regionSlice]

    dfGO[keys[5]] = xco2_uncert[:][regionSlice]

    timelist = dfGO.time.to_list()
    time_arr = []
    for i in range(len(timelist)):
        time_arr.append(pd.to_datetime(str(timelist[i])[2:-1], format='%Y-%m-%d %H:%M:%S'))
    dfGO.index = time_arr
    dfGO = dfGO.drop('time', axis =1)
    if out_file != None:
        dfGO.to_csv('data/'+ out_file)

if __name__ == "__main__":
    print('Reading TCCON data')
    df, lon0, lat0 = read_TCCCON_data()
    df.to_csv('data/TCCCON_daily_avg.csv')
    print('Reading XCH4 large region...')
    #Save XCH4 large region
    df = readGOSat('GOSAT_NIES_XCH4_v02.75.h5', lon0, lat0, 
                    out_file='XCH4_large_region.csv')

    #Save XCH4 small region
    print('Reading XCH4 small region...')
    df = readGOSat('GOSAT_NIES_XCH4_v02.75.h5', lon0, lat0,
                    extentLon=5, extentLat=2.5, 
                    out_file='XCH4_small_region.csv')
    #Save XCO2 large region 
    print('Reading XCO2 large region...')
    df = readGOSat('GOSAT_NIES_XCO2_v02.75.h5', lon0, lat0, 
                    out_file='XCO2_large_region.csv')
    #Save XCO2 small region
    print('Reading XCO2 small region...')
    df = readGOSat('GOSAT_NIES_XCO2_v02.75.h5', lon0, lat0,
                    extentLon=5, extentLat=2.5, 
                    out_file='XCO2_small_region.csv')
    