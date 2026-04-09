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

    def download_latest_file(self, test_name, remote_folder, local_folder):
        """
        Baixa o arquivo mais recente do osciloscópio para o caminho local.
        Parâmetros:
        - test_name: Nome do teste para organizar a pasta local
        - remote_folder: Pasta no osciloscópio onde os arquivos estão
        - local_folder: Caminho local onde o arquivo será salvo
        """

        # Ir para a pasta remota
        self.ftp.cwd(remote_folder)

        # Listar arquivos no diretório remoto
        files = self.ftp.nlst()  # retorna lista de arquivos
        if test_name:
            files = [f for f in files if f.startswith(test_name)]

        if not files:
            raise FileNotFoundError("Nenhum arquivo encontrado no diretório remoto com o prefixo especificado.")

        # Pegar o arquivo mais recente (normalmente o último em ordem alfabética: TESTE0000, TESTE0001...)
        latest_file = sorted(files)[-1]

        # Caminho completo para salvar localmente
        local_path = f"{local_folder}/{test_name}/{latest_file}"

        # Baixar arquivo
        with open(local_path, "wb") as f:
            self.ftp.retrbinary(f"RETR {latest_file}", f.write)
                    
        return local_path, latest_file

    def close(self):
        """Encerra a conexão FTP de forma segura."""
        if self.ftp:
            self.ftp.quit()

    def create_local_folder(local_folder, test_name):
        """Cria a pasta local para salvar os arquivos, se ela não existir."""
        os.makedirs(f"{local_folder}/{test_name}", exist_ok=True)

def main():
    """Função principal para executar o download do arquivo CSV do osciloscópio."""

    file_name = "OUTPUT_TEST0000.csv"
    test_name = "OUTPUT_TEST"

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