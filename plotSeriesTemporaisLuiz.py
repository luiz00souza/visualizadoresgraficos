import os
import pandas as pd
import psycopg2
import pandas.io.sql as sqlio
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gsw
from dotenv import load_dotenv
import io
import zipfile
import xml.etree.ElementTree as ET

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Ocean Multi-Table Explorer", layout="wide")
load_dotenv()

ULTIMOS_DIAS_PADRAO = 3   # 👈 AQUI você muda se quiser (ex: 5 dias)

# ======================
# METADADOS DAS TABELAS
# ======================
TABLES = {
    "bmobr_raw": {"schema": "moored", "table": "bmobr_raw", "time": "date_time", "id_col": "buoy_id"},
    "triaxys_raw": {"schema": "moored", "table": "triaxys_raw", "time": "date_time", "id_col": "buoy_id"},
    "bmobr_general": {"schema": "moored", "table": "bmobr_general", "time": "date_time", "id_col": "buoy_id"},
    "triaxys_general": {"schema": "moored", "table": "triaxys_general", "time": "date_time", "id_col": "buoy_id"},
    "spotter_general": {"schema": "moored", "table": "spotter_general", "time": "date_time", "id_col": "buoy_id"},
    "axys_general_new": {"schema": "moored", "table": "axys_general_new", "time": "date_time", "id_col": "buoy_id"},
    "criosfera_general": {"schema": "moored", "table": "criosfera_general", "time": "date_time", "id_col": "buoy_id"},
    "triaxys_status": {"schema": "moored", "table": "triaxys_status", "time": "date_time", "id_col": "buoy_id"},
    "sailbuoy_merged": {"schema": "sailbuoy", "table": "merged", "time": "sailbuoy_time", "id_col": "sailbuoy_unit"},
    "bmobr_qualified_qartod": {"schema": "qualified_data", "table": "bmobr_qualified_qartod", "time": "date_time", "id_col": "buoy_id"},
    "triaxys_qualified_qartod": {"schema": "qualified_data", "table": "triaxys_qualified_qartod", "time": "date_time", "id_col": "buoy_id"},
    "spotter_qualified_qartod": {"schema": "qualified_data", "table": "spotter_qualified_qartod", "time": "date_time", "id_col": "buoy_id"},
    "axys_qualified_qartod": {"schema": "qualified_data", "table": "axys_qualified_qartod", "time": "date_time", "id_col": "buoy_id"},
    "criosfera_qualified_qartod": {"schema": "qualified_data", "table": "criosfera_qualified_qartod", "time": "date_time", "id_col": "buoy_id"},
    "sailbuoy_merged_qualified": {"schema": "sailbuoy", "table": "merged_qualified", "time": "sailbuoy_time", "id_col": "sailbuoy_unit"},
}

# ======================
# BANCO
# ======================
@st.cache_data(show_spinner=False)
def run_query(query, params=None):
    conn = psycopg2.connect(
        dbname=os.getenv("PNBOIA_DB"),
        user=os.getenv("PNBOIA_USER"),
        password=os.getenv("PNBOIA_PSW"),
        host=os.getenv("PNBOIA_HOST"),
        port=os.getenv("PNBOIA_PORT"),
    )
    df = sqlio.read_sql(query, conn, params=params)
    conn.close()
    return df

@st.cache_data(show_spinner=False)
def get_last_timestamp(schema, table, time_col, id_col, record_id):
    df = run_query(
        f"""
        SELECT MAX({time_col}) AS tmax
        FROM {schema}.{table}
        WHERE {id_col} = %s
        """,
        [record_id],
    )
    if df.empty:
        return None
    tmax = df.iloc[0]["tmax"]
    return None if pd.isna(tmax) else pd.to_datetime(tmax, errors="coerce")

@st.cache_data(show_spinner=False)
def get_table_columns(schema, table):
    df = run_query(f"SELECT * FROM {schema}.{table} LIMIT 1")
    return list(df.columns)

