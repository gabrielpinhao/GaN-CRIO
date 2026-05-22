import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

folder = 'Dados'

files = {
        "SICCT_VG_ALL.csv": 'MOSFET SiC',
        "SICRT_VG_ALL.csv": 'MOSFET SiC',
        "I2RT_VG_final.csv": 'IGBT',
        "M2RT_VG_final.csv": 'MOSFET Si2',
        "M2CT_VG_final.csv": 'MOSFET Si2'
}

# Caso Output, colocar os Vgs desejados aqui para filtrar as colunas [10, 15, ...]
# Para plotar todos, deixe a lista vazia.

vgs = [9,11]
#vgs = [5, 7, 9, 11, 13]
#vgs = [2.5, 3, 4, 6, 8, 10, 12, 15] 

# ================================ DADOS DAS CHAVES ===================================

rdson = {
    'MOSFET SiC': 45, # mOhm
    'MOSFET Si1': 12, # mOhm
    'MOSFET Si2': 7.5, # mOhm
    'IGBT': 38.333, # mOhm
    'GaN HEMT': 75, # mOhm
}

print(list(files.keys()))


# ==================================== PLOTAGEM ======================================

test = 'Transfer' if 'VD' in files[list(files.keys())[0]] else 'Output'

if test == 'Transfer':

    plt.figure(figsize=(5, 4))
    rt = ct = 0

    for f in list(files.keys()):
        df = pd.read_csv(f"{folder}/{f}")
        df = df.sort_values(by='Vg').reset_index(drop=True)

        f_label = '298 K' if 'RT' in f else '77 K'

        n_curves = len(files)

        if 'RT' in f:
            colors = plt.cm.Reds(np.linspace(0.5, 0.9, n_curves))
        elif 'CT' in f:
            colors = plt.cm.Blues(np.linspace(0.5, 0.9, n_curves))
        
        f_color = rt if 'RT' in f else ct
        f_adj = 0 if 'RT' in f else 0.9
        
        x = df['Vg']
        y = df['Ids'] + f_adj
        
        # --- LÓGICA DE AJUSTE LINEAR (REGRESSÃO) ---

        mask = (y >= 12) & (y <= 17)
        x_fit = x[mask]
        y_fit = y[mask]
        
        if len(x_fit) > 1:

            coef = np.polyfit(x_fit, y_fit, 1)
            a, b = coef # a é inclinação, b é intercepto em y
            poly1d_fn = np.poly1d(coef) 
            v_th_extrapolated = -b / a
            print(f'Transconductance = {a:.2f} S')
            
            x_range = np.linspace(v_th_extrapolated, 8.5, 100) # Plota a reta de ajuste
            plt.plot(x_range, poly1d_fn(x_range), ls='--', lw = 0.5, c=colors[f_color], alpha=0.8)

            plt.text(v_th_extrapolated-0.3, -3, f'{v_th_extrapolated:.2f}', 
                    color=colors[f_color], fontsize='x-small', fontweight='bold')

        plt.plot(x, y, ls='-', marker='.', markersize=8, 
                label=f'{f_label}: $g_{{fs}}$ = {a:.2f} S', lw=1.5, c=colors[f_color])
    
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(2))
    plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    plt.grid(True, which='major', linestyle='-', linewidth=0.4, alpha=0.4)
    #plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)

    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(20))
    plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(5))
    plt.grid(True, which='major', linestyle='-', linewidth=0.4, alpha=0.4)
    #plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)

    plt.xlabel('$V_{GS}$, Gate-to-Source Voltage [V]')
    plt.ylabel('$I_{D}$, Drain-to-Source Current [A]')
    plt.xlim(2, 16)
    plt.ylim(0, 80)
    plt.grid(True, linestyle='-', alpha=0.2)
    plt.legend(loc='upper left', fontsize='small', ncol=1)
    plt.tight_layout()

    plt.subplots_adjust(
    left=0.1,   # Margem esquerda
    bottom=0.124, # Margem inferior
    right=0.974,  # Margem direita
    top=0.971,    # Margem superior
    wspace=0.2,   # Espaço horizontal entre subplots
    hspace=0.2    # Espaço vertical entre subplots
)
    plt.show()

