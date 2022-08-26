import pathlib
import logging
import numpy as np
from fitting import find_resonance, fit
from current import export_current_density
from simulation import single_pixel

logging.basicConfig(level=logging.INFO)

max_fill = 1950
d_fill = 0.5  # smallest capacitor fill that keeps to the sonnet grid
max_length = 46 # this is the smallest coupling. coupling bar decreases with higher number
d_length = 0.5  # smallest coupling length that keeps to the sonnet grid
qc_target = 20000
tolerance = 10000
directory = pathlib.Path(__file__).parent.absolute()
folder = pathlib.Path('sonnet/fine')

cap_low_freq = dict(fill=1950, coupling_bar_height=0)
cap_high_freq = dict(fill=0, coupling_bar_height=46)
cap = dict(coupling_bar_height=0, fill=0)
# find resonance of two most extreme capacitor fills
find_resonance("low_freq", folder=folder, epsilon=9.3, capacitor_kwargs=cap_low_freq, f1=4, f2=8)
find_resonance("high_freq", folder=folder, epsilon=9.3, capacitor_kwargs=cap_high_freq, f1=4, f2=8)

# fit the two extreme pixels
f0 = fit("pixel_low", folder=folder)["f0"]
f1 = fit("pixel_high", folder=folder)["f0"]

# make and array of capacitor fill values
f = np.linspace(f0, f1, 10)
fill_array = (f0 / f)**2 * (f1**2 - f**2) / (f1**2 - f0**2) * max_fill
fill_array = np.round(fill_array[::-1] / d_fill) * d_fill

# Make an array of coupler length values
length_array = np.arange(0,max_length,d_length)
save_array = [] # array of f, qc, fill, coupling

f2 = 8
for fill in fill_array: # go down the list of fill sizes
    f1 = 4
    for length in length_array:
        name = f"pixel_{abs(fill):g}_{length:g}".replace('.', 'd')
        cap['coupling_bar_height']=length
        cap['fill']=fill
        find_resonance(name, epsilon=9.3, folder=folder, capacitor_kwargs=cap, f1=f1, f2=f2,)
        result = fit(name, folder=folder)

        if result['qc'] < qc_target - tolerance:
            break
        elif abs(result['qc'] - qc_target) < tolerance:
            save_array.append([result['f0'], result['qc'], fill, length])
            filename = f"pixel_{result['f0']:g}_{result['qc']:g}".replace('.', 'd')
            single_pixel(filename, single_freq=True, folder=folder, epsilon=9.3, capacitor_kwargs=cap, f1=round(result['f0'],4))
            export_current_density(folder= folder, xml_name=name, csv_name=f"{filename}.csv",
                                   son_label=f"{filename}.son", frequency=str(int(round(result['f0'],4)*10**9)))
            break
        else:
            continue

# Save the data
save_array = np.array(save_array)
np.savez(directory / folder / "results.npz", save_array)