@st.cache_data(show_spinner=False)
def get_buoy_options():
    df = run_query("""
        SELECT id AS buoy_id, name
        FROM moored.buoys
        ORDER BY name
    """)
    options = [f"{row.buoy_id} – {row.name}" for row in df.itertuples()]
    ids = df["buoy_id"].tolist()
    return options, ids

@st.cache_data(show_spinner=False)
def get_ids_only(schema, table, id_col):
    df = run_query(
        f"""
        SELECT DISTINCT ({id_col})::text AS id
        FROM {schema}.{table}
        ORDER BY id
        """
    )
    return df["id"].tolist()

# ======================
# PROCESSAMENTO
# ======================
def compute_salinidade(df, temp_col="cttemp", cond_col="ctcond"):
    df = df.copy()
    df["Salinidade (PSU)"] = gsw.SP_from_C(df[cond_col], df[temp_col], 0)
    return df
def daily_stats_panel(df, time_col, vars_, label, tz="America/Sao_Paulo"):
    """
    Painel UX por variável:
      - Último valor válido (não-nulo) + timestamp desse valor
      - Min / Média / Máx do DIA referente ao último valor daquela variável
    """
    if df.empty or not vars_:
        return

    _df = df[[time_col] + vars_].copy()
    _df[time_col] = pd.to_datetime(_df[time_col], errors="coerce")
    _df = _df.dropna(subset=[time_col]).sort_values(time_col)

    # normaliza timezone (sem quebrar se já for tz-aware)
    try:
        if _df[time_col].dt.tz is None:
            _df[time_col] = _df[time_col].dt.tz_localize(
                tz, nonexistent="shift_forward", ambiguous="NaT"
            )
        else:
            _df[time_col] = _df[time_col].dt.tz_convert(tz)
    except Exception:
        pass

    st.subheader("📌 Painel rápido (último valor por variável + estatística do dia)")
    st.caption(f"Referência: **{label}** · cálculo do último dado é **por variável** (último não-nulo).")

    cards_per_row = 4
    blocks = [vars_[i:i + cards_per_row] for i in range(0, len(vars_), cards_per_row)]

    for block in blocks:
        cols = st.columns(len(block))
        for c, var in zip(cols, block):
            with c:
                s_all = pd.to_numeric(_df[var], errors="coerce")

                # achar o último valor não-nulo dessa variável
                valid_mask = s_all.notna()
                if not valid_mask.any():
                    st.markdown(
                        f"""
                        <div style="border:1px solid rgba(0,0,0,0.08); border-radius:16px; padding:14px;
                                    background: rgba(255,255,255,0.7); box-shadow: 0 1px 8px rgba(0,0,0,0.04);">
                          <div style="font-size:14px; opacity:0.75; margin-bottom:6px;">{label} · <b>{var}</b></div>
                          <div style="font-size:26px; font-weight:700; line-height:1.1; margin-bottom:4px;">—</div>
                          <div style="font-size:12px; opacity:0.7; margin-bottom:10px;">Sem dados válidos</div>
                          <div style="display:flex; gap:10px; justify-content:space-between; font-size:12px;">
                            <div><b>Min</b><br>—</div>
                            <div><b>Média</b><br>—</div>
                            <div><b>Máx</b><br>—</div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    continue

                last_idx = _df.index[valid_mask.to_numpy()][-1]
                last_val = float(pd.to_numeric(_df.loc[last_idx, var], errors="coerce"))
                last_ts = _df.loc[last_idx, time_col]
                last_day = pd.Timestamp(last_ts).date()

                # estatística do DIA do último valor (para essa variável)
                day_mask = _df[time_col].dt.date == last_day
                s_day = pd.to_numeric(_df.loc[day_mask, var], errors="coerce").dropna()

                day_min = "—" if s_day.empty else f"{s_day.min():.3g}"
                day_mean = "—" if s_day.empty else f"{s_day.mean():.3g}"
                day_max = "—" if s_day.empty else f"{s_day.max():.3g}"

                st.markdown(
                    f"""
                    <div style="
                        border:1px solid rgba(0,0,0,0.06);
                        border-radius:12px;
                        padding:8px 10px 6px 10px;
                        background: rgba(255,255,255,0.85);
                        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
                        line-height:1.1;
                    ">
                      <div style="font-size:12px; opacity:0.75; margin-bottom:2px;">
                        <b>{var}</b>
                      </div>
                
                      <div style="font-size:18px; font-weight:700; margin-bottom:2px;">
                        {last_val}
                      </div>
                
                      <div style="font-size:10px; opacity:0.6; margin-bottom:4px;">
                        {last_ts}
                      </div>
                
                      <div style="
                            display:flex;
                            justify-content:space-between;
                            font-size:10px;
                            font-weight:600;
                      ">
                        <div style="color:#1f77b4;">↓ {day_min}</div>
                        <div style="color:#555;">μ {day_mean}</div>
                        <div style="color:#d62728;">↑ {day_max}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def find_lat_lon_columns(cols):
    # tenta achar nomes comuns
    lower_map = {c.lower(): c for c in cols}

    lat_candidates = ["latitude", "lat", "y", "nav_lat"]
    lon_candidates = ["longitude", "lon", "long", "x", "nav_lon"]

    lat_col = next((lower_map[c] for c in lat_candidates if c in lower_map), None)
    lon_col = next((lower_map[c] for c in lon_candidates if c in lower_map), None)
    return lat_col, lon_col


@st.cache_data(show_spinner=False)
def get_track_filtered(schema, table, time_col, id_col, record_id, lat_col, lon_col, tmin, tmax):
    q = f"""
        SELECT {time_col} AS t, {lat_col} AS lat, {lon_col} AS lon
        FROM {schema}.{table}
        WHERE {id_col} = %s
          AND {time_col} >= %s
          AND {time_col} <= %s
          AND {lat_col} IS NOT NULL
          AND {lon_col} IS NOT NULL
        ORDER BY {time_col}
    """
    df = run_query(q, [record_id, tmin, tmax])
    if df.empty:
        return df

    df["t"] = pd.to_datetime(df["t"], errors="coerce")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["t", "lat", "lon"])

    # sanity
    df = df[df["lat"].between(-90, 90) & df["lon"].between(-180, 180)]
    return df

