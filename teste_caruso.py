import os
import time
import pyvisa
from HIKARI_DC import HikariHF3205P
from YOKOclass import YokogawaDL850  
from FTPDownloader import FTPDownloader
from DATAclass import DATAclass as data


arquivo = data.selecionar_arquivo()

if arquivo:
    df = data.processar_dados(arquivo)  
    data.plot_separated(df)
else:
    print("Nenhum arquivo selecionado.")
