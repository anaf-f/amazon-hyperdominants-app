import io
import os
import streamlit as st
import geopandas as gpd
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
import pandas as pd
import base64

st.set_page_config(
    page_title="Ecological Niche Modeling – Amazon",
    layout="wide"
)

def img_html(path, mime, width):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<img src="data:{mime};base64,{b64}" width="{width}">'

col_logo, col_title = st.columns([1, 8], vertical_alignment="center")
with col_logo:
    st.markdown(img_html("data/logo_v3.svg", "image/svg+xml", 120), unsafe_allow_html=True)
with col_title:
    st.title("Ecological Niche Modeling – Amazon")
    
st.markdown(
    """
    Interactive visualization of occurrence data and ecological niche models
    under current and future climate scenarios for hyperdominant Amazonian species.
    """
)

RASTER_DIR = "raster"
DATA_DIR = "data"

SCENARIO_COLORS = {
    "Current (present)": "#440154",
    "SSP245 – 2041–2060": "#fde725",
    "SSP585 – 2041–2060": "#75d054",
    "SSP245 – 2081–2100": "#1f968b",
    "SSP585 – 2081–2100": "#33638d",
}

# nomes de exibicao (iguais aos do artigo)
DISPLAY = {
    "Current (present)":  "Current",
    "SSP245 – 2041–2060": "Moderate SSP245 – 2050",
    "SSP585 – 2041–2060": "Severe SSP585 – 2050",
    "SSP245 – 2081–2100": "Moderate SSP245 – 2090",
    "SSP585 – 2081–2100": "Severe SSP585 – 2090",
}

