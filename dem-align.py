import geoutils as gu
import os
import numpy as np
import xdem
import matplotlib.pyplot as plt

path = '/Users/mistral/Documents/ETHZ/Science/Nesthorn-Birchgletscher/Data/DEMs'

coreg_pipeline = xdem.coreg.NuthKaab()

#dems
dem1986 = xdem.DEM(os.path.join(path, 'B32-06_birch_19860903_dsm_histVHM_1m_lv95_ln02.tif'))
dem1993 = xdem.DEM(os.path.join(path, 'B32-06_birch_19930901_dsm_histVHM_1m_lv95_ln02.tif'))
dem2011 = xdem.DEM(os.path.join(path, 'B32-06_birch_20119999_dsm_sa3d-2018_2m_lv95_ln02.tif'))
dem2017 = xdem.DEM(os.path.join(path, 'B32-06_birch_20179999_dsm_sa3d-2019_2m_lv95_ln02.tif'))
dem2022 = xdem.DEM(os.path.join(path, 'B32-06_birch_20220716_dsm_is-spez_2m_lv95_ln02.tif'))
dem2023 = xdem.DEM(os.path.join(path, 'B32-06_birch_20230823_dsm_is-stand_2m_lv95_ln02.tif'))
dem2023_sa3d = xdem.DEM(os.path.join(path, 'B32-06_birch_20239999_dsm_sa3d-2024_2m_lv95_ln02.tif'))


#reproject
reproj_1986 = dem1986.reproject(dem2011)
reproj_1993 = dem1993.reproject(dem2011)
reproj_2017 = dem2017.reproject(dem2011)
reproj_2022 = dem2022.reproject(dem2011)
reproj_2023 = dem2023.reproject(dem2011)
reproj_2023_sa3d = dem2023_sa3d.reproject(dem2011)

#stable terrain
glacier_outlines = gu.Vector(os.path.join(path, '/Users/mistral/Documents/ETHZ/Science/Nesthorn-Birchgletscher/Data/DEMs/mask-nuuthkaab.geojson'))
stable_terrain = ~glacier_outlines.create_mask(dem2011)

#align 
aligned_1986 = coreg_pipeline.fit_and_apply(dem2011, reproj_1986, stable_terrain)
aligned_1993 = coreg_pipeline.fit_and_apply(dem2011, reproj_1993, stable_terrain)
aligned_2017 = coreg_pipeline.fit_and_apply(dem2011, reproj_2017, stable_terrain)
aligned_2022 = coreg_pipeline.fit_and_apply(dem2011, reproj_2022, stable_terrain)
aligned_2023 = coreg_pipeline.fit_and_apply(dem2011, reproj_2023, stable_terrain)
aligned_2023_sa3d = coreg_pipeline.fit_and_apply(dem2011, reproj_2023_sa3d, stable_terrain)

#differening-uncorrected
dh_1993_1986_uncor = reproj_1993-reproj_1986
dh_2023_1993_uncor = reproj_1993-reproj_2023
dh_2011_1993_uncor = dem2011-reproj_1993
dh_2017_2011_uncor = reproj_2017-dem2011
dh_2022_2017_uncor = reproj_2022-reproj_2017
dh_2023_2022_uncor = reproj_2023-reproj_2022
dh_2023_2011_uncor = reproj_2023-dem2011
dh_2023sa3d_2022_uncor = reproj_2023_sa3d-reproj_2022
dh_2023sa3d_1993_uncor = reproj_2023_sa3d-reproj_1993
dh_2023sa3d_2011_uncor = reproj_2023_sa3d-dem2011


