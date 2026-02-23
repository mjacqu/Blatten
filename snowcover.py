import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.cm as cm

path = '/Users/mistral/Documents/ETHZ/Science/Nesthorn-Birchgletscher/Data/Permafrost'

data = pd.read_csv(os.path.join(path,'SnowCover_NDSI_Points_CloudMask_ON_1985-2025.csv'), parse_dates=['date'])

plt.plot(data['date'], data['mean'], '.')
plt.show()

# Create 100m elevation bins
bin_width = 100
data['ElevBin'] = (data['elevation1'] // bin_width) * bin_width

# Create a colormap based on ElevBin
unique_bins = sorted(data['ElevBin'].unique())
cmap = plt.get_cmap('viridis')
colors = {b: cmap(i / (len(unique_bins)-1)) for i, b in enumerate(unique_bins)}

# Plot only that bin
single_bin =2700.0
data_bin = data[data['ElevBin'] == single_bin]
plt.figure(figsize=(10,5))
plt.scatter(data_bin['date'], data_bin['mean'], s=25)
plt.xlabel("Date")
plt.ylabel("Value")
plt.title(f"Value vs Date for Elevation Bin {single_bin}–{single_bin+bin_width} m")
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 5))

for b in unique_bins:
    subset = data[data['ElevBin'] == b]
    plt.scatter(subset['date'], subset['mean'], label=f"{int(b)}–{int(b+bin_width)} m",
                color=colors[b], s=20)

plt.xlabel("Date")
plt.ylabel("Value")
plt.title("Value vs Date colored by Elevation (100m bins)")
plt.legend(title="Elevation Bin")
plt.tight_layout()
plt.show()


# group-by elevation bin and take the mean:
snow_by_elevation = data.groupby([pd.Grouper(key='date', freq='D'), 'ElevBin'])['mean'].mean().reset_index()

plt.figure(figsize=(15, 5))

for b in unique_bins:
    subset = snow_by_elevation[snow_by_elevation['ElevBin'] == b]
    plt.scatter(subset['date'], subset['mean'], label=f"{int(b)}–{int(b+bin_width)} m",
                color=colors[b], s=20)

plt.xlabel("Date")
plt.ylabel("Value")
plt.title("Value vs Date colored by Elevation (100m bins)")
plt.legend(title="Elevation Bin")
plt.tight_layout()
plt.show()

# Extract year for grouping
snow_by_elevation['Year'] = snow_by_elevation['date'].dt.year

threshold = 0

records = []

for (elev, yr), sub in snow_by_elevation.groupby(['ElevBin', 'Year']):
    sub = sub.sort_values('date')

    # First date below threshold
    first_below = sub.loc[sub['mean'] < threshold, 'date'].min()

    # Last date above threshold
    last_above = sub.loc[sub['mean'] > threshold, 'date'].max()

    records.append([elev, yr, first_below, last_above])

snow_threshold_summary = pd.DataFrame(records, columns=[
    'ElevBin', 'Year', 'FirstBelowZero', 'LastAboveZero'
])

print(snow_threshold_summary)

snow_threshold_summary['SnowDuration_days'] = (
    snow_threshold_summary['LastAboveZero'] - snow_threshold_summary['FirstBelowZero']
).dt.days

# FOR NOW, DROP VALUES WITH NEGATIVE DAYS. NEED TO FIX THIS!!!!!
snow_threshold_summary = snow_threshold_summary[snow_threshold_summary['SnowDuration_days']>0]

# Create colormap
years = snow_threshold_summary['Year'].unique()
colors = cm.viridis((snow_threshold_summary['Year'] - years.min()) / (years.max() - years.min()))

# Scatter plot with colors by year
plt.figure(figsize=(8,5))
scatter = plt.scatter(
    snow_threshold_summary['ElevBin'],
    snow_threshold_summary['SnowDuration_days'],
    c=snow_threshold_summary['Year'],
    cmap='viridis',
    s=50
)
plt.xlabel("Elevation (m)")
plt.ylabel("Snow-free Duration (days)")
plt.title("Snow-free Duration vs Elevation (colored by year)")
plt.colorbar(scatter, label='Year')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# with year on the x-axis
plt.figure(figsize=(10,5))

# Scatter plot: x = Year, y = SnowFreeDays, color = Elevation
scatter = plt.scatter(
    snow_threshold_summary['Year'],
    snow_threshold_summary['SnowDuration_days'],
    c=snow_threshold_summary['ElevBin'],  # color by elevation
    cmap='viridis',
    s=60
)

plt.xlabel("Year")
plt.ylabel("Snow-Free Days")
plt.title("Snow-Free Days vs Year colored by Elevation")
plt.colorbar(scatter, label='Elevation (m)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()