SPECIES_CONFIG = {
    "Bertholletia excelsa": {
        "current": os.path.join(RASTER_DIR, "Bertholletia_excelsa.tif"),
        "occ": os.path.join(DATA_DIR, "castanheira.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "B_excelsa_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "B_excelsa_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "B_excelsa_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "B_excelsa_ffinal_binario_SSP585_2081_2100.tif"),
        },
    },
    "Eperua falcata": {
        "current": os.path.join(RASTER_DIR, "Eperua_falcata.tif"),
        "occ": os.path.join(DATA_DIR, "eperua.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "E_falcata_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "E_falcata_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "E_falcata_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "E_falcata_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Eschweilera coriacea": {
        "current": os.path.join(RASTER_DIR, "Eschweilera_coriacea.tif"),
        "occ": os.path.join(DATA_DIR, "eschweilera.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "E_coriacea_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "E_coriacea_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "E_coriacea_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "E_coriacea_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Euterpe oleracea": {
        "current": os.path.join(RASTER_DIR, "Euterpe_oleracea.tif"),
        "occ": os.path.join(DATA_DIR, "oleracea.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "E_oleracea_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "E_oleracea_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "E_oleracea_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "E_oleracea_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Euterpe precatoria": {
        "current": os.path.join(RASTER_DIR, "Euterpe_precatoria.tif"),
        "occ": os.path.join(DATA_DIR, "precatoria.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "E_precatoria_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "E_precatoria_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "E_precatoria_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "E_precatoria_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Goupia glabra": {
        "current": os.path.join(RASTER_DIR, "Goupia_glabra.tif"),
        "occ": os.path.join(DATA_DIR, "goupia.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "G_glabra_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "G_glabra_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "G_glabra_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "G_glabra_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Iriartea deltoidea": {
        "current": os.path.join(RASTER_DIR, "Iriartea_deltoidea.tif"),
        "occ": os.path.join(DATA_DIR, "iriartea.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "I_deltoidea_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "I_deltoidea_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "I_deltoidea_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "I_deltoidea_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Licania apetala": {
        "current": os.path.join(RASTER_DIR, "Licania_apetala.tif"),
        "occ": os.path.join(DATA_DIR, "licania.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "L_apetala_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "L_apetala_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "L_apetala_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "L_apetala_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Oenocarpus bataua": {
        "current": os.path.join(RASTER_DIR, "Oenocarpus_bataua.tif"),
        "occ": os.path.join(DATA_DIR, "bataua.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "O_bataua_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "O_bataua_final_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "O_bataua_final_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "O_bataua_final_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Protium altissimum": {
        "current": os.path.join(RASTER_DIR, "Protium_altissimum.tif"),
        "occ": os.path.join(DATA_DIR, "protium.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "P_altissimum_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "P_altissimum_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "P_altissimum_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "P_altissimum_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Pseudolmedia laevis": {
        "current": os.path.join(RASTER_DIR, "Pseudolmedia_laevis.tif"),
        "occ": os.path.join(DATA_DIR, "pseudo.txt"),
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "P_laevis_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "P_laevis_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "P_laevis_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "P_laevis_final_binario_SSP585_2081_2100.tif"),
        },
    },
    "Vouacapoua americana": {
        "current": os.path.join(RASTER_DIR, "Vouacapoua_americana.tif"),
        "occ": None,
        "future": {
            "SSP245 – 2041–2060": os.path.join(RASTER_DIR, "V_americana_final_binario_SSP245_2041_2060.tif"),
            "SSP245 – 2081–2100": os.path.join(RASTER_DIR, "V_americana_final_binario_SSP245_2081_2100.tif"),
            "SSP585 – 2041–2060": os.path.join(RASTER_DIR, "V_americana_final_binario_SSP585_2041_2060.tif"),
            "SSP585 – 2081–2100": os.path.join(RASTER_DIR, "V_americana_final_binario_SSP585_2081_2100.tif"),
        },
    },
}

CURRENT_LABEL = "Current (present)"
PRODES_RASTER = os.path.join(DATA_DIR, "prodes_binary.tif")   # imagem (png) ou raster (tif); ver load_prodes_rgba
OVERLAP_CSV = os.path.join(DATA_DIR, "species_prodes_overlap.csv")   # valores do artigo (calculados no R)
# coluna do CSV para cada cenario
OVERLAP_COL = {
    "Current (present)": "Current",
    "SSP245 – 2041–2060": "Moderate SSP245 2050",
    "SSP585 – 2041–2060": "Severe SSP585 2050",
    "SSP245 – 2081–2100": "Moderate SSP245 2090",
    "SSP585 – 2081–2100": "Severe SSP585 2090",
}
REGIONS_FILE = os.path.join(DATA_DIR, "regions_legal_amazon.geojson")   # gerado no R (ver instrucoes)

# -------------------------
# Sidebar
# -------------------------
st.sidebar.header("Settings")
species_name = st.sidebar.selectbox("Species", list(SPECIES_CONFIG.keys()))
scenario_label = st.sidebar.selectbox(
    "Scenario",
    [CURRENT_LABEL, "SSP245 – 2041–2060", "SSP585 – 2041–2060",
     "SSP245 – 2081–2100", "SSP585 – 2081–2100"],
    format_func=lambda s: DISPLAY.get(s, s)
)
show_occ = st.sidebar.checkbox("Show occurrences", value=True)
show_def = st.sidebar.checkbox("Show deforestation layer", value=True)
show_regions = st.sidebar.checkbox("Show regions (adapted from ter Steege et al. 2013)", value=True)
show_states = st.sidebar.checkbox("Show state names", value=True)

species_info = SPECIES_CONFIG[species_name]

# -------------------------
# Funções
# -------------------------
@st.cache_data
def load_occurrences(path):
    if path is None or not os.path.exists(path):
        return None
    df = pd.read_csv(path, sep="\t")
    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.x, df.y),
        crs="EPSG:4326"
    )

@st.cache_data
def load_amazon():
    return gpd.read_file(os.path.join(DATA_DIR, "states_legal_amazon.shp")).to_crs(4326)

@st.cache_data
def load_regions(path):
    """Le as regioes (aceita o arquivo original do ter Steege ou o estendido) e recorta na Amazonia Legal."""
    if not os.path.exists(path):
        return None
    gdf = gpd.read_file(path).to_crs(4326)
    if "code" not in gdf.columns and "region" in gdf.columns:     # arquivo original: coluna 'region'
        gdf = gdf.rename(columns={"region": "code"})
    if "name" not in gdf.columns:
        gdf["name"] = gdf["code"]
    gdf["name"] = gdf["name"].astype(str).str.replace(r"\s*\(.*\)$", "", regex=True)   # tira a sigla do nome
    gdf["name"] = gdf["name"].str.replace("Amazonia", "Amazon", regex=False)             # "Amazon", como no artigo

    amz = load_amazon()
    amz_union = amz.geometry.union_all() if hasattr(amz.geometry, "union_all") else amz.unary_union
    gdf["geometry"] = gdf.geometry.intersection(amz_union)       # so a parte dentro da Amazonia Legal
    gdf = gdf[~gdf.geometry.is_empty].reset_index(drop=True)
    return gdf

@st.cache_data
def read_binary_raster(path):
    with rasterio.open(path) as src:
        data = src.read(1).astype(float)
        nodata = src.nodata
        if nodata is not None:
            data = np.where(data == nodata, np.nan, data)
        data = np.where(data == 1, 1, np.nan)
        bounds = src.bounds
        extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)
    return data, extent

@st.cache_data
def load_prodes_rgba(path, png_extent=None):
    """PRODES em vermelho (transparente onde nao ha desmatamento). Aceita png (RGBA) ou tif (raster)."""
    if path.lower().endswith(".png"):
        img = plt.imread(path)                       # floats 0-1, shape (h, w, 3 ou 4)
        if img.ndim == 2:
            mask = img < 0.95
        elif img.shape[2] == 4:
            mask = img[..., 3] > 0.05                # pixels com alpha = desmatamento
        else:
            mask = np.any(img[..., :3] < 0.95, axis=2)   # RGB: tudo que nao e branco
        extent = png_extent                          # (xmin, xmax, ymin, ymax): o png nao traz coordenadas
    else:
        with rasterio.open(path) as src:
            data = src.read(1).astype(float)
            nodata = src.nodata
            if nodata is not None:
                data = np.where(data == nodata, np.nan, data)
            mask = (data == 1)
            b_ = src.bounds
            extent = (b_.left, b_.right, b_.bottom, b_.top)

    h, w = mask.shape
    rgba = np.zeros((h, w, 4), dtype=float)
    rgba[mask, 0] = 1.0   # vermelho
    rgba[mask, 3] = 0.85
    return rgba, extent

@st.cache_data
def load_overlap(path):
    """Area adequada sobreposta ao PRODES (km2), calculada no R (mesmos valores do artigo)."""
    if not os.path.exists(path):
        return None
    return pd.read_csv(path).set_index("Species")

# -------------------------
# Carrega dados base
# -------------------------
amazon = load_amazon()
xmin, ymin, xmax, ymax = amazon.total_bounds
occ = load_occurrences(species_info["occ"]) if show_occ else None
regions = load_regions(REGIONS_FILE) if show_regions else None

prodes_rgba, prodes_extent = None, None
if show_def and os.path.exists(PRODES_RASTER):
    prodes_rgba, prodes_extent = load_prodes_rgba(PRODES_RASTER, (xmin, xmax, ymin, ymax))
elif show_def:
    st.warning(f"Deforestation layer not shown: file '{PRODES_RASTER}' was not found.")

# -------------------------
# Plot
# -------------------------
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_facecolor("none")
fig.patch.set_alpha(0)

legend_patches = []

# SDM atual
try:
    cur_data, cur_extent = read_binary_raster(species_info["current"])
    cur_cmap = ListedColormap([SCENARIO_COLORS[CURRENT_LABEL]])
    ax.imshow(cur_data, extent=cur_extent, cmap=cur_cmap, alpha=0.9, zorder=1)
    legend_patches.append(Patch(color=SCENARIO_COLORS[CURRENT_LABEL], label=DISPLAY[CURRENT_LABEL]))
except Exception as e:
    st.warning(f"Could not load current raster: {e}")

# SDM futuro
if scenario_label != CURRENT_LABEL:
    fut_path = species_info["future"][scenario_label]
    fut_color = SCENARIO_COLORS[scenario_label]
    try:
        fut_data, fut_extent = read_binary_raster(fut_path)
        fut_cmap = ListedColormap([fut_color])
        ax.imshow(fut_data, extent=fut_extent, cmap=fut_cmap, alpha=0.7, zorder=2)
        legend_patches.append(Patch(color=fut_color, label=DISPLAY[scenario_label]))
    except Exception as e:
        st.warning(f"Could not load raster for '{scenario_label}': {e}")

# Amazônia Legal
amazon.plot(ax=ax, facecolor="none", edgecolor="white",
            linewidth=0.6, alpha=0.8, zorder=3)
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

# PRODES como RGBA — transparente onde não há desmatamento
if prodes_rgba is not None:
    ax.imshow(prodes_rgba, extent=prodes_extent,
              aspect="auto", zorder=4, interpolation="none")
    legend_patches.append(Patch(color="red", label="Deforestation (PRODES 2015–2025)"))

# Regioes (ter Steege adaptadas): contorno tracejado + sigla + chave
halo = [pe.withStroke(linewidth=2.5, foreground="black")]
region_pts = []
if regions is not None:
    regions.boundary.plot(ax=ax, color="white", linestyle="--", linewidth=1.0, zorder=3.5)
    for _, r in regions.iterrows():
        pt = r.geometry.representative_point()
        region_pts.append((pt.x, pt.y))
        ax.text(pt.x, pt.y, r["code"], color="white", fontsize=13, fontweight="bold",
                ha="center", va="center", zorder=7, path_effects=halo)
    key = "Regions\n" + "\n".join(f"{r['code']}  {r['name']}" for _, r in regions.sort_values("code").iterrows())
    ax.text(0.99, 0.01, key, transform=ax.transAxes, color="white", fontsize=8,
            ha="right", va="bottom", linespacing=1.4, zorder=7, path_effects=halo)

# Nomes dos estados
if show_states:
    for _, r in amazon.iterrows():
        pt = r.geometry.representative_point()
        px, py = pt.x, pt.y
        # se o nome do estado cai em cima da sigla de uma regiao, empurra na vertical
        for rx, ry in region_pts:
            if abs(px - rx) < 0.12 * (xmax - xmin) and abs(py - ry) < 0.04 * (ymax - ymin):
                py = ry + (1 if py >= ry else -1) * 0.045 * (ymax - ymin)
        ax.text(px, py, r["nome"], color="white", fontsize=9, style="italic",
                ha="center", va="center", zorder=7, path_effects=halo)

# Barra de escala (1000 km) e seta do norte
mean_lat = (ymin + ymax) / 2
km_per_deg = 111.32 * np.cos(np.radians(mean_lat))
bar_deg = 500 / km_per_deg
x0 = xmin + 0.47 * (xmax - xmin)
y0 = ymin + 0.03 * (ymax - ymin)
ax.plot([x0, x0 + bar_deg], [y0, y0], color="white", linewidth=3, zorder=7, solid_capstyle="butt")
ax.text(x0 + bar_deg / 2, y0 + 0.01 * (ymax - ymin), "500 km", color="white", fontsize=9,
        ha="center", va="bottom", zorder=7, path_effects=halo)
ax.annotate("N", xy=(0.94, 0.95), xytext=(0.94, 0.85), xycoords="axes fraction",
            textcoords="axes fraction", color="white", fontsize=12, fontweight="bold",
            ha="center", va="bottom", zorder=7,
            arrowprops=dict(facecolor="white", edgecolor="white", width=3, headwidth=10))

# Ocorrências
if occ is not None:
    occ.plot(ax=ax, color="black", markersize=8, alpha=0.8, zorder=5)

legend = ax.legend(handles=legend_patches, loc="lower left", frameon=False)
for text in legend.get_texts():
    text.set_color("white")

ax.set_title(f"{species_name} – {DISPLAY[scenario_label]}", color="white", fontsize=14)
ax.set_axis_off()

# download do mapa (fundo escuro para o texto branco ficar legivel)
buf = io.BytesIO()
fig.patch.set_alpha(1.0)
fig.savefig(buf, format="png", dpi=200, facecolor="#111111", bbox_inches="tight")
fig.patch.set_alpha(0)

col_map, col_bar = st.columns([3, 2])

with col_map:
    st.download_button(
        "Download map (PNG)",
        data=buf.getvalue(),
        file_name=f"{species_name}_{DISPLAY[scenario_label]}.png".replace(" ", "_").replace("–", "-"),
        mime="image/png",
    )
    st.pyplot(fig, clear_figure=True)

# -------------------------
# Grafico de barras: area adequada dentro do PRODES, por cenario
# -------------------------
with col_bar:
    overlap = load_overlap(OVERLAP_CSV)
    if overlap is None or species_name not in overlap.index:
        st.info(f"Overlap table not found: {OVERLAP_CSV}")
    else:
        order = [CURRENT_LABEL, "SSP245 – 2041–2060", "SSP585 – 2041–2060",
                 "SSP245 – 2081–2100", "SSP585 – 2081–2100"]
        labels = [DISPLAY[sc] for sc in order]
        values = [float(overlap.loc[species_name, OVERLAP_COL[sc]]) / 1000.0 for sc in order]   # mil km2
        colors = [SCENARIO_COLORS[sc] for sc in order]
        shown = [sc == scenario_label or sc == CURRENT_LABEL for sc in order]   # camadas visiveis no mapa

        if values:
            fig2, ax2 = plt.subplots(figsize=(5, 4.2))
            fig2.patch.set_alpha(0)
            ax2.set_facecolor("none")
            y = np.arange(len(values))[::-1]
            ax2.barh(y, values, color=colors, height=0.65)
            for yi, v, sh, bar in zip(y, values, shown, ax2.patches):
                bar.set_alpha(1.0 if sh else 0.25)             # destaca as camadas visiveis no mapa
                ax2.text(v, yi, f" {v:,.1f}", va="center", ha="left", color="white",
                         fontsize=9, alpha=1.0 if sh else 0.5)
            ax2.set_yticks(y)
            ax2.set_yticklabels(labels, color="white", fontsize=9)
            ax2.set_xlabel("Suitable area overlapping PRODES (thousand km²)", color="white", fontsize=9)
            ax2.tick_params(axis="x", colors="white", labelsize=8)
            ax2.set_xlim(0, max(values) * 1.18 if max(values) > 0 else 1)
            for sp in ("top", "right"):
                ax2.spines[sp].set_visible(False)
            for sp in ("left", "bottom"):
                ax2.spines[sp].set_color("#888888")
            ax2.set_title(f"{species_name}", color="white", fontsize=11, style="italic")
            fig2.tight_layout()
            st.pyplot(fig2, clear_figure=True)
            st.caption("Bars highlighted = layers shown on the map (current + selected scenario).")

# -------------------------
# About
# -------------------------
with st.expander("About this app"):
    st.markdown(
        """
        **What it shows.** Climatically suitable area for 12 hyperdominant Amazonian tree species,
        modelled at the Latin American scale and shown here for the Brazilian Legal Amazon,
        under current climate and moderate (SSP245) and severe (SSP585) scenarios for 2050 (2041–2060) and 2090 (2081–2100).

        **Deforestation.** Accumulated deforestation from PRODES/INPE (2015–2025).

        **Regions.** Dashed lines show Amazonian regions adapted from ter Steege et al. (2013):
        boundaries were digitised from the original figure (approximate) and extended to the remaining
        area of the Legal Amazon states by assigning each area to the nearest region.
        They are a geographic reference, not floristic or biogeographic units.

 
        """
    )
