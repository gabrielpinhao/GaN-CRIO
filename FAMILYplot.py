import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

folder = 'Ensaios'
prefix = 'OUT_VG'

tests = [f for f in os.listdir(folder) if f.startswith(prefix)]

data_to_plot = []

# 1. Primeiro, colete os dados e as médias
for t in tests:
    file = os.path.join(folder, t, t + '_ALL.csv')
    df = pd.read_csv(file)
    vg_mean = df['Vg'].mean()
    data_to_plot.append((vg_mean, df))

# 2. Ordene a lista com base no vg_mean (o primeiro item da tupla)
data_to_plot.sort(key=lambda x: x[0])

# 3. Agora, faça o plot na ordem correta
for vg_mean, df in data_to_plot:
    plt.loglog(df['Vds'], df['Ids'], label=f"Vg = {vg_mean:.1f} V")

plt.title('Typical Output Characteristics: IRFL44N')
plt.grid(True, which="both", ls="-", lw=0.5)
plt.xlim(0.1, 100)
plt.ylim(1, 1000)
plt.legend(loc='upper left')
plt.show()
