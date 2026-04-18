import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

folder = 'Dados'

files = [
        "M2RT_VG_final.csv",
        "M2CT_VG_final.csv",
        ]

vgs = [15] #Caso Output, colocar os Vgs desejados aqui para filtrar as colunas [10, 15, ...]

# ========== PLOTAGEM ==========

test = 'Transfer' if 'VD' in files[0] else 'Output'

if test == 'Transfer':

    plt.figure(figsize=(5, 4))

    for f in files:
        df = pd.read_csv(f"{folder}/{f}")
        
        # Ajuste de labels e cores
        f_label = '298 K' if 'RT' in f else '77 K'
        f_color = 'red' if 'RT' in f else 'blue'
        f_adj = 0 if 'RT' in f else 0.9
        
        # Dados atuais
        x = df['Vg']
        y = df['Ids'] + f_adj
        
        # --- LÓGICA DE AJUSTE LINEAR (REGRESSÃO) ---
        # Selecionamos, por exemplo, apenas pontos onde Vg > 2.5V para o ajuste
        # Você pode ajustar esse valor conforme a curva
        mask = x > 3.5 
        x_fit = x[mask]
        y_fit = y[mask]
        
        if len(x_fit) > 1:
            coef = np.polyfit(x_fit, y_fit, 1)
            a, b = coef # a é inclinação, b é intercepto em y
            poly1d_fn = np.poly1d(coef) 
            
            # 1. Calcula o intercepto no eixo X (onde y = 0)
            v_th_extrapolated = -b / a
            
            # 2. Plota a reta de ajuste
            x_range = np.linspace(v_th_extrapolated, 4.0, 100) 
            plt.plot(x_range, poly1d_fn(x_range), ls='--', lw = 0.5, c=f_color, alpha=0.8)
                     
            # 5. Adiciona um texto com o valor do intercepto (opcional)
            plt.text(v_th_extrapolated-0.05, -4.5, f'{v_th_extrapolated:.2f}', 
                    color=f_color, fontsize='x-small', fontweight='bold')

        # Plot original dos pontos
        plt.plot(x, y, ls='-', marker='.', markersize=5, 
                label=f_label, lw=1.5, c=f_color)
    
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.5))
    plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    plt.grid(True, which='major', linestyle='-', linewidth=0.8, alpha=0.7)
    plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)

    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(20))
    plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(5))
    plt.grid(True, which='major', linestyle='-', linewidth=0.8, alpha=0.7)
    plt.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)

    plt.xlabel('$V_{G}$, Gate-to-Source Voltage [V]')
    plt.ylabel('$I_{D}$, Drain-to-Source Current [A]')
    plt.xlim(2, 4)
    plt.ylim(0, 100)
    plt.grid(True, linestyle='-', alpha=0.6)
    plt.legend(loc='upper left', fontsize='small', ncol=1)
    plt.tight_layout()
    plt.show()

elif test == 'Output':

    vgs_str = [str(v) for v in vgs]
    max_ron_mili = max_vds_mili = 0

    fig1 = plt.figure(1, figsize=(5, 4))
    ax1 = fig1.add_subplot(111) # Gráfico de Ids vs Vds (Original)

    fig2 = plt.figure(2, figsize=(5, 4))
    ax2 = fig2.add_subplot(111) # Gráfico de Ron vs Ids (Resistência)

    xmin = 10

    for f in files:
        df = pd.read_csv(f"{folder}/{f}")

        colunas_para_dropar = [
            col for col in df.columns 
            if col != 'Vds' and not any(v in col for v in vgs_str)
        ]
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
            t_label = t_label.replace('Vg', '$V_{G}$')
            
            ax1.plot(df_plot['Vds'], df_plot[c], ls='-', marker='.', markersize=5, 
                    label=t_label, color=colors[i], lw=1.5)
            
            ax2.plot(df_plot[c], df_plot['Ron']*1000,ls='-', marker='.', markersize=5, 
                    label=t_label, color=colors[i], lw=1.5)
            
            filtro_ron = df_plot[df_plot[c] > xmin]

            if not filtro_ron.empty:
                max_ron_local = filtro_ron['Ron'].max() * 1000
                max_ron_mili = max(max_ron_mili, max_ron_local)

    # --- CONFIGURAÇÕES FINAIS: GRÁFICO 1 ---

    plt.figure(1)
    plt.title(f'Output Characteristics')
    plt.xlabel('$V_{DS}$, Drain-to-Source Voltage [V]')
    plt.ylabel('$I_{D}$, Drain-to-Source Current [A]')
    #plt.xlim(0, 2.5)
    #plt.ylim(0, 150)
    plt.grid(True, linestyle='-', alpha=0.6)
    plt.legend(loc='upper right', fontsize='small')
    plt.tight_layout()

    # --- CONFIGURAÇÕES FINAIS: GRÁFICO 2 ---
    plt.figure(2)
    plt.title('On-Resistance Characteristics')
    plt.xlabel('$I_{D}$, Drain-to-Source Current [A]')
    plt.ylabel('$R_{DS(on)}$, Static On-Resistance [$m\Omega$]')
    #plt.yscale('log') # Ron costuma ser melhor visualizado em log se variar muito
    plt.grid(True, which="both", linestyle='-', alpha=0.6)
    plt.legend(loc='upper left', fontsize='small')
    plt.xlim(left=10)
    plt.ylim(0, max_ron_mili)
    plt.tight_layout()

    plt.show()