elif test == 'Output':

    if vgs and isinstance(vgs, (list, tuple)): vgs_str = [str(v) for v in vgs]
    else: vgs_str = []

    max_ron_mili = max_vds_mili = 0
    xmin = 10

    fig1 = plt.figure(1, figsize=(5, 4))
    ax1 = fig1.add_subplot(111) # Gráfico de Ids vs Vds (Original)

    fig2 = plt.figure(2, figsize=(5, 4))
    ax2 = fig2.add_subplot(111) # Gráfico de Ron vs Ids (Resistência)

    for f in list(files.keys()):
        
        df = pd.read_csv(f"{folder}/{f}")

        colunas_para_dropar = [
            col for col in df.columns 
            if col != 'Vds' and vgs_str and not any(f"={v}." in col or f"={v}V" in col for v in vgs_str)
        ]

        if colunas_para_dropar:
            df.drop(columns=colunas_para_dropar, inplace=True)
        
        cols_to_plot = [c for c in df.columns if c != 'Vds']
        n_curves = len(cols_to_plot)

        if 'RT' in f:
            colors = plt.cm.Reds(np.linspace(0.5, 0.9, n_curves))
            suffix = ' @ 298 K'
        elif 'CT' in f:
            colors = plt.cm.Blues(np.linspace(0.5, 0.9, n_curves))
            suffix = ' @ 77 K'

        for i, c in enumerate(cols_to_plot):
            df_plot = df[['Vds', c]].dropna().copy()
            
            df_plot = df_plot[df_plot[c] > 0]
            df_plot['Ron'] = df_plot['Vds'] / df_plot[c]
            
            t_label = c.split('(')[-1].split(')')[0] + suffix
            t_label = t_label.replace('Vg', '$V_{GS}$')

            rd_label = f"{files[f]}: {suffix}"
            
            ax1.plot(df_plot['Vds'], df_plot[c], ls='-', marker='.', markersize=5, 
                    label=t_label, lw=1.5, color=colors[i])
            
            ax2.plot(df_plot[c], df_plot['Ron']*1000/rdson[files[f]],ls='-', marker='.', markersize=5, 
                    label=rd_label, color=colors[i], lw=1.5)
            
            filtro_ron = df_plot[df_plot[c] > xmin]

            if not filtro_ron.empty:
                max_ron_local = filtro_ron['Ron'].max() * 1000
                max_ron_mili = max(max_ron_mili, max_ron_local)

    # --- CONFIGURAÇÕES FINAIS: GRÁFICO OUTPUT ---

    plt.figure(1)

    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(1))
    plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(0.5))

    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(10))
    plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(5))

    plt.grid(True, which='major', linestyle='-', linewidth=0.4, alpha=0.4)
    #plt.grid(True, which='minor', linestyle=':', linewidth=0.3, alpha=0.3)

    #plt.title('SiC MOSFET Output Characteristics')

    plt.xlabel('$V_{DS}$, Drain-to-Source Voltage [V]')
    plt.ylabel('$I_{D}$, Drain-to-Source Current [A]')
    plt.xlim(0, 6)
    plt.ylim(0, 120)

    # Legenda e layout
    plt.legend(loc='upper left', fontsize='small')
    plt.tight_layout()

    plt.subplots_adjust(
    left=0.10,   # Margem esquerda
    bottom=0.12, # Margem inferior
    right=0.986,  # Margem direita
    top=0.983,    # Margem superior
    wspace=0.2,   # Espaço horizontal entre subplots
    hspace=0.2    # Espaço vertical entre subplots
)

    # --- CONFIGURAÇÕES FINAIS: GRÁFICO Rds(on) ---
    
    plt.figure(2)
    #plt.title('On-Resistance Characteristics')
    plt.xlabel('$I_{D}$, Drain-to-Source Current [A]')
    plt.ylabel('$R_{DS(on)}$, Static On-Resistance [$pu$]')
    #plt.yscale('log') # Ron costuma ser melhor visualizado em log se variar muito
    plt.grid(True, which="both", linestyle='-', alpha=0.6)
    plt.legend(loc='upper right', fontsize='small')
    #plt.xlim(5, 60)
    #plt.ylim(0, 3)
    plt.tight_layout()

    plt.subplots_adjust(
        left=0.123,   # Margem esquerda
        bottom=0.124, # Margem inferior
        right=0.974,  # Margem direita
        top=0.971,    # Margem superior
        wspace=0.2,   # Espaço horizontal entre subplots
        hspace=0.2    # Espaço vertical entre subplots
    )
    plt.show()