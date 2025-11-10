# -*- coding: utf-8 -*-
import io, os, math, tempfile, zipfile
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend_mare import *
from OPERACIONAL_UMI_SIMPLIFICADO import processar_sensor

st.set_page_config(page_title="🌊 Monitoramento de Maré com Zonas Contíguas", layout="wide")
st.title("🌊 Monitoramento de Maré - Pontos Intermediários e Zonas Contíguas")

# ====== Config ======
caminho_config = r"C:\Users\campo\Desktop\SistamaQAQC\DASH\f_configSensores.csv"
sensores_disponiveis = [7, 8]
nomes_sensores = {7: "JAGUANUM", 8: "ITAGUAI"}

# Sidebar
st.sidebar.title("Configuração")
estacoes_selecionadas = st.sidebar.multiselect(
    "Selecione uma ou duas estações:",
    options=sensores_disponiveis,
    format_func=lambda x: nomes_sensores.get(x, "")
)
num_pontos = st.sidebar.slider("Número de pontos intermediários:", min_value=1, max_value=10, value=1)
st.sidebar.markdown("---")
st.sidebar.info("Zonas contíguas: comprimento = 10x largura perpendicular; faixas centradas nos pontos; hover com maré mais recente.")

# ====== Helpers ======
@st.cache_data(show_spinner=False)
def carregar_dados_sensor(registro_id):
    try:
        ret = processar_sensor(registro_id=registro_id, caminho_config=caminho_config)
        df = ret[0]
        resultados = ret[1]
        lat = ret[2]
        lon = ret[3]
        df_config = ret[4] if len(ret) >= 5 else pd.DataFrame()

        time_col = "GMT-03:00" if "GMT-03:00" in df.columns else df.columns[0]
        height_col = "Altura Final" if "Altura Final" in df.columns else df.columns[-1]
        df_filtrado = df[[time_col, height_col]].copy()
        df_filtrado = df_filtrado.rename(columns={time_col: "Tempo", height_col: "Altura da Maré (m)"})

        return {
            "df": df_filtrado,
            "resultados": resultados,
            "lat": lat,
            "lon": lon,
            "nome": nomes_sensores.get(registro_id, f"Estação {registro_id}"),
            "df_config": df_config
        }
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar sensor {registro_id}: {e}")
        return {"df": pd.DataFrame(), "resultados": {}, "lat": None, "lon": None, "nome": f"Estação {registro_id}", "df_config": pd.DataFrame()}