def _kml_ns(root):
    # namespace tipo "{http://www.opengis.net/kml/2.2}"
    if root.tag.startswith("{") and "}" in root.tag:
        return root.tag.split("}")[0] + "}"
    return ""

def _parse_kml_coords(coord_text):
    # "lon,lat,alt lon,lat,alt ..."
    if not coord_text:
        return []
    pts = []
    for token in coord_text.replace("\n", " ").replace("\t", " ").split():
        parts = token.split(",")
        if len(parts) >= 2:
            try:
                lon = float(parts[0])
                lat = float(parts[1])
                pts.append((lat, lon))
            except Exception:
                pass
    return pts

def parse_kml_bytes(kml_bytes, default_name="KML"):
    """
    Retorna lista de features:
      {"type": "point"|"line"|"polygon", "name": str, "lat": [...], "lon": [...]}
    """
    feats = []
    try:
        root = ET.fromstring(kml_bytes)
    except Exception:
        return feats

    ns = _kml_ns(root)

    for pm in root.iter(f"{ns}Placemark"):
        name_el = pm.find(f"{ns}name")
        name = name_el.text.strip() if (name_el is not None and name_el.text) else default_name

        # POINT
        for pt in pm.iter(f"{ns}Point"):
            coord_el = pt.find(f"{ns}coordinates")
            coords = _parse_kml_coords(coord_el.text if coord_el is not None else "")
            for (lat, lon) in coords:
                feats.append({"type": "point", "name": name, "lat": [lat], "lon": [lon]})

        # LINESTRING
        for ls in pm.iter(f"{ns}LineString"):
            coord_el = ls.find(f"{ns}coordinates")
            coords = _parse_kml_coords(coord_el.text if coord_el is not None else "")
            if len(coords) >= 2:
                lats = [p[0] for p in coords]
                lons = [p[1] for p in coords]
                feats.append({"type": "line", "name": name, "lat": lats, "lon": lons})

        # POLYGON (outerBoundaryIs / LinearRing)
        for pol in pm.iter(f"{ns}Polygon"):
            outer = pol.find(f".//{ns}outerBoundaryIs/{ns}LinearRing/{ns}coordinates")
            coords = _parse_kml_coords(outer.text if outer is not None else "")
            if len(coords) >= 3:
                lats = [p[0] for p in coords]
                lons = [p[1] for p in coords]
                # fecha o anel
                if (lats[0], lons[0]) != (lats[-1], lons[-1]):
                    lats.append(lats[0])
                    lons.append(lons[0])
                feats.append({"type": "polygon", "name": name, "lat": lats, "lon": lons})

    return feats

