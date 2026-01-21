import os
from ftplib import FTP, error_perm, error_temp, error_reply, error_proto
from socket import gaierror, timeout

# ============================ #
# CONFIGURAÇÕES GERAIS        #
# ============================ #

FTP_HOST = "cloud10.mmitecnologia.com.br"
FTP_PORT = 1322
FTP_USER = "umi"
FTP_PASS = "MeteoceanUmi123"
FTP_DIR = "/SIG1000"
LOCAL_DIR = r"C:\Users\campo\Desktop\SistamaQAQC\SIG1000RawData"
# ============================ #
# FUNÇÕES FTP                 #
# ============================ #
def conectar_ftp(modo_passivo=True):
    try:
        print(f"[INFO] Conectando ao FTP {FTP_HOST}:{FTP_PORT}...")
        ftp = FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
        print("[OK] Conexão estabelecida.")

        print(f"[INFO] Fazendo login como '{FTP_USER}'...")
        ftp.login(FTP_USER, FTP_PASS)
        print("[OK] Login realizado com sucesso.")

        ftp.set_pasv(modo_passivo)
        print(f"[INFO] Modo passivo {'ativado' if modo_passivo else 'desativado'}.")

        print(f"[INFO] Mudando para diretório remoto: {FTP_DIR}")
        ftp.cwd(FTP_DIR)
        print("[OK] Diretório remoto alterado.")

        return ftp

    except gaierror:
        print("[ERRO] Nome do host não pôde ser resolvido.")
    except timeout:
        print("[ERRO] Conexão expirou.")
    except error_reply as e:
        print(f"[ERRO] Resposta inesperada do servidor FTP: {e}")
    except error_temp as e:
        print(f"[ERRO] Erro temporário: {e}")
    except error_perm as e:
        print(f"[ERRO] Erro permanente: {e}")
    except error_proto as e:
        print(f"[ERRO] Erro de protocolo FTP: {e}")
    except Exception as e:
        print(f"[ERRO] Erro geral ao conectar ao FTP: {e}")

    return None

def baixar_arquivo(ftp, arquivo_remoto, caminho_local, modo_passivo=True):
    caminho_local_completo = os.path.join(caminho_local, arquivo_remoto)

    try:
        if os.path.exists(caminho_local_completo):
            tamanho_remoto = ftp.size(arquivo_remoto)
            tamanho_local = os.path.getsize(caminho_local_completo)
            if tamanho_local >= tamanho_remoto:
                print(f"[INFO] {arquivo_remoto} já existe e está completo. Pulando download.")
                return
            else:
                print(f"[WARN] {arquivo_remoto} está incompleto. Baixando novamente...")

        with open(caminho_local_completo, "wb") as f:
            ftp.retrbinary(f"RETR {arquivo_remoto}", f.write)
        print(f"[✓] Arquivo salvo: {arquivo_remoto}")

    except Exception as e:
        print(f"[ERRO] Falha ao baixar {arquivo_remoto}: {e}")
        if modo_passivo:
            print("[INFO] Tentando novamente em modo ativo...")
            try:
                ftp.quit()
            except:
                pass
            ftp = conectar_ftp(modo_passivo=False)
            if ftp:
                try:
                    with open(caminho_local_completo, "wb") as f:
                        ftp.retrbinary(f"RETR {arquivo_remoto}", f.write)
                    print(f"[✓] Arquivo salvo: {arquivo_remoto} (modo ativo)")
                except Exception as e:
                    print(f"[ERRO] Falha no modo ativo ao baixar {arquivo_remoto}: {e}")

def espelhar_ftp_local():
    ftp = conectar_ftp()
    if not ftp:
        print("[FALHA] Não foi possível estabelecer conexão FTP.")
        return

    try:
        arquivos_remotos = ftp.nlst()
    except Exception as e:
        print(f"[ERRO] Falha ao listar arquivos: {e}")
        ftp.quit()
        return

    for arquivo in arquivos_remotos:
        if arquivo.endswith(".dat"):
            print(f"[INFO] Baixando: {arquivo}")
            baixar_arquivo(ftp, arquivo, LOCAL_DIR)

    ftp.quit()
    print("[✓] Espelhamento concluído.")
#import os

# def consolidar_arquivos(pasta, nome_saida="consolidado.dat", filtro_nome="Teste_13_adcp"):
#     """
#     Consolida arquivos .dat de uma pasta, ignorando as 4 primeiras linhas de cada arquivo.
#     Apenas arquivos com um nome que contenha o texto do filtro são incluídos.
    
#     Args:
#         pasta (str): Caminho da pasta com os arquivos .dat.
#         nome_saida (str): Nome do arquivo de saída. Default: 'consolidado.dat'.
#         filtro_nome (str): Texto que deve estar no nome dos arquivos a serem incluídos. Default: 'Teste_13_adcp'.
#     """
#     arquivos = sorted([
#         f for f in os.listdir(pasta)
#         if f.endswith(".dat")
#         and filtro_nome in f
#         and f != nome_saida
#     ])

#     if not arquivos:
#         print("⚠️ Nenhum arquivo encontrado com o filtro especificado.")
#         return

#     caminho_saida = os.path.join(pasta, nome_saida)

#     with open(caminho_saida, "w", encoding="utf-8") as saida:
#         for nome_arquivo in arquivos:
#             caminho = os.path.join(pasta, nome_arquivo)
#             with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
#                 linhas = f.readlines()[4:]  # Ignora cabeçalho
#                 saida.writelines(linhas)

#     print(f"✔️ Arquivo consolidado criado em:\n{caminho_saida}")
#============================ #
#EXECUÇÃO                     #
#============================ #

#espelhar_ftp_local()
#consolidar_arquivos(LOCAL_DIR)
