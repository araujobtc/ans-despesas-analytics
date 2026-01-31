import os
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/"
DEMOSTRACOES_PATH = "demonstracoes_contabeis"
OPERADORAS_PATH = "operadoras_acreditadas"
OPERADORAS_FILE = "operadoras_acreditadas.csv"

DATA_PATH = "data/ans"

# Certifica que a pasta de download existe
os.makedirs(DATA_PATH, exist_ok=True)


def listar_pastas(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Não foi possível acessar {url}. Status code: {resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")
    links = [a["href"].strip("/") for a in soup.find_all("a", href=True)]
    return links


def baixar_arquivos_ultimos_trimestres(quantidade=3):
    # Verificar se existe a pasta demonstracoes_contabeis
    base_demo_url = f"{BASE_URL}{DEMOSTRACOES_PATH}/"
    pastas = listar_pastas(BASE_URL)

    if DEMOSTRACOES_PATH not in pastas:
        raise FileNotFoundError(
            f"A pasta {DEMOSTRACOES_PATH} não existe em {BASE_URL}"
        )

    # Listar anos disponíveis
    anos = listar_pastas(base_demo_url)
    anos = sorted([a for a in anos if a.isdigit()], reverse=True)

    arquivos_baixados = []

    for ano in anos:
        ano_url = f"{base_demo_url}{ano}/"
        arquivos_no_ano = listar_pastas(ano_url)

        # Filtrar apenas arquivos ZIP
        zip_files = [
            f for f in arquivos_no_ano
            if f.endswith(".zip") and f[0].isdigit()
        ]

        # Ordenar do mais recente para o mais antigo (trimestre, ano)
        zip_files = sorted(
            zip_files,
            key=lambda x: (int(x[0]), int(x[-8:-4])),
            reverse=True
        )

        for zip_file in zip_files:
            if len(arquivos_baixados) >= quantidade:
                break

            download_url = f"{ano_url}{zip_file}"
            caminho_local = os.path.join(DATA_PATH, zip_file)

            if not os.path.exists(caminho_local):
                print(f"Baixando {download_url} ...")
                r = requests.get(download_url, stream=True)
                if r.status_code == 200:
                    with open(caminho_local, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    print(f"Salvo em {caminho_local}")
                else:
                    print(f"Erro ao baixar {download_url}: {r.status_code}")
            else:
                print(f"Arquivo já existe: {caminho_local}")

            arquivos_baixados.append(caminho_local)

        if len(arquivos_baixados) >= quantidade:
            break

    if len(arquivos_baixados) < quantidade:
        print(
            f"Atenção: Apenas {len(arquivos_baixados)} arquivos encontrados. "
            f"Não foi possível completar {quantidade} trimestres."
        )

    return arquivos_baixados


def baixar_operadoras_acreditadas():
    base_operadoras_url = f"{BASE_URL}{OPERADORAS_PATH}/"
    pastas = listar_pastas(BASE_URL)

    if OPERADORAS_PATH not in pastas:
        raise FileNotFoundError(
            f"A pasta {OPERADORAS_PATH} não existe em {BASE_URL}"
        )

    download_url = f"{base_operadoras_url}{OPERADORAS_FILE}"
    caminho_local = os.path.join(DATA_PATH, OPERADORAS_FILE)

    if os.path.exists(caminho_local):
        print(f"Arquivo já existe: {caminho_local}")
        return caminho_local

    print(f"Baixando {download_url} ...")
    r = requests.get(download_url, stream=True)
    if r.status_code == 200:
        with open(caminho_local, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Salvo em {caminho_local}")
    else:
        raise Exception(
            f"Erro ao baixar {download_url}. Status code: {r.status_code}"
        )

    return caminho_local


if __name__ == "__main__":
    print("\nBaixando arquivos trimestrais...")
    arquivos_zip = baixar_arquivos_ultimos_trimestres()

    print("\nBaixando operadoras acreditadas...")
    operadoras_csv = baixar_operadoras_acreditadas()

    print("\nDownload concluído")
    print("ZIPs:", arquivos_zip)
    print("Operadoras:", operadoras_csv)
