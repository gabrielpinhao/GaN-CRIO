from ftplib import FTP
import os

class FTPDownloader:
    def __init__(self, host = "192.168.1.131", user = "NITEE", password = "NITEE"):
        """
        Classe para baixar arquivos via FTP do osciloscópio Yokogawa DL850E.
        Parâmetros:
        - host: Endereço IP do osciloscópio
        - user: Nome de usuário para login FTP
        - password: Senha para login FTP
        """

        self.host = host
        self.user = user
        self.password = password
        self.ftp = None

    def connect(self):
        """Estabelece a conexão FTP com o osciloscópio."""

        self.ftp = FTP(self.host)
        self.ftp.login(user=self.user, passwd=self.password)

    def download_file(self, file_name, test_name, remote_folder, local_folder):
        """
        Baixa um arquivo específico do osciloscópio para o caminho local.
        Parâmetros:
        - file_name: Nome do arquivo a ser baixado
        - test_name: Nome do teste para organizar a pasta local
        - remote_folder: Pasta no osciloscópio onde o arquivo está localizado
        - local_folder: Caminho local onde o arquivo será salvo
        """

        local_path = f"{local_folder}/{test_name}/{file_name}"
        self.ftp.cwd(remote_folder)

        with open(local_path, "wb") as f:
            self.ftp.retrbinary(f"RETR {file_name}", f.write)

    def close(self):
        """Encerra a conexão FTP de forma segura."""
        if self.ftp:
            self.ftp.quit()

def create_local_folder(local_folder, test_name):
    """Cria a pasta local para salvar os arquivos, se ela não existir."""
    os.makedirs(f"{local_folder}/{test_name}", exist_ok=True)

def main():
    """Função principal para executar o download do arquivo CSV do osciloscópio."""

    file_name = "CARUSO_CSV0000.csv"
    test_name = "caruso_test"

    remote_folder = "/HD-0/Gabriel"
    local_folder = f"C:/Users/nitee/Desktop/GaN-CRIO/GaN-CRIO/Ensaios/"

    # --- Preparar pasta ---
    create_local_folder(local_folder, test_name)

    # --- Download ---
    downloader = FTPDownloader()

    downloader.connect()
    downloader.download_file(file_name, test_name, remote_folder, local_folder)
    downloader.close()

if __name__ == "__main__":
    main()