def distancia_euclidiana(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def construir_retangulo_centred(center, axis_vec, perp_vec, half_len, half_w):
    cx, cy = center
    ux, uy = axis_vec
    vx, vy = perp_vec
    c1 = (cx + ux*half_len + vx*half_w, cy + uy*half_len + vy*half_w)
    c2 = (cx - ux*half_len + vx*half_w, cy - uy*half_len + vy*half_w)
    c3 = (cx - ux*half_len - vx*half_w, cy - uy*half_len - vy*half_w)
    c4 = (cx + ux*half_len - vx*half_w, cy + uy*half_len - vy*half_w)
    return [c1, c2, c3, c4, c1]

# ====== App logic ======
if not estacoes_selecionadas:
    st.info("Selecione ao menos uma estação na barra lateral.")
else:
    if len(estacoes_selecionadas) == 1:
        registro = estacoes_selecionadas[0]
        dados = carregar_dados_sensor(registro)
        df = dados["df"]
        st.subheader(f"Altura da Maré - {dados['nome']}")
        if not df.empty:
            fig = px.line(df, x="Tempo", y="Altura da Maré (m)", labels={"Tempo": "Tempo", "Altura da Maré (m)": "Maré (m)"})
            fig.update_layout(height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            # CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button("⬇️ Baixar CSV", data=csv_buffer.getvalue(), file_name=f"{dados['nome']}_dados.csv", mime="text/csv")
            # TID
            tid_buffer = io.StringIO()
            tid_buffer.write("--------\tNaN\n")
            for i in range(len(df)):
                tid_buffer.write(f"{df['Tempo'].iloc[i].strftime('%Y/%m/%d %H:%M:%S')} {float(df['Altura da Maré (m)'].iloc[i]):.6f}\n")
            st.download_button("💾 Baixar .tid", data=tid_buffer.getvalue(), file_name=f"{dados['nome']}.tid", mime="text/plain")
        else:
            st.warning("Nenhum dado disponível para esta estação.")

    elif len(estacoes_selecionadas) == 2:
        dados1 = carregar_dados_sensor(estacoes_selecionadas[0])
        dados2 = carregar_dados_sensor(estacoes_selecionadas[1])
        df1 = dados1["df"].rename(columns={"Altura da Maré (m)": "Maré1"})
        df2 = dados2["df"].rename(columns={"Altura da Maré (m)": "Maré2"})
        df1["Tempo"] = pd.to_datetime(df1["Tempo"])
        df2["Tempo"] = pd.to_datetime(df2["Tempo"])
        df_merge = pd.merge(df1, df2, on="Tempo", how="inner").sort_values("Tempo").reset_index(drop=True)

        if df_merge.empty:
            st.warning("As séries das estações não têm timestamps coincidentes.")
        else:
            lat1, lon1 = dados1["lat"], dados1["lon"]
            lat2, lon2 = dados2["lat"], dados2["lon"]

            # gerar pontos intermediários
            pontos = [{"nome": dados1["nome"], "lat": lat1, "lon": lon1, "is_station": True}]
            for i in range(1, num_pontos+1):
                frac = i / (num_pontos+1)
                lat_i = lat1 + (lat2 - lat1)*frac
                lon_i = lon1 + (lon2 - lon1)*frac
                pontos.append({"nome": f"Z{i}", "lat": lat_i, "lon": lon_i, "frac": frac, "is_station": False})
            pontos.append({"nome": dados2["nome"], "lat": lat2, "lon": lon2, "is_station": True})

            # calcular séries de maré interpoladas
            for p in pontos:
                if p["is_station"]:
                    p["series"] = df_merge["Maré1"] if p["nome"]==dados1["nome"] else df_merge["Maré2"]
                else:
                    frac = p["frac"]
                    p["series"] = df_merge["Maré1"] + (df_merge["Maré2"] - df_merge["Maré1"])*frac
                p["mare_atual"] = float(p["series"].iloc[-1])

            # eixo unitário e perpendicular
            axis_dx = lat2 - lat1
            axis_dy = lon2 - lon1
            axis_len = math.hypot(axis_dx, axis_dy)
            axis_unit = (axis_dx/axis_len, axis_dy/axis_len) if axis_len>0 else (1.0,0.0)
            perp_unit = (-axis_unit[1], axis_unit[0])

            # largura mínima entre pontos
            coords = [(p["lat"], p["lon"]) for p in pontos]
            distances_to_nearest = []
            for i,c in enumerate(coords):
                other_dists = [distancia_euclidiana(c,o) for j,o in enumerate(coords) if j!=i]
                distances_to_nearest.append(min(other_dists) if other_dists else 0.0)
            for i,p in enumerate(pontos):
                p["width"] = distances_to_nearest[i]

            # construir zonas
            zonas = []
            cor_zona = "#1f77b4"
            for i,p in enumerate(pontos):
                half_len = p["width"]/2 if p["width"]>0 else 1e-9
                half_w = half_len * 10
                center = (p["lat"], p["lon"])
                poly = construir_retangulo_centred(center, axis_unit, perp_unit, half_len, half_w)
                p["poly"] = poly
                zonas.append({"nome":p["nome"], "poly":poly, "color":cor_zona, "mare_atual":p["mare_atual"]})

            # --- GRÁFICO ---
            st.subheader("📊 Séries de Maré")
            fig_ts = go.Figure()
            fig_ts.add_trace(go.Scatter(x=df_merge["Tempo"], y=df_merge["Maré1"], mode="lines", name=dados1["nome"], line=dict(color="#0096c7")))
            colors = px.colors.qualitative.Plotly
            mid_idx = 0
            for p in pontos:
                if not p["is_station"]:
                    fig_ts.add_trace(go.Scatter(x=df_merge["Tempo"], y=p["series"], mode="lines", name=p["nome"], line=dict(color=colors[mid_idx%len(colors)])))
                    mid_idx+=1
            fig_ts.add_trace(go.Scatter(x=df_merge["Tempo"], y=df_merge["Maré2"], mode="lines", name=dados2["nome"], line=dict(color="#f94144")))
            fig_ts.update_layout(height=480, template="plotly_white", xaxis_title="Tempo", yaxis_title="Altura da Maré (m)", legend_title="Séries")
            st.plotly_chart(fig_ts, use_container_width=True)

            # --- MAPA ---
            st.subheader("🗺️ Mapa")
            df_mapa_pts = pd.DataFrame([{"Nome":p["nome"],"Latitude":p["lat"],"Longitude":p["lon"],"Maré_Atual":p["mare_atual"]} for p in pontos])
            fig_map = px.scatter_mapbox(df_mapa_pts, lat="Latitude", lon="Longitude", hover_name="Nome", hover_data={"Maré_Atual":True}, zoom=6, height=700, mapbox_style="open-street-map")
            fig_map.update_traces(hovertemplate="<b>%{hovertext}</b><br>Maré mais recente: %{customdata[0]:.3f} m")
            # linha de conexão
            #fig_map.add_trace(go.Scattermapbox(lat=[p["lat"] for p in pontos], lon=[p["lon"] for p in pontos], mode="lines", name="Linha", line=dict(width=2,color="gray")))
            # polígonos
            for z in zonas:
                fig_map.add_trace(go.Scattermapbox(
                    lat=[pt[0] for pt in z["poly"]],
                    lon=[pt[1] for pt in z["poly"]],
                    mode="lines",
                    fill="toself",
                    name=f"{z['nome']}",
                    marker=dict(size=1),
                    opacity=0.35,
                    line=dict(width=2,color=z["color"]),
                    hoverinfo="text",
                    text=f"{z['nome']}<br>Maré atual: {z['mare_atual']:.3f} m"
                ))
            fig_map.update_layout(mapbox=dict(center=dict(lat=(lat1+lat2)/2, lon=(lon1+lon2)/2), zoom=6))
            st.plotly_chart(fig_map, use_container_width=True)

            # --- TID e ZDF ---
            tid_folder = tempfile.mkdtemp()
            for idx,p in enumerate(pontos,start=1):
                tid_path = os.path.join(tid_folder,f"{p['nome'].replace(' ','_')}.tid")
                with open(tid_path,"w") as f:
                    f.write("--------\tNaN\n")
                    for t,m in zip(df_merge["Tempo"],p["series"]):
                        f.write(f"{t.strftime('%Y/%m/%d %H:%M:%S')} {m:.6f}\n")
                p["tid_path"]=tid_path
                p["tid_code"]=f"{idx:07d}"

            # criar ZDF
            zdf_lines=["[ZONE_DEF_VERSION_3]\n"]
            for p in pontos:
                zdf_lines.append("[ZONE]")
                zdf_lines.append(f"{p['nome']},{len(p['poly'])}")
                for lat,lon in p["poly"]:
                    zdf_lines.append(f"{lat},{lon}")
            zdf_lines.append("\n[TIDE_ZONE]")
            for p in pontos:
                zdf_lines.append(f"{p['nome']},{p['tid_code']},PRIM,0,1,0,0")
            zdf_lines.append("\n[TIDE_STATION]")
            for p in pontos:
                zdf_lines.append(f"{p['tid_code']},{p['lat']},{p['lon']},1.5,0.1,{p['tid_path']}")
            zdf_lines.append("\n[TIDE_AVERAGE]")
            for i,p in enumerate(pontos):
                neighbors=[]
                if i>0: neighbors.append(pontos[i-1]["tid_code"])
                if i<len(pontos)-1: neighbors.append(pontos[i+1]["tid_code"])
                zdf_lines.append(f"{p['nome']},{p['tid_code']},{','.join(neighbors)}")
            zdf_lines.append("\n[OPTIONS]")
            zdf_lines.append("Outage, 300")
            zdf_lines.append("Interval, 300")
            zdf_text="\n".join(zdf_lines)

            # --- botão para baixar todos ---
            st.subheader("💾 Baixar todos os arquivos em ZIP")
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                # adicionar TID individuais
                for p in pontos:
                    with open(p["tid_path"], "r") as f:
                        tid_text = f.read()
                    zipf.writestr(f"{p['nome'].replace(' ','_')}.tid", tid_text)
                # adicionar ZDF
                zipf.writestr("zoneamento.zdf", zdf_text)
            zip_buffer.seek(0)
            st.download_button(
                label="⬇️ Baixar ZIP com todos os arquivos",
                data=zip_buffer,
                file_name="zonas_com_tid.zip",
                mime="application/zip"
            )
