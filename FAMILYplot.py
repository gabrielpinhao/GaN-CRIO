import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

folder = 'Ensaios'
prefix = 'OUT_VG'

tests = [f for f in os.listdir(folder) if f.startswith(prefix)]

data_to_plot = []

for t in tests:
    try:
        file = os.path.join(folder, t, t + '_ALL.csv')
        print(file)
        df = pd.read_csv(file)
        vg_mean = df['Vg'].mean()
        data_to_plot.append((vg_mean, df))
    except Exception as e:
        print(f"Error occurred while processing files: {e}")
        continue

data_to_plot.sort(key=lambda x: x[0])

for vg_mean, df in data_to_plot:
    plt.loglog(df['Vds'], df['Ids'], label=f"Vg = {vg_mean:.1f} V")

plt.title('Typical Output Characteristics: IRLZ44N')
plt.xlabel('Vds (V)')
plt.ylabel('Ids (A)')
plt.grid(True, which="both", ls="-", lw=0.5)
plt.xlim(0.1, 100)
plt.ylim(1, 1000)
plt.legend(loc='upper left', fontsize='small')
plt.show()
