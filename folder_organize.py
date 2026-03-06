from ftplib import FTP
import os

ftp_host = "192.168.1.131"
ftp_user = "NITEE"
ftp_pass = "NITEE"  # se houver

file_name = "CARUSO_CSV0000.csv"
remote_folder = "/HD-0/Gabriel"
remote_path = f"{remote_folder}/{file_name}"

test_name = "caruso_test"
local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/{test_name}"
local_path = f"{local_folder}/{file_name}"

# --- Cria pasta local se não existir ---
os.makedirs(local_folder, exist_ok=True)

# --- Conectar no DL850 via FTP ---
ftp = FTP(ftp_host)
ftp.login(user=ftp_user, passwd=ftp_pass)

# Mudar para diretório remoto
ftp.cwd(remote_folder)

# Baixar o arquivo
with open(local_path, 'wb') as f:
    ftp.retrbinary(f"RETR {file_name}", f.write)

ftp.quit()

print(f"Arquivo baixado para {local_path}")