import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import ruptures
from sklearn.linear_model import LinearRegression

path = '/Users/mistral/Documents/ETHZ/Science/Nesthorn-Birchgletscher/Data/meteo'
path_imis = '/Users/mistral/Documents/ETHZ/Science/Nesthorn-Birchgletscher/Data/meteo/IMIS'

elev_jujo = 3571
elev_blatten = 1538
elev_nesthorn = 3100
elev_gan1 = 3193
elev_gan2 = 2710
lr = 0.006 #°C pro meter

blatten = pd.read_csv(os.path.join(path, 'ogd-smn_bla_d_historical.csv'), sep=';')
jujo = pd.read_csv(os.path.join(path, 'ogd-nbcn_jun_d_historical.csv'), sep=';')
gan1 = pd.read_csv(os.path.join(path_imis, 'GAN1.csv'))
gan2 = pd.read_csv(os.path.join(path_imis, 'GAN2.csv'))

# make ref_time to datetime
blatten['reference_timestamp'] = pd.to_datetime(blatten['reference_timestamp'], format='%d.%m.%Y %H:%M')
jujo['reference_timestamp'] = pd.to_datetime(jujo['reference_timestamp'], format='%d.%m.%Y %H:%M')
gan1['measure_date'] = pd.to_datetime(gan1['measure_date'], format='ISO8601', errors='coerce')
gan2['measure_date'] = pd.to_datetime(gan2['measure_date'], format='ISO8601', errors='coerce')

#combine GAN stations
gan = pd.merge(gan1, gan2, on='measure_date', suffixes=['_gan1', '_gan2'])

#aggregate GAN to daily
gan1_daily = gan1.groupby(gan1['measure_date'].dt.date)['TA_30MIN_MEAN'].mean().reset_index().rename(columns={'TA_30MIN_MEAN':'TA_mean'})
gan2_daily = gan2.groupby(gan2['measure_date'].dt.date)['TA_30MIN_MEAN'].mean().reset_index().rename(columns={'TA_30MIN_MEAN':'TA_mean'})

plt.plot(gan1_daily['measure_date'], gan1_daily['TA_mean'], label='gan1')
plt.plot(gan2_daily['measure_date'], gan2_daily['TA_mean'], label='gan2')
plt.legend()
plt.show()

gan_daily = pd.merge(gan1_daily, gan2_daily, on='measure_date', suffixes=['_gan1', '_gan2'])
gan_daily['lr'] = (gan_daily['TA_mean_gan2']-gan_daily['TA_mean_gan1'])/(elev_gan1-elev_gan2)


# apply general lapse-rate correction
blatten['Nesthorn_BLA'] = blatten['tre200d0']+(elev_blatten-elev_nesthorn)*lr
jujo['Nesthorn_JUJO'] = jujo['ths200d0']+(elev_jujo-elev_nesthorn)*lr
gan1_daily['Nesthorn_gan1'] = gan1_daily['TA_mean']+(elev_gan1-elev_nesthorn)*lr
gan2_daily['Nesthorn_gan2'] = gan2_daily['TA_mean']+(elev_gan2-elev_nesthorn)*lr

#plt.plot(blatten['reference_timestamp'], blatten['tre200d0'],'.')
#plt.plot(jujo['reference_timestamp'], jujo['ths200d0'],'.')
plt.plot(blatten['reference_timestamp'], blatten['Nesthorn_BLA'], label='Nesthorn-BLA')
plt.plot(jujo['reference_timestamp'], jujo['Nesthorn_JUJO'], label='Nesthorn_JUJ=')
plt.plot(gan1_daily['measure_date'], gan1_daily['Nesthorn_gan1'], label='Nesthorn_gan1')
plt.plot(gan2_daily['measure_date'], gan2_daily['Nesthorn_gan2'], label='Nesthorn_gan2')
plt.legend()
plt.show()

#merge to extract same dates
same_dates = pd.merge(blatten, jujo, on = 'reference_timestamp', )

#variable lapse-rate:
same_dates['lr'] = (same_dates['tre200d0'] - same_dates['ths200d0']) / (elev_jujo-elev_blatten)