def load_kml_or_kmz(file_bytes, filename="uploaded"):
    """
    Aceita bytes de .kml ou .kmz.
    Se for KMZ, carrega TODOS os .kml internos.
    Retorna lista de features.
    """
    feats = []
    fname = (filename or "").lower()

    if fname.endswith(".kmz"):
        try:
            z = zipfile.ZipFile(io.BytesIO(file_bytes))
        except Exception:
            return feats

        kml_names = [n for n in z.namelist() if n.lower().endswith(".kml")]
        for kn in kml_names:
            try:
                kb = z.read(kn)
                feats.extend(parse_kml_bytes(kb, default_name=os.path.basename(kn)))
            except Exception:
                pass
        return feats

    # default .kml
    feats.extend(parse_kml_bytes(file_bytes, default_name=os.path.basename(filename)))
    return feats
def plot_track_map(df_track, title, kml_features=None):
    if df_track is None or df_track.empty:
        st.info("Sem pontos de latitude/longitude no período selecionado.")
        return

    max_points = 8000
    if len(df_track) > max_points:
        step = max(1, len(df_track) // max_points)
        dfp = df_track.iloc[::step].copy()
    else:
        dfp = df_track

    last = df_track.iloc[-1]
    center_lat = float(dfp["lat"].mean())
    center_lon = float(dfp["lon"].mean())

    fig = go.Figure()

    # =========================================================
    # KML overlay — SOMENTE GEOMETRIA (sem fill, sem legenda)
    # =========================================================
    if kml_features:
        for f in kml_features:

            # ----- LINHAS e POLÍGONOS (apenas contorno)
            if f["type"] in ("line", "polygon"):
                fig.add_trace(
                    go.Scattermapbox(
                        lat=f["lat"],
                        lon=f["lon"],
                        mode="lines",
                        line=dict(width=2, color="black"),
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

            # ----- PONTOS
            elif f["type"] == "point":
                fig.add_trace(
                    go.Scattermapbox(
                        lat=f["lat"],
                        lon=f["lon"],
                        mode="markers",
                        marker=dict(size=8, color="black"),
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

    # =========================================================
    # TRAJETÓRIA
    # =========================================================
    fig.add_trace(
        go.Scattermapbox(
            lat=dfp["lat"],
            lon=dfp["lon"],
            mode="lines",
            line=dict(width=2),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # pontos
    fig.add_trace(
        go.Scattermapbox(
            lat=dfp["lat"],
            lon=dfp["lon"],
            mode="markers",
            marker=dict(size=5, opacity=0.6),
            text=dfp["t"].astype(str),
            hovertemplate="t=%{text}<br>lat=%{lat:.4f}<br>lon=%{lon:.4f}<extra></extra>",
            showlegend=False,
        )
    )

    # última posição
    fig.add_trace(
        go.Scattermapbox(
            lat=[float(last["lat"])],
            lon=[float(last["lon"])],
            mode="markers",
            marker=dict(size=12),
            text=[str(last["t"])],
            hovertemplate="<b>ÚLTIMA</b><br>t=%{text}<br>lat=%{lat:.4f}<br>lon=%{lon:.4f}<extra></extra>",
            showlegend=False,
        )
    )

    fig.update_layout(
        title=title,
        height=520,
        margin=dict(l=5, r=5, t=40, b=5),
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=5,
        ),
        showlegend=False,  # 👈 garante que não aparece legenda
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_series_multi(dfs, time_cols, var_lists, labels, mode):

    n_rows = sum(len(v) for v in var_lists) if mode == "Gráficos separados" else 1

    fig = make_subplots(
        rows=n_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02  # espaço mínimo entre gráficos
    )

    row = 1
    annotations = []

    for df, tcol, vars_, label in zip(dfs, time_cols, var_lists, labels):

        for v in vars_:

            fig.add_trace(
                go.Scatter(
                    x=df[tcol],
                    y=df[v],
                    mode="lines+markers",
                    marker=dict(size=2),
                    showlegend=False
                ),
                row=row if mode == "Gráficos separados" else 1,
                col=1,
            )

            # 👇 título ENTRE os gráficos
            annotations.append(
                dict(
                    text=f"{label} · {v}",
                    x=0.01,
                    xref="paper",
                    y=1 - (row - 0.5) / n_rows,
                    yref="paper",
                    showarrow=False,
                    font=dict(size=11),
                    align="left"
                )
            )

            if mode == "Gráficos separados":
                row += 1

    altura_por_linha = 120

    fig.update_layout(
        height=altura_por_linha * n_rows,
        plot_bgcolor="rgba(245,245,245,0.9)",
        margin=dict(l=40, r=5, t=10, b=25),
        showlegend=False,
        annotations=annotations
    )

    # remove eixo X repetido
    if mode == "Gráficos separados":
        for i in range(1, n_rows):
            fig.update_xaxes(showticklabels=False, row=i, col=1)

    return fig



# ======================
# UI
# ======================
st.title("🌊 Ocean Multi-Table Explorer")

with st.sidebar:
    st.header("🔎 Fonte de dados")

    primary_table = st.selectbox("Tabela principal", list(TABLES.keys()),index=8)
    pinfo = TABLES[primary_table]
    cols = get_table_columns(pinfo["schema"], pinfo["table"])

    if "name" in cols:
        options, ids = get_buoy_options()
        sel = st.selectbox("Registro (ID – Nome)", options)
        record_id = ids[options.index(sel)]
    else:
        ids = get_ids_only(pinfo["schema"], pinfo["table"], pinfo["id_col"])
        record_id = st.selectbox(pinfo["id_col"], ids)

    selected_tables = st.multiselect(
        "Tabelas adicionais",
        [t for t in TABLES if t != primary_table]
    )
    selected_tables = [primary_table] + selected_tables

    st.header("📊 Variáveis")
    DEFAULT_VARS = {
        "bmobr_general": ["vento_vel", "vento_dir"],
        "spotter_general": ["hs", "tp"],
        "sailbuoy_merged": ["ft_windspeed", "ft_winddir","ft_windgust","nortekspeed","nortekdirection",
                            "hs","t0","crudeoil","refined_fuel","turbidity","cttemp","ctcond"],
    }

    table_vars = {}
    for t in selected_tables:
        info = TABLES[t]
        cols_t = get_table_columns(info["schema"], info["table"])
        ignore = {info["time"], info["id_col"], "geom"}
        selectable = [c for c in cols_t if c not in ignore]
        # table_vars[t] = st.multiselect(t, selectable, default=selectable[:2])
                
        default_vars = DEFAULT_VARS.get(t, selectable[:2])
        
        table_vars[t] = st.multiselect(
            t,
            selectable,
            default=[v for v in default_vars if v in selectable]
        )

    dias = st.number_input("Mostrar últimos N dias", min_value=1, max_value=600, value=3, step=1)
    st.header("🗺️ Overlay KML/KMZ")
    kml_file = st.file_uploader("Envie KML ou KMZ", type=["kml", "kmz"])
    kml_features = []
    if kml_file is not None:
        try:
            kml_bytes = kml_file.getvalue()
            kml_features = load_kml_or_kmz(kml_bytes, filename=kml_file.name)
            if not kml_features:
                st.warning("Arquivo carregou, mas não achei geometrias (Placemark/Point/LineString/Polygon).")
            else:
                st.success(f"KML/KMZ OK: {len(kml_features)} geometrias carregadas.")
        except Exception as e:
            st.error(f"Falha lendo KML/KMZ: {e}")
            kml_features = []
    mode = st.radio("Modo", ["Gráficos separados","Mesmo gráfico"])
    carregar = st.button("🚀 Executar")

# ======================
# EXECUÇÃO
# ======================
if carregar:

    dfs, time_cols, var_lists, labels = [], [], [], []

    # ======================
    # 1) Janela de tempo (tmin/tmax) baseada na TABELA PRINCIPAL
    # ======================
    pinfo = TABLES[primary_table]

    tmax_global = get_last_timestamp(
        pinfo["schema"], pinfo["table"],
        pinfo["time"], pinfo["id_col"],
        record_id,
    )

    if tmax_global is None:
        st.warning("Não encontrei timestamp (tmax) para a tabela principal / ID selecionado.")
        st.stop()

    tmin_global = tmax_global - pd.Timedelta(days=int(dias))

    # ======================
    # 2) MAPA (somente se a tabela principal tiver lat/lon) - usa a MESMA janela
    # ======================
    st.markdown("### 🗺️ Mapa (trajetória no período selecionado)")

    p_cols = get_table_columns(pinfo["schema"], pinfo["table"])
    lat_col, lon_col = find_lat_lon_columns(p_cols)

    if lat_col and lon_col:
        df_track = get_track_filtered(
            pinfo["schema"], pinfo["table"],
            pinfo["time"], pinfo["id_col"],
            record_id,
            lat_col, lon_col,
            tmin_global, tmax_global
        )
        # plot_track_map(df_track, title=f"{primary_table} · {record_id} · últimos {int(dias)} dias")
        plot_track_map(df_track, title=f"{primary_table} · {record_id} · últimos {int(dias)} dias", kml_features=kml_features)
    else:
        st.info("Tabela principal não tem colunas reconhecidas de latitude/longitude (lat/lon).")

    st.markdown("---")

    # ======================
    # 3) BUSCA DADOS (todas as tabelas selecionadas) - MESMA janela
    # ======================
    for t in selected_tables:
        info = TABLES[t]
        vars_ = table_vars.get(t, [])
        if not vars_:
            continue

        cols_sel = [info["time"]] + vars_

        q = (
            f"SELECT {', '.join(cols_sel)} "
            f"FROM {info['schema']}.{info['table']} "
            f"WHERE {info['id_col']} = %s "
            f"AND {info['time']} >= %s "
            f"AND {info['time']} <= %s "
            f"ORDER BY {info['time']}"
        )

        params = [record_id, tmin_global, tmax_global]
        df = run_query(q, params)

        if df.empty:
            continue

        df[info["time"]] = pd.to_datetime(df[info["time"]], errors="coerce")
        df = df.dropna(subset=[info["time"]])

        if {"cttemp", "ctcond"}.issubset(set(vars_)):
            df = compute_salinidade(df)
            if "Salinidade (PSU)" not in vars_:
                vars_ = vars_ + ["Salinidade (PSU)"]

        dfs.append(df)
        time_cols.append(info["time"])
        var_lists.append(vars_)
        labels.append(t)

    # ======================
    # 4) RENDER (fora do loop!)
    # ======================
    if dfs:

        st.markdown("### 📊 Painel rápido")
        for df, tcol, vars_, label in zip(dfs, time_cols, var_lists, labels):
            with st.expander(f"📌 {label}", expanded=True):
                daily_stats_panel(df, tcol, vars_, label)

        st.markdown("---")

        fig = plot_series_multi(dfs, time_cols, var_lists, labels, mode)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Nenhum dado encontrado no período selecionado.")