#differencing-corrected
dh_1993_1986 = aligned_1993 - aligned_1986
dh_2011_1993 = dem2011 - aligned_1993
dh_2023_1993 = aligned_2023 - aligned_1993
dh_2017_2011 = aligned_2017 - dem2011
dh_2022_2017 = aligned_2022 - aligned_2017
dh_2023_2022 = aligned_2023 - aligned_2022
dh_2023_2011 = aligned_2023 - dem2011
dh_2023_1986 = aligned_2023 - aligned_1986
dh_2023sa3d_2022 = aligned_2023_sa3d - aligned_2022
dh_2023sa3d_1993 = aligned_2023_sa3d - aligned_1993
dh_2023sa3d_2011 = aligned_2023_sa3d - dem2011
dh_2023sa3d_1986 = aligned_2023_sa3d - aligned_1986


#verification
def improvement(dh_before, dh_after):
    inliers_before = dh_before[stable_terrain]
    med_before = np.ma.median(inliers_before)
    #nmad_before = inliers_before.get_stats(nmad)

    inliers_after = dh_after[stable_terrain]
    med_after = np.ma.median(inliers_after)

    print(f"Error before: median = {med_before:.2f}")
    print(f"Error after: median = {med_after:.2f}")

improvement(dh_1993_1986_uncor, dh_1993_1986)
improvement(dh_2023_1993_uncor, dh_2023_1993)
improvement(dh_2011_1993_uncor, dh_2011_1993)
improvement(dh_2017_2011_uncor, dh_2017_2011)
improvement(dh_2022_2017_uncor, dh_2022_2017)
improvement(dh_2023_2022_uncor, dh_2023_2022)
improvement(dh_2023_2011_uncor, dh_2023_2011)
improvement(dh_2023sa3d_2022_uncor, dh_2023sa3d_2022)

#plot
fig, axs = plt.subplots(2,2, figsize=(8, 8), sharex=True, sharey=True)
dh_2017_2011.plot(ax=axs[0,0], cmap='seismic_r', vmin=-45, vmax=45)
axs[0, 0].set_title('2017 minus 2011')
dh_2022_2017_uncor.plot(ax=axs[0,1], cmap='seismic_r', vmin=-45, vmax=45)
axs[0, 1].set_title('2022 minus 2017')
dh_2023_2022.plot(ax=axs[1,0], cmap='seismic_r', vmin=-45, vmax=45)
axs[1, 0].set_title('2023 minus 2017')
dh_2023_2011.plot(ax=axs[1,1], cmap='seismic_r', vmin=-45, vmax=45)
axs[1, 1].set_title('2023 minus 2011')
fig.suptitle('Pre-event glacier evolution (2011 - 2023)', y=0.9)
fig.tight_layout()

#plt.show()

fig.savefig('/Users/mistral/Documents/ETHZ/Science/Nesthorn-Birchgletscher/Results/DEM-differencing/pre-event-2011-2023.png')


#save-dh
#dh_2017_2011.save(os.path.join(path, 'dh_2017_2011.tif'), nodata=-9999)
#dh_2022_2017_uncor.save(os.path.join(path, 'dh_2022_2017.tif'), nodata=-9999)
#dh_2023_2022.save(os.path.join(path, 'dh_2023_2022.tif'), nodata=-9999)
#dh_2023_2011.save(os.path.join(path, 'dh_2023_2011.tif'), nodata=-9999)
#dh_2023_1993.save(os.path.join(path, 'dh_2023_1993.tif'), nodata=-9999)
#dh_2011_1993.save(os.path.join(path, 'dh_2011_1993.tif'), nodata=-9999)
#dh_1993_1986.save(os.path.join(path, 'dh_1993_1986.tif'), nodata=-9999)
#dh_2023_1986.save(os.path.join(path, 'dh_2023_1986.tif'), nodata=-9999)
#dh_2023sa3d_2022.save(os.path.join(path, 'dh_2023sa3d_2022.tif'), nodata=-9999)
#dh_2023sa3d_1993.save(os.path.join(path, 'dh_2023sa3d_1993.tif'), nodata=-9999)
#dh_2023sa3d_2011.save(os.path.join(path, 'dh_2023sa3d_2011.tif'), nodata=-9999)
#dh_2023sa3d_1986.save(os.path.join(path, 'dh_2023sa3d_1986.tif'), nodata=-9999)