# lapse-rate variation
plt.plot(same_dates['reference_timestamp'], same_dates['lr'],'.')
plt.plot(gan_daily['measure_date'], gan_daily['lr'], '.')
plt.show()

#It looks like there is a seasonal variation in the lapse-rate. Can we correct based on typical lapse-rate for that time (day? month?) of the year?
# jujo - blatten
lr_month = same_dates.groupby(same_dates['reference_timestamp'].dt.month)['lr'].median().reset_index().rename(columns={'lr':'lr_monthly'})
lr_doy = same_dates.groupby(same_dates['reference_timestamp'].dt.dayofyear)['lr'].median().reset_index().rename(columns={'lr':'lr_daily'})

#GAN IMIS Stations
gan_daily['measure_date'] = pd.to_datetime(gan_daily['measure_date'], format='ISO8601', errors='coerce')
gan_lr_month = gan_daily.groupby(gan_daily['measure_date'].dt.month)['lr'].median().reset_index().rename(columns={'lr':'lr_monthly'})

#fitting exponential function:
lr_c = np.polyfit(lr_doy['reference_timestamp'], lr_doy['lr_daily'], 2)
lr_f = np.poly1d(lr_c)
#running mean:
#window_size = 30
#lr_doy['MovingAverage'] = lr_doy['lr'].rolling(window=window_size).median()

plt.plot(lr_doy['reference_timestamp'], lr_doy['lr_daily'],'.')
plt.plot(lr_doy['reference_timestamp'], lr_f(lr_doy['reference_timestamp']))
#plt.plot(lr_doy['reference_timestamp'], lr_doy['MovingAverage'])
plt.show()

plt.plot(lr_month['reference_timestamp'], lr_month['lr_monthly'],'.', label='BLA-JUJO')
plt.plot(gan_lr_month['measure_date'], gan_lr_month['lr_monthly'], '.', label='GAN1-GAN2')
plt.xlabel('Month')
plt.ylabel('Mean lapse rate in °C/m')
plt.title('Monthly median lapse rates')
plt.legend()
plt.show()

################################## APPLY LAPSE RATES ##################################

#apply monthly lapse-rate to jujo and blatten data:
same_dates['month'] = same_dates['reference_timestamp'].dt.month
# merge by month
month_merged = same_dates.merge(lr_month, left_on='month', right_on='reference_timestamp', how='left')
month_merged['Nesthorn_jujo_variable'] = month_merged['ths200d0']+(elev_jujo-elev_nesthorn)*month_merged['lr_monthly']
month_merged['Nesthorn_blatten_variable'] = month_merged['tre200d0']+(elev_blatten-elev_nesthorn)*month_merged['lr_monthly']

plt.scatter(same_dates['Nesthorn_JUJO'], same_dates['Nesthorn_BLA'], label='fixed lapse rate (6 °C/km)', alpha = 0.7, s=2, zorder=2)
plt.scatter(month_merged['Nesthorn_jujo_variable'], month_merged['Nesthorn_blatten_variable'], label='variable lapse rate', alpha = 0.7, s=2, zorder=3)
plt.xlabel('Temp Nesthorn based on JuJo')
plt.ylabel('Temp Nesthorn based on Blatten')
plt.xlim([-30,10])
plt.ylim([-30,10])
plt.axline((-30,-30),(10,10), linewidth=0.5, color='k', zorder=4)
plt.legend()
plt.show()

#Apply monthly lapse-rate to whole data series:
jujo['month'] = jujo['reference_timestamp'].dt.month
jujo_merged = jujo.merge(lr_month, left_on='month', right_on='reference_timestamp', how='left')
jujo_merged['corr_Nesthorn_variable'] = jujo_merged['ths200d0']+(elev_jujo-elev_nesthorn)*jujo_merged['lr_monthly']

blatten['month'] = blatten['reference_timestamp'].dt.month
blatten_merged = blatten.merge(lr_month, left_on='month', right_on='reference_timestamp', how='left')
blatten_merged['corr_Nesthorn_variable'] = blatten_merged['tre200d0']+(elev_blatten-elev_nesthorn)*blatten_merged['lr_monthly']

