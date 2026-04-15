import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

folder = 'Ensaios'
prefix = 'OUT_VG'

tests = [f for f in os.listdir(folder) if f.startswith(prefix)]

for t in tests:
    file = os.path.join(folder, t, t + '_ALL.csv')
    df = pd.read_csv(file)

    plt.loglog(df['Vds'], df['Ids'], label=f"Vg = {df['Vg'].mean():.0f} V")

plt.xlim(0.1,100)
plt.ylim(1, 1000)
plt.legend()
plt.show()
