from tqdm import tqdm
import folium
import pandas as pd
import requests
import time

caminho_arquivo = r"C:\Users\campo\Downloads\savedrecs.xls"
df = pd.read_excel(caminho_arquivo)
# Gerar lista com apenas os 5 primeiros DOIs
dois = df['DOI'].dropna().head(5).tolist()
resultados = []
for doi in dois:
    url = f"https://api.crossref.org/works/{doi}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()['message']
        authors = data.get('author', [])
        if not authors:
            resultados.append({'DOI': doi, 'Author': None, 'Affiliation': None})
            continue
        for a in authors:
            nome = f"{a.get('given','')} {a.get('family','')}".strip()
            afil = a.get('affiliation', [])
            afil_str = afil[0]['name'] if afil else None
            resultados.append({'DOI': doi, 'Author': nome, 'Affiliation': afil_str})
    except Exception as e:
        resultados.append({'DOI': doi, 'Author': None, 'Affiliation': None})
        print(f"Erro com DOI {doi}: {e}")
# Transformar em DataFrame
df = pd.DataFrame(resultados)
geocode_cache = {}
def geocode_affiliation(affiliation):
    """Tenta geocodificar usando 3, 2 ou 1 palavra final, sem sobrescrever resultados existentes."""
    if not affiliation:
        return None, None, None, None, None
    if affiliation in geocode_cache:
        return geocode_cache[affiliation]
    words = affiliation.split()
    for n in [3, 2, 1]:  # tenta 3, depois 2, depois 1 palavra
        if len(words) < n:
            continue
        core = " ".join(words[-n:])
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {'q': core, 'format': 'json', 'limit': 1}
            resp = requests.get(url, params=params, headers={'User-Agent': 'PythonGeocoder'})
            resp.raise_for_status()
            data = resp.json()
            if data:
                address = data[0].get('address', {})
                city = address.get('city') or address.get('town') or address.get('village')
                country = address.get('country')
                lat = data[0].get('lat')
                lon = data[0].get('lon')
                result = (core, city, country, lat, lon)
                geocode_cache[affiliation] = result
                return result
        except Exception as e:
            print(f"Erro ao geocodificar '{core}': {e}")
            time.sleep(1)
            continue
    geocode_cache[affiliation] = (None, None, None, None, None)
    return None, None, None, None, None
unique_affiliations = df['Affiliation'].dropna().unique()
for aff in tqdm(unique_affiliations, desc="Geocodificando afiliações"):
    geocode_affiliation(aff)
    time.sleep(1)  # respeitar limite do Nominatim
df[['Core', 'City', 'Country', 'Latitude', 'Longitude']] = df['Affiliation'].apply(
    lambda x: pd.Series(geocode_cache.get(x, (None, None, None, None, None))))
print("\n--- Estatísticas de valores válidos por coluna ---")
for col in df.columns:
    total = len(df)
    valid = df[col].notna().sum()
    pct = (valid / total) * 100
    print(f"{col}: {valid}/{total} válidos ({pct:.2f}%)")
    #%%
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df = df.dropna(subset=['Latitude', 'Longitude'])
mapa = folium.Map(
    location=[df['Latitude'].mean(), df['Longitude'].mean()],
    zoom_start=12)
for idx, row in df.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"Registro {idx}",
    ).add_to(mapa)
df.to_excel("autores_afiliacoes_geocodificadas.xlsx", index=False)
mapa.save(r"C:\Users\campo\Desktop\mapa_microdados_eficiencia_2021.html")
print("Mapa salvo com sucesso!")