#save lapse-rate corrected dataframes
blatten_merged.to_csv(os.path.join(path,'Nesthorn_lr-corr_BLA.csv'), columns=['station_abbr', 'reference_timestamp_x', 'lr_monthly', 'corr_Nesthorn_variable'])
jujo_merged.to_csv(os.path.join(path,'Nesthorn_lr-corr_JUJO.csv'), columns=['station_abbr', 'reference_timestamp_x', 'lr_monthly', 'corr_Nesthorn_variable'])

Nesthorn_jujo_maat = (jujo_merged.groupby(jujo_merged['reference_timestamp_x'].dt.year)['corr_Nesthorn_variable'].mean()).reset_index()
Nesthorn_blatten_maat = (blatten_merged.groupby(blatten_merged['reference_timestamp_x'].dt.year) ['corr_Nesthorn_variable'].mean()).reset_index()

plt.plot(Nesthorn_jujo_maat['reference_timestamp_x'], Nesthorn_jujo_maat['corr_Nesthorn_variable'])
plt.plot(Nesthorn_blatten_maat['reference_timestamp_x'], Nesthorn_blatten_maat['corr_Nesthorn_variable'])
plt.title(f'Mittlere Jahrestemperatur Nesthorn {elev_nesthorn}m')
plt.xlabel('Jahr')
plt.ylabel('Temperatur °C')
plt.show()

#Identify breakpoints and trends using ruptures package
#based on https://medium.com/@enginsorhun/decoding-market-shifts-detecting-structural-breaks-ii-2b77bdafd064
#and https://centre-borelli.github.io/ruptures-docs/

signal = Nesthorn_jujo_maat['corr_Nesthorn_variable'].values


algo = ruptures.Dynp(model="l1", min_size=28)
algo.fit(signal)

#just one breakpoint
n_bkps = 1
result = algo.predict(n_bkps=n_bkps)

plt.plot(Nesthorn_jujo_maat['reference_timestamp_x'], signal)  # Plotting against dates
for bkp in result:
     plt.axvline(x=Nesthorn_jujo_maat['reference_timestamp_x'][bkp-1], color='k', linestyle='--')  # Using dates for breakpoints
plt.tight_layout()
plt.show()

#Primary break point is in 1987/1988
#--> calculate warming trend from start of data to 1987 and then warming trend from 1988 to end of TS

break_year = Nesthorn_jujo_maat['reference_timestamp_x'][result[0]]
x = Nesthorn_jujo_maat[Nesthorn_jujo_maat['reference_timestamp_x']<break_year]['reference_timestamp_x'].values.reshape((-1, 1))
y = Nesthorn_jujo_maat[Nesthorn_jujo_maat['reference_timestamp_x']<break_year]['corr_Nesthorn_variable'].values

x_b = Nesthorn_blatten_maat['reference_timestamp_x'].values.reshape((-1, 1))
y_b = Nesthorn_blatten_maat['corr_Nesthorn_variable'].values

reg = LinearRegression().fit(x, y)
reg_b = LinearRegression().fit(x_b, y_b)


#plot
plt.subplots(figsize=(9,5))
plt.plot(Nesthorn_jujo_maat['reference_timestamp_x'], signal, '.-', color='orange', label='from Jungfraujoch')  # Plotting against dates
plt.plot(Nesthorn_blatten_maat['reference_timestamp_x'], Nesthorn_blatten_maat['corr_Nesthorn_variable'],'.-', color='cornflowerblue', label='from Blatten')
plt.plot(x, reg.predict(x), color='orangered', label=f'slope: {reg.coef_[0]:.3f}°/year')
plt.plot(x_b, reg_b.predict(x_b), color='midnightblue', label=f'slope: {reg_b.coef_[0]:.3f}°/year')
plt.axvline(x=Nesthorn_jujo_maat['reference_timestamp_x'][result[0]-1], color='k', linestyle=':', label='breakpoint')  # Using dates for breakpoints
plt.title(f'Mittlere Jahrestemperatur Nesthorn {elev_nesthorn}m')
plt.xlabel('Jahr')
plt.ylabel('Temperatur °C')
plt.legend()
plt.tight_layout()
plt.show()