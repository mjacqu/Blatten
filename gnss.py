import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

path = "../Data/monitoring/GNSS/11Ma00_GNSS Blatten_KleinesNesthorn.csv"

#read data
gnss = pd.read_csv(path,header=0, names=['Timestamp', 'Position'])
gnss['Timestamp'] = pd.to_datetime(gnss['Timestamp'], format='%d.%m.%Y %H:%M:%S')

gnss[["x", "y", "z"]] = gnss["Position"].str.strip("()").str.split(";", expand=True).astype(float)

gnss['displacement_total'] = np.sqrt((gnss['x'].shift(1)-gnss['x'])**2+
                               (gnss['y'].shift(1)-gnss['y'])**2+
                               (gnss['z'].shift(1)-gnss['z'])**2)

gnss['displacement_total'] = np.sqrt((gnss['x']-gnss['x'][0])**2+
                               (gnss['y']-gnss['y'][0])**2+
                               (gnss['z']-gnss['z'][0])**2)

plt.figure(figsize=(4, 3))
plt.plot(gnss['Timestamp'],gnss['displacement_total'], '.', ms=20)
plt.xlabel('Date (May 2025)', fontsize=20)
plt.ylabel('Motion (m)', fontsize=20)
plt.ylim([-1,20])
ax = plt.gca()
ax.tick_params('both', labelsize=16)
plt.xticks([gnss['Timestamp'][2], gnss['Timestamp'][31]],['17', '19'])
plt.yticks([0,10,20])
ax.tick_params(axis='both', width=1.5, length=5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)
plt.tight_layout()
plt.show()

plt.savefig('../Publications/hazard-cascade/Figures/gnss.pdf')