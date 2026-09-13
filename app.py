import os
import streamlit as st
import geopandas as gpd
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import pandas as pd

st.set_page_config(
    page_title="Ecological Niche Modeling – Amazonia",
    layout="wide"
)

st.title("Ecological Niche Modeling – Amazonia")
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
PRODES_RASTER = os.path.join(DATA_DIR, "prodes_binary.tif")

# -------------------------
# Sidebar
# -------------------------
st.sidebar.header("Settings")
species_name = st.sidebar.selectbox("Species", list(SPECIES_CONFIG.keys()))
scenario_label = st.sidebar.selectbox(
    "Scenario",
    [CURRENT_LABEL, "SSP245 – 2041–2060", "SSP585 – 2041–2060",
     "SSP245 – 2081–2100", "SSP585 – 2081–2100"]
)
show_occ = st.sidebar.checkbox("Show occurrences", value=True)
show_def = st.sidebar.checkbox("Show deforestation layer", value=True)

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
def load_prodes_rgba(path):
    with rasterio.open(path) as src:
        data = src.read(1).astype(float)
        nodata = src.nodata
        if nodata is not None:
            data = np.where(data == nodata, np.nan, data)
        data = np.where(data == 1, 1, np.nan)
        bounds = src.bounds
        extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)

    # Cria RGBA — vermelho onde há desmatamento, transparente onde não há
    h, w = data.shape
    rgba = np.zeros((h, w, 4), dtype=float)
    mask = ~np.isnan(data)
    rgba[mask, 0] = 1.0   # R
    rgba[mask, 1] = 0.0   # G
    rgba[mask, 2] = 0.0   # B
    rgba[mask, 3] = 0.85  # alpha

    return rgba, extent

# -------------------------
# Carrega dados base
# -------------------------
amazon = load_amazon()
xmin, ymin, xmax, ymax = amazon.total_bounds
occ = load_occurrences(species_info["occ"]) if show_occ else None

prodes_rgba, prodes_extent = None, None
if show_def and os.path.exists(PRODES_RASTER):
    prodes_rgba, prodes_extent = load_prodes_rgba(PRODES_RASTER)

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
    legend_patches.append(Patch(color=SCENARIO_COLORS[CURRENT_LABEL], label="Current"))
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
        legend_patches.append(Patch(color=fut_color, label=scenario_label))
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
    legend_patches.append(Patch(color="red", label="Deforestation (PRODES)"))

# Ocorrências
if occ is not None:
    occ.plot(ax=ax, color="black", markersize=8, alpha=0.8, zorder=5)

legend = ax.legend(handles=legend_patches, loc="lower left", frameon=False)
for text in legend.get_texts():
    text.set_color("white")

ax.set_title(f"{species_name} – {scenario_label}", color="white", fontsize=14)
ax.set_axis_off()

st.pyplot(fig, clear_figure=True)