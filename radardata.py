import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


#set path
path = '/Users/mistral/Documents/ETHZ/Science/Nesthorn-Birchgletscher/Data/monitoring/GP-radar-data'

dirs = os.listdir(path)

def read_radar_data(path,dir,file):
    df = pd.read_csv(os.path.join(path, os.path.join(dir, file)))
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
    df.set_index('Timestamp', inplace = True)
    df.columns = df.columns.str.split().str[1]
    return df

radar_6h_median = read_radar_data(path, dirs[2], '06Ha02_GP-AIM-ROI-velocities-06h-median.csv')
radar_24h_median = read_radar_data(path, dirs[3], '06Hb01_GP-AIM-ROI-velocities-24h-median.csv')
radar_RWB_24h = read_radar_data(path, dirs[0], '06Hb01_GP-AIM-RWB-ROI-velocities-24h-median.csv')


plt.plot(radar_6h_median['R06'], '.', label='R06-6h')
plt.plot(radar_6h_median['R06b'], '.', label='R06b-6h')
plt.plot(radar_6h_median['R06c'], '.', label='R06c-6h')
plt.plot(radar_24h_median['R06'], '.', label='R06-24h')
plt.plot(radar_24h_median['R06b'], '.', label='R06b-24h')
plt.plot(radar_24h_median['R06c'], '.', label='R06c-24h')
plt.plot(radar_RWB_24h['R06'], '.', label='R06-24h-RWB')
plt.plot(radar_RWB_24h['R06b'], '.', label='R06b-24h-RWB')
plt.plot(radar_RWB_24h['R06c'], '.', label='R06c-24h-RWB')
plt.legend()
plt.ylabel('displacement (mm)')
plt.show()

