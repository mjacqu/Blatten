import os
import sys
sys.path.append('/Users/mistral/git_repos/FlatCreek')
from VolumeChange import CalculateVolumes
import xdem
import matplotlib.pyplot as plt
import numpy as np

poly_path = '/Users/mistral/Documents/ETHZ/Science/Nesthorn-Birchgletscher/Data/QGIS/mapping'
dem_path = '/Users/mistral/Documents/ETHZ/Science/Nesthorn-Birchgletscher/Data/DEMs'

dh_res = 0.5
total_release = CalculateVolumes(os.path.join(poly_path, 'main-release.geojson'),
                                os.path.join(dem_path, 'dem-diff_20250529-20250523.tif'),
                                dh_res)

#initial rock avalanche
ra_release = CalculateVolumes(os.path.join(poly_path, 'rock-avalanche.geojson'),
                                os.path.join(dem_path, 'dem-diff_20250523-20230823.tif'),
                                dh_res)

# Nestglacier rock avalanche 1
Nestglacier_ra1 = CalculateVolumes(os.path.join(poly_path, '2023-rockfall.geojson'),
                                    os.path.join(dem_path, 'dh_2023sa3d_2022.tif'),
                                    2)

Nestglacier_ra2 = CalculateVolumes(os.path.join(poly_path, 'post-2023-rockfall.geojson'),
                                    os.path.join(dem_path, 'dh_20250523_2023sa3d.tif'),
                                    2)

#behind_glacier
above_glacier = CalculateVolumes(os.path.join(poly_path, 'slope-above-glacier.geojson'),
                                os.path.join(dem_path, 'dem-diff_20250529-20250523.tif'),
                                dh_res)


#deposited rock by May 23 2025
initial_rock_deposit = CalculateVolumes(os.path.join(poly_path, 'deposited-rock-20250523.geojson'),
                                    os.path.join(dem_path, 'dh_20250523_2023sa3d.tif'),
                                    2)

initial_rock_failure = CalculateVolumes(os.path.join(poly_path, 'rock-avalanche.geojson'),
                                    os.path.join(dem_path, 'dh_20250523_2023sa3d.tif'),
                                    2)

missing_mountain = CalculateVolumes(os.path.join(poly_path, 'Missing-mountain.geojson'),
                                    os.path.join(dem_path, 'dh_20250529_2023sa3d.tif'),
                                    2)

remaining_deposits = CalculateVolumes(os.path.join(poly_path, 'remaining-deposits.geojson'),
                                    os.path.join(dem_path, 'dh_20250529_2023sa3d.tif'),
                                    2)


#removed glacier ice
removed_glacier = CalculateVolumes(os.path.join(poly_path, 'removed-glacier-outline.geojson'),
                                    os.path.join(dem_path, 'dh_20250529_2023sa3d.tif'),
                                    2)


#possible pillar volume:
pillar_volume = np.abs(total_release[0])-(np.abs(removed_glacier[0])+initial_rock_deposit[0])                                    


#thickening 2011-2017
gain_2011_2017 = CalculateVolumes(os.path.join(poly_path, 'thickening-2011_2017.geojson'),
                                    os.path.join(dem_path, 'dh_2017_2011_epsg2056.tif'),
                                    2)

# thinning 1986-1993
loss_1986_1993 = CalculateVolumes(os.path.join(poly_path, 'thickening-2011_2017.geojson'),
                                    os.path.join(dem_path, 'dh_1993_1986_epsg2056.tif'),
                                    2)

# thinning 1993-2011
loss_1993_2011 = CalculateVolumes(os.path.join(poly_path, 'thickening-2011_2017.geojson'),
                                    os.path.join(dem_path, 'dh_2011_1993_epsg2056.tif'),
                                    2)



# Deposition and Entrainment
runout_dh = xdem.DEM(os.path.join(dem_path, 'dem-diff_20250529-20250523-runout.tif'))

deposition_msk = (runout_dh.data > 0).astype(int)
erosion_msk = (runout_dh.data < 0).astype(int)

deposition = np.where(deposition_msk == 1, runout_dh.data, np.nan)
erosion = np.where(erosion_msk == 1, runout_dh.data, np.nan)

print(np.nansum(deposition)*0.5*0.5)
print(np.nansum(erosion)*0.5*0.5)


plt.imshow(deposition)
plt.show()



############# ice melt calculation #############

v_ice = 9371803-5815818
v_rock = 5815818+1082076
rho_ice = 917
rho_rock = 2600 #appropriate for gneiss according to suppl. in Shugar et al., 2021
h = 2700-1500
g = 9.6
lf = 333550 #J/kg

p_e = ((v_ice * rho_ice) + (v_rock * rho_rock)) * h * g
ice_melt = (p_e/lf)/rho_ice

#assumptions: all ice at 0°C
#assumption (all potential energy went into ice-melt (likely not realistic))