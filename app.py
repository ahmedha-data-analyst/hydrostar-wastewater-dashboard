import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# HydroStar Brand Colors
PRIMARY_GREEN = "#a7d730"
SECONDARY_GREEN = "#499823"
DARK_GREY = "#30343c"
LIGHT_GREY = "#8c919a"
PLOT_BG = "#f2f4f7"
TEXT_BLACK = "#000000"

# Status colors
STATUS_GREEN = "#4CAF50"
STATUS_ORANGE = "#FF9800"
STATUS_RED = "#F44336"

# Page configuration
st.set_page_config(
    page_title="HydroStar Wastewater Analysis",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for HydroStar branding
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Hind:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Hind', sans-serif;
    }}
    
    .main {{
        background-color: #0e1117;
    }}
    
    .stApp {{
        background-color: #0e1117;
    }}
    
    h1, h2, h3 {{
        font-family: 'Hind', sans-serif;
        color: {DARK_GREY};
    }}
    
    .header-container {{
        background-color: {DARK_GREY};
        padding: 20px 30px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 20px;
    }}
    
    .header-title {{
        color: {PRIMARY_GREEN};
        font-size: 32px;
        font-weight: 700;
        margin: 0;
        font-family: 'Hind', sans-serif;
    }}
    
    .header-subtitle {{
        color: white;
        font-size: 16px;
        margin: 5px 0 0 0;
        font-family: 'Hind', sans-serif;
    }}
    
    .status-card {{
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-family: 'Hind', sans-serif;
        color: #000000;
    }}
    
    .status-safe {{
        background-color: #e8f5e9;
        border-left: 5px solid {STATUS_GREEN};
    }}
    
    .status-action {{
        background-color: #fff3e0;
        border-left: 5px solid {STATUS_ORANGE};
    }}
    
    .status-escalation {{
        background-color: #ffebee;
        border-left: 5px solid {STATUS_RED};
    }}
    
    .metric-label {{
        color: {DARK_GREY};
        font-size: 14px;
        font-weight: 500;
    }}
    
    .metric-value {{
        font-size: 24px;
        font-weight: 700;
    }}
    
    .sidebar .stSelectbox label {{
        color: {DARK_GREY};
        font-weight: 500;
    }}
    
    div[data-testid="stSidebar"] {{
        background-color: {DARK_GREY};
    }}
    
    div[data-testid="stSidebar"] .stMarkdown {{
        color: white;
    }}
    
    div[data-testid="stSidebar"] label {{
        color: white !important;
    }}
    
    div[data-testid="stSidebar"] .stSelectbox label {{
        color: white !important;
    }}
    
    .stButton > button {{
        background-color: {PRIMARY_GREEN};
        color: {DARK_GREY};
        font-weight: 600;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-family: 'Hind', sans-serif;
    }}
    
    .stButton > button:hover {{
        background-color: {SECONDARY_GREEN};
        color: white;
    }}
    
    .info-box {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }}
    
    .legend-item {{
        display: inline-flex;
        align-items: center;
        margin-right: 20px;
        font-family: 'Hind', sans-serif;
    }}
    
    .legend-color {{
        width: 20px;
        height: 20px;
        border-radius: 4px;
        margin-right: 8px;
        display: inline-block;
    }}
</style>
""", unsafe_allow_html=True)

# Hardcoded data from Electrolyser_Wastewater_Action_Levels.xlsx
ALKALINE_DATA = {
    "Chloride (Cl-)": {
        "action_level": 10.0,
        "escalation_level": 50.0,
        "why_it_matters": "Anodic Cl2/ClO-/ClO3- formation competes with OER.",
        "citation": "CER well-documented; more competitive under alkaline on MMO anodes (Ru/Ir oxides). (Chen et al., 2021, Electrochim. Acta)"
    },
    "Sulphide (S2-/HS-)": {
        "action_level": 0.05,
        "escalation_level": 0.5,
        "why_it_matters": "Oxidizes to S0/polysulfides; electrode poisoning.",
        "citation": "Rapid anodic oxidation and catalyst fouling. (Mollah et al., 2004, J. Hazard. Mater.)"
    },
    "Cyanide (CN-)": {
        "action_level": 0.01,
        "escalation_level": 0.05,
        "why_it_matters": "Oxidized; with Cl- forms CNCl (toxic).",
        "citation": "CN oxidation and CNCl formation in Cl- media reported. (Zhou et al., 2012, Electrochim. Acta)"
    },
    "Nitrate (NO3- as N)": {
        "action_level": 5.0,
        "escalation_level": 20.0,
        "why_it_matters": "Competes with HER at cathode - NOx/NH3.",
        "citation": "Nitrate readily reduced; competes with HER. (Rosca et al., 2009, Chem. Rev.)"
    },
    "Nitrite (NO2- as N)": {
        "action_level": 0.1,
        "escalation_level": 1.0,
        "why_it_matters": "Cathodic reduction to NO/N2O/NH3.",
        "citation": "Nitrite reduced at low conc; side-reactions documented. (Dima et al., 2003, J. Electroanal. Chem.)"
    },
    "Ammonium (NH4+)": {
        "action_level": 1.0,
        "escalation_level": 5.0,
        "why_it_matters": "Forms chloramines with Cl-; NH3 slip.",
        "citation": "Chloramine kinetics well studied. (Vikesland et al., 2001, ES&T)"
    },
    "Carbonate/Bicarbonate": {
        "action_level": 100.0,
        "escalation_level": 200.0,
        "why_it_matters": "Consumes OH-; carbonate scaling.",
        "citation": "CO2 absorption - carbonate formation in alkaline electrolytes. (Li et al., 2020, Nat. Catal.)"
    },
    "Phosphate (PO43-)": {
        "action_level": 2.0,
        "escalation_level": 5.0,
        "why_it_matters": "Precipitates with Ca2+/Mg2+.",
        "citation": "Electrochemically induced Ca-phosphate precipitation. (Snoeyink & Jenkins, 1980, Water Chemistry)"
    },
    "Iron (Fe2+/Fe3+)": {
        "action_level": 0.1,
        "escalation_level": 0.3,
        "why_it_matters": "Hydroxide sludge; surface blocking.",
        "citation": "Fe hydroxide precipitation and deposition on electrodes. (Zhang et al., 2016, J. Power Sources)"
    },
    "Manganese (Mn2+)": {
        "action_level": 0.02,
        "escalation_level": 0.05,
        "why_it_matters": "Anodic MnO2 films (insulating).",
        "citation": "Mn2+ oxidation - MnO2 deposits. (Post, 1999, Water Res.)"
    },
    "Copper (Cu2+)": {
        "action_level": 0.05,
        "escalation_level": 0.2,
        "why_it_matters": "Cathodic plating; HER overpotential shifts.",
        "citation": "Cu deposition on cathodes. (Fan et al., 2013, Electrochim. Acta)"
    },
    "Nickel (Ni2+)": {
        "action_level": 0.05,
        "escalation_level": 0.1,
        "why_it_matters": "Precipitation/deposition; catalyst drift.",
        "citation": "Ni hydroxide deposition documented. (Biesinger et al., 2009, Appl. Surf. Sci.)"
    },
    "Lead (Pb2+)": {
        "action_level": 0.005,
        "escalation_level": 0.01,
        "why_it_matters": "Cathodic deposition; toxicity.",
        "citation": "Pb deposition/interference. (Hu et al., 2003, Water Res.)"
    },
    "Cadmium (Cd2+)": {
        "action_level": 0.001,
        "escalation_level": 0.005,
        "why_it_matters": "Deposition; toxicity.",
        "citation": "Cd2+ electroreduction documented. (Chen et al., 2000, J. Appl. Electrochem.)"
    },
    "Mercury (Hg2+)": {
        "action_level": 0.0005,
        "escalation_level": 0.001,
        "why_it_matters": "Amalgams; extreme toxicity.",
        "citation": "Hg deposition and amalgam formation. (Liu et al., 2002, ES&T)"
    }
}

NEUTRAL_DATA = {
    "Chloride (Cl-)": {
        "action_level": 5.0,
        "escalation_level": 20.0,
        "why_it_matters": "Cl2/HOCl formation competes strongly with OER at neutral pH.",
        "citation": "Cl- oxidation more competitive at neutral; CER vs OER selectivity. (Zhong et al., 2020, Chem. Rev.)"
    },
    "Bromide (Br-)": {
        "action_level": 0.1,
        "escalation_level": 0.5,
        "why_it_matters": "HOBr/BrO3- formation.",
        "citation": "Bromide oxidized to bromate at neutral. (von Gunten, 2003, Water Res.)"
    },
    "Iodide (I-)": {
        "action_level": 0.02,
        "escalation_level": 0.1,
        "why_it_matters": "I2/iodate; catalyst poisoning.",
        "citation": "Iodide oxidation documented at neutral/alkaline. (Heeb et al., 2014, ES&T)"
    },
    "Sulphide (HS-/S2-)": {
        "action_level": 0.02,
        "escalation_level": 0.2,
        "why_it_matters": "Rapid anodic oxidation; fouling.",
        "citation": "HS- oxidation to S0; poisoning electrodes. (Jiang et al., 2017, J. Hazard. Mater.)"
    },
    "Cyanide (CN-)": {
        "action_level": 0.005,
        "escalation_level": 0.02,
        "why_it_matters": "Oxidized; CNCl with Cl-.",
        "citation": "Electrochemical CN oxidation. (Rodriguez et al., 2002, Ind. Eng. Chem. Res.)"
    },
    "Nitrate (NO3- as N)": {
        "action_level": 2.0,
        "escalation_level": 10.0,
        "why_it_matters": "Competes with HER; reduced to NH3/NO/N2O.",
        "citation": "Nitrate reduction well studied. (Rosca et al., 2009, Chem. Rev.)"
    },
    "Nitrite (NO2- as N)": {
        "action_level": 0.1,
        "escalation_level": 1.0,
        "why_it_matters": "Cathodic reduction products NO/N2O/NH3.",
        "citation": "Nitrite reduction pathways documented. (Dima et al., 2003, J. Electroanal. Chem.)"
    },
    "Ammonium (NH4+)": {
        "action_level": 0.5,
        "escalation_level": 2.0,
        "why_it_matters": "Forms chloramines with HOCl from Cl-.",
        "citation": "Chloramine formation kinetics at neutral pH. (Vikesland et al., 2001, ES&T)"
    },
    "Phosphate (PO43-)": {
        "action_level": 3.0,
        "escalation_level": 8.0,
        "why_it_matters": "Ca/Mg phosphate scaling.",
        "citation": "Electrochemically induced phosphate precipitation. (Snoeyink & Jenkins, 1980)"
    },
    "Carbonate/Bicarbonate": {
        "action_level": 150.0,
        "escalation_level": 300.0,
        "why_it_matters": "Buffering; CaCO3 scaling possible.",
        "citation": "CO2/HCO3- impacts scaling, OER efficiency. (Li et al., 2020, Nat. Catal.)"
    },
    "Calcium (Ca2+)": {
        "action_level": 40.0,
        "escalation_level": 100.0,
        "why_it_matters": "CaCO3/CaSO4 scale.",
        "citation": "Scaling tendency known. (Stumm & Morgan, 1996, Aquatic Chemistry)"
    },
    "Magnesium (Mg2+)": {
        "action_level": 20.0,
        "escalation_level": 60.0,
        "why_it_matters": "MgCO3/Mg-phosphate scaling.",
        "citation": "Scaling risk with phosphate. (Stumm & Morgan, 1996)"
    },
    "Barium (Ba2+)": {
        "action_level": 0.03,
        "escalation_level": 0.1,
        "why_it_matters": "BaSO4 insoluble scale.",
        "citation": "BaSO4 precipitation well documented. (Snoeyink & Jenkins, 1980)"
    },
    "Strontium (Sr2+)": {
        "action_level": 0.1,
        "escalation_level": 0.3,
        "why_it_matters": "SrSO4/SrCO3 scaling.",
        "citation": "Sr salts scale similarly to Ba. (Stumm & Morgan, 1996)"
    },
    "Iron (Fe2+/Fe3+)": {
        "action_level": 0.05,
        "escalation_level": 0.2,
        "why_it_matters": "Soluble at neutral - electrode fouling.",
        "citation": "Fe redox cycling and fouling documented. (Zhang et al., 2016)"
    },
    "Manganese (Mn2+)": {
        "action_level": 0.02,
        "escalation_level": 0.05,
        "why_it_matters": "Oxidized to MnO2 (insulating).",
        "citation": "Mn2+ - MnO2 passivation. (Post, 1999, Water Res.)"
    },
    "Copper (Cu2+)": {
        "action_level": 0.02,
        "escalation_level": 0.1,
        "why_it_matters": "Cathodic plating.",
        "citation": "Cu deposition observed. (Fan et al., 2013, Electrochim. Acta)"
    },
    "Nickel (Ni2+)": {
        "action_level": 0.03,
        "escalation_level": 0.1,
        "why_it_matters": "Deposition/poisoning.",
        "citation": "Ni hydroxide deposition. (Biesinger et al., 2009)"
    },
    "Lead (Pb2+)": {
        "action_level": 0.003,
        "escalation_level": 0.01,
        "why_it_matters": "Cathodic deposition.",
        "citation": "Pb deposition. (Hu et al., 2003, Water Res.)"
    },
    "Cadmium (Cd2+)": {
        "action_level": 0.001,
        "escalation_level": 0.005,
        "why_it_matters": "Deposition.",
        "citation": "Cd2+ electroreduction documented. (Chen et al., 2000)"
    },
    "Mercury (Hg2+)": {
        "action_level": 0.0005,
        "escalation_level": 0.001,
        "why_it_matters": "Amalgams.",
        "citation": "Hg deposition/amalgam. (Liu et al., 2002, ES&T)"
    }
}


def get_status(concentration, action_level, escalation_level):
    """Determine the status based on concentration levels."""
    if concentration >= escalation_level:
        return "escalation"
    elif concentration >= action_level:
        return "action"
    else:
        return "safe"


def get_status_color(status):
    """Return color based on status."""
    if status == "escalation":
        return STATUS_RED
    elif status == "action":
        return STATUS_ORANGE
    else:
        return STATUS_GREEN


def get_status_message(status, analyte, concentration, data):
    """Generate status message based on the concentration level."""
    if status == "safe":
        return f"Concentration is within safe limits (below {data['action_level']} mg/L action level)."
    elif status == "action":
        return f"ACTION LEVEL REACHED: This could start happening - {data['why_it_matters']} Reference: {data['citation']}"
    else:
        return f"ESCALATION LEVEL REACHED: This is serious and green hydrogen production should be stopped. {data['why_it_matters']} Reference: {data['citation']}"


def create_heatmap(results_df):
    """Create a heatmap visualization for the results."""
    if results_df.empty:
        return None
    
    # Create color mapping
    color_map = {
        "safe": 0,
        "action": 0.5,
        "escalation": 1
    }
    
    results_df["color_value"] = results_df["status"].map(color_map)
    
    # Create heatmap
    heatmap_customdata = [[
        [concentration, status_label, action_level, escalation_level, times_threshold]
        for concentration, status_label, action_level, escalation_level, times_threshold in zip(
            results_df["concentration"],
            results_df["status_label"],
            results_df["action_level"],
            results_df["escalation_level"],
            results_df["times_threshold"]
        )
    ]]
    
    fig = go.Figure(data=go.Heatmap(
        z=[[color_map[s] for s in results_df["status"]]],
        x=results_df["analyte"],
        y=["Status"],
        colorscale=[
            [0, STATUS_GREEN],
            [0.5, STATUS_ORANGE],
            [1, STATUS_RED]
        ],
        showscale=False,
        hovertemplate=(
            "<b>%{x}</b>"
            "<br>Concentration: %{customdata[0]:.4f} mg/L"
            "<br>Action Level: %{customdata[2]:.4f} mg/L"
            "<br>Escalation Level: %{customdata[3]:.4f} mg/L"
            "<br>Multiplier: %{customdata[4]:.1f}x (vs action level)"
            "<br>Status: %{customdata[1]}"
            "<extra></extra>"
        ),
        customdata=heatmap_customdata
    ))
    
    # Add text annotations
    for i, row in results_df.iterrows():
        fig.add_annotation(
            x=row["analyte"],
            y="Status",
            text=f"{row['times_threshold']:.1f}x" if row['times_threshold'] >= 1 else "OK",
            showarrow=False,
            font=dict(color=TEXT_BLACK, size=12, family="Hind")
        )
    
    fig.update_layout(
        title=dict(
            text="Water Quality vs Threshold Levels",
            font=dict(size=18, color=TEXT_BLACK, family="Hind")
        ),
        xaxis=dict(
            title=dict(text="Analyte", font=dict(size=12, color=TEXT_BLACK, family="Hind")),
            tickangle=45,
            tickfont=dict(size=10, color=TEXT_BLACK, family="Hind")
        ),
        yaxis=dict(
            title=dict(text="", font=dict(size=12, color=TEXT_BLACK, family="Hind")),
            tickfont=dict(size=12, color=TEXT_BLACK, family="Hind")
        ),
        height=300,
        margin=dict(l=50, r=50, t=50, b=150),
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_BLACK, family="Hind")
    )
    
    return fig


def create_bar_chart(results_df):
    """Create a bar chart comparing concentrations to thresholds."""
    if results_df.empty:
        return None
    
    fig = go.Figure()
    
    # Add bars for user concentration
    fig.add_trace(go.Bar(
        name="Your Concentration",
        x=results_df["analyte"],
        y=results_df["concentration"],
        marker_color=[get_status_color(s) for s in results_df["status"]],
        hovertemplate="<b>%{x}</b><br>Your Concentration: %{y:.4f} mg/L<extra></extra>"
    ))
    
    # Add line for action level
    fig.add_trace(go.Scatter(
        name="Action Level",
        x=results_df["analyte"],
        y=results_df["action_level"],
        mode="markers+lines",
        marker=dict(symbol="diamond", size=10, color=STATUS_ORANGE),
        line=dict(color=STATUS_ORANGE, dash="dash"),
        hovertemplate="<b>%{x}</b><br>Action Level: %{y:.4f} mg/L<extra></extra>"
    ))
    
    # Add line for escalation level
    fig.add_trace(go.Scatter(
        name="Escalation Level",
        x=results_df["analyte"],
        y=results_df["escalation_level"],
        mode="markers+lines",
        marker=dict(symbol="x", size=10, color=STATUS_RED),
        line=dict(color=STATUS_RED, dash="dot"),
        hovertemplate="<b>%{x}</b><br>Escalation Level: %{y:.4f} mg/L<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text="Concentration Comparison",
            font=dict(size=18, color=TEXT_BLACK, family="Hind")
        ),
        xaxis=dict(
            title=dict(text="Analyte", font=dict(size=12, color=TEXT_BLACK, family="Hind")),
            tickangle=45,
            tickfont=dict(size=10, color=TEXT_BLACK, family="Hind")
        ),
        yaxis=dict(
            title=dict(text="Concentration (mg/L)", font=dict(size=12, color=TEXT_BLACK, family="Hind")),
            tickfont=dict(size=10, color=TEXT_BLACK, family="Hind"),
            type="log"
        ),
        barmode="group",
        height=400,
        margin=dict(l=50, r=50, t=50, b=150),
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family="Hind", color=TEXT_BLACK)
        ),
        font=dict(color=TEXT_BLACK, family="Hind")
    )
    
    return fig


# Initialize session state
if "analyte_entries" not in st.session_state:
    st.session_state.analyte_entries = [{"analyte": None, "concentration": None}]

if "results" not in st.session_state:
    st.session_state.results = []


# Header with logo
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try:
        st.image("logo.png", width=100)
    except:
        st.markdown(f"<div style='background-color:{PRIMARY_GREEN}; padding:20px; border-radius:10px; text-align:center;'><span style='font-size:24px; font-weight:bold; color:{DARK_GREY};'>H1</span></div>", unsafe_allow_html=True)

with col_title:
    st.markdown(f"""
    <div>
        <h1 style='color:{PRIMARY_GREEN}; margin-bottom:0; font-family:Hind;'>Electrolyser Wastewater Analysis</h1>
        <p style='color:{LIGHT_GREY}; font-family:Hind;'>Evaluate your wastewater quality for green hydrogen production</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar for pH selection
with st.sidebar:
    st.markdown(f"<h2 style='color:{PRIMARY_GREEN}; font-family:Hind;'>Configuration</h2>", unsafe_allow_html=True)
    
    ph_type = st.selectbox(
        "Select Wastewater pH Type",
        options=["Alkaline pH", "Neutral pH"],
        index=1,
        help="Select whether your wastewater is alkaline or neutral in pH"
    )
    
    # Get the appropriate data based on pH selection
    current_data = ALKALINE_DATA if ph_type == "Alkaline pH" else NEUTRAL_DATA
    analyte_options = list(current_data.keys())
    
    st.markdown("---")
    st.markdown(f"<h3 style='color:{PRIMARY_GREEN}; font-family:Hind;'>Legend</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='color:white; font-family:Hind;'>
        <div style='display:flex; align-items:center; margin:10px 0;'>
            <div style='width:20px; height:20px; background-color:{STATUS_GREEN}; border-radius:4px; margin-right:10px;'></div>
            <span>Safe - Below action level</span>
        </div>
        <div style='display:flex; align-items:center; margin:10px 0;'>
            <div style='width:20px; height:20px; background-color:{STATUS_ORANGE}; border-radius:4px; margin-right:10px;'></div>
            <span>Caution - At action level</span>
        </div>
        <div style='display:flex; align-items:center; margin:10px 0;'>
            <div style='width:20px; height:20px; background-color:{STATUS_RED}; border-radius:4px; margin-right:10px;'></div>
            <span>Critical - At escalation level</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"<p style='color:{LIGHT_GREY}; font-size:12px; font-family:Hind;'>HydroStar Europe Ltd.</p>", unsafe_allow_html=True)

# Main content area
st.markdown(f"<h2 style='color:{SECONDARY_GREEN}; font-family:Hind;'>Enter Analyte Concentrations</h2>", unsafe_allow_html=True)

# Instructions
st.markdown(f"""
<div style='background-color:white; padding:15px; border-radius:8px; border-left:5px solid {PRIMARY_GREEN}; margin-bottom:20px;'>
    <p style='margin:0; font-family:Hind; color:{DARK_GREY};'>
        Select analytes from the dropdown and enter their concentrations in mg/L. 
        Click the <strong>+ Add Analyte</strong> button to add more entries. 
        Click <strong>Analyze</strong> when ready to see results.
    </p>
</div>
""", unsafe_allow_html=True)

# Analyte entry form
for i, entry in enumerate(st.session_state.analyte_entries):
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        # Filter out already selected analytes
        selected_analytes = [e["analyte"] for j, e in enumerate(st.session_state.analyte_entries) if j != i and e["analyte"]]
        available_options = ["-- Select Analyte --"] + [a for a in analyte_options if a not in selected_analytes]
        
        current_selection = entry["analyte"] if entry["analyte"] in available_options else "-- Select Analyte --"
        
        selected = st.selectbox(
            f"Analyte {i+1}",
            options=available_options,
            index=available_options.index(current_selection) if current_selection in available_options else 0,
            key=f"analyte_{i}",
            label_visibility="collapsed"
        )
        
        if selected != "-- Select Analyte --":
            st.session_state.analyte_entries[i]["analyte"] = selected
        else:
            st.session_state.analyte_entries[i]["analyte"] = None
    
    with col2:
        concentration = st.number_input(
            f"Concentration {i+1} (mg/L)",
            min_value=0.0,
            value=entry["concentration"],
            format="%.6f",
            key=f"concentration_{i}",
            placeholder="Input analyte concentration",
            label_visibility="collapsed"
        )
        st.session_state.analyte_entries[i]["concentration"] = concentration
    
    with col3:
        if len(st.session_state.analyte_entries) > 1:
            if st.button("X", key=f"remove_{i}", help="Remove this entry"):
                st.session_state.analyte_entries.pop(i)
                st.rerun()

# Add analyte button
col_add, col_analyze, col_clear = st.columns([1, 1, 1])

with col_add:
    if st.button("+ Add Analyte", use_container_width=True):
        st.session_state.analyte_entries.append({"analyte": None, "concentration": None})
        st.rerun()

with col_analyze:
    analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

with col_clear:
    if st.button("Clear All", use_container_width=True):
        st.session_state.analyte_entries = [{"analyte": None, "concentration": None}]
        st.session_state.results = []
        st.rerun()

# Analysis and Results
if analyze_clicked:
    valid_entries = [
        e for e in st.session_state.analyte_entries
        if e["analyte"] is not None and e["concentration"] is not None and e["concentration"] > 0
    ]
    
    if not valid_entries:
        st.warning("Please select at least one analyte and enter a concentration greater than 0.")
    else:
        results = []
        for entry in valid_entries:
            analyte = entry["analyte"]
            concentration = entry["concentration"]
            data = current_data[analyte]
            
            status = get_status(concentration, data["action_level"], data["escalation_level"])
            
            # Calculate times above action level threshold
            times_threshold = concentration / data["action_level"]
            
            results.append({
                "analyte": analyte,
                "concentration": concentration,
                "action_level": data["action_level"],
                "escalation_level": data["escalation_level"],
                "status": status,
                "status_label": status.capitalize(),
                "times_threshold": times_threshold,
                "why_it_matters": data["why_it_matters"],
                "citation": data["citation"],
                "message": get_status_message(status, analyte, concentration, data)
            })
        
        st.session_state.results = results

# Display results
if st.session_state.results:
    st.markdown("---")
    st.markdown(f"<h2 style='color:{SECONDARY_GREEN}; font-family:Hind;'>Analysis Results</h2>", unsafe_allow_html=True)
    
    results_df = pd.DataFrame(st.session_state.results)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    safe_count = len(results_df[results_df["status"] == "safe"])
    action_count = len(results_df[results_df["status"] == "action"])
    escalation_count = len(results_df[results_df["status"] == "escalation"])
    total_count = len(results_df)
    
    with col1:
        st.markdown(f"""
        <div style='background-color:white; padding:20px; border-radius:10px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <p style='color:{TEXT_BLACK}; margin:0; font-family:Hind;'>Total Analytes</p>
            <p style='font-size:36px; font-weight:bold; color:{DARK_GREY}; margin:0; font-family:Hind;'>{total_count}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background-color:white; padding:20px; border-radius:10px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <p style='color:{TEXT_BLACK}; margin:0; font-family:Hind;'>Safe</p>
            <p style='font-size:36px; font-weight:bold; color:{STATUS_GREEN}; margin:0; font-family:Hind;'>{safe_count}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background-color:white; padding:20px; border-radius:10px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <p style='color:{TEXT_BLACK}; margin:0; font-family:Hind;'>Action Level</p>
            <p style='font-size:36px; font-weight:bold; color:{STATUS_ORANGE}; margin:0; font-family:Hind;'>{action_count}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background-color:white; padding:20px; border-radius:10px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <p style='color:{TEXT_BLACK}; margin:0; font-family:Hind;'>Escalation Level</p>
            <p style='font-size:36px; font-weight:bold; color:{STATUS_RED}; margin:0; font-family:Hind;'>{escalation_count}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Overall status message
    if escalation_count > 0:
        st.markdown(f"""
        <div style='background-color:#ffebee; padding:20px; border-radius:10px; border-left:5px solid {STATUS_RED}; margin-bottom:20px;'>
            <h3 style='color:{STATUS_RED}; margin:0 0 10px 0; font-family:Hind;'>CRITICAL: Production Should Be Stopped</h3>
            <p style='margin:0; font-family:Hind; color:{DARK_GREY};'>
                One or more analytes have reached escalation levels. Green hydrogen production should be halted 
                until wastewater treatment addresses these concentrations.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif action_count > 0:
        st.markdown(f"""
        <div style='background-color:#fff3e0; padding:20px; border-radius:10px; border-left:5px solid {STATUS_ORANGE}; margin-bottom:20px;'>
            <h3 style='color:{STATUS_ORANGE}; margin:0 0 10px 0; font-family:Hind;'>CAUTION: Action Required</h3>
            <p style='margin:0; font-family:Hind; color:{DARK_GREY};'>
                One or more analytes have reached action levels. Monitor closely and consider treatment 
                to prevent escalation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color:#e8f5e9; padding:20px; border-radius:10px; border-left:5px solid {STATUS_GREEN}; margin-bottom:20px;'>
            <h3 style='color:{STATUS_GREEN}; margin:0 0 10px 0; font-family:Hind;'>ALL CLEAR: Safe for Production</h3>
            <p style='margin:0; font-family:Hind; color:{DARK_GREY};'>
                All analytes are within safe limits. Your wastewater is suitable for green hydrogen production.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Visualizations
    st.markdown(f"<h3 style='color:{SECONDARY_GREEN}; font-family:Hind;'>Visualizations</h3>", unsafe_allow_html=True)
    
    # Heatmap
    heatmap_fig = create_heatmap(results_df)
    if heatmap_fig:
        st.plotly_chart(heatmap_fig, use_container_width=True)
    
    # Bar chart
    bar_fig = create_bar_chart(results_df)
    if bar_fig:
        st.plotly_chart(bar_fig, use_container_width=True)
    
    # Detailed results
    st.markdown(f"<h3 style='color:{SECONDARY_GREEN}; font-family:Hind;'>Detailed Results</h3>", unsafe_allow_html=True)
    
    for result in st.session_state.results:
        status = result["status"]
        if status == "safe":
            card_class = "status-safe"
            icon = "OK"
        elif status == "action":
            card_class = "status-action"
            icon = "!"
        else:
            card_class = "status-escalation"
            icon = "X"
        
        st.markdown(f"""
        <div class='status-card {card_class}'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                <div>
                    <h4 style='margin:0 0 5px 0; color:{DARK_GREY}; font-family:Hind;'>{result["analyte"]}</h4>
                    <p style='margin:0; font-family:Hind;'>
                        <strong>Your Concentration:</strong> {result["concentration"]:.6f} mg/L | 
                        <strong>Action Level:</strong> {result["action_level"]:.4f} mg/L | 
                        <strong>Escalation Level:</strong> {result["escalation_level"]:.4f} mg/L
                    </p>
                    <p style='margin:10px 0 0 0; font-family:Hind; font-style:italic;'>{result["message"]}</p>
                </div>
                <div style='font-size:24px; font-weight:bold; color:{get_status_color(status)};'>{icon}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; color:{LIGHT_GREY}; font-family:Hind; padding:20px;'>
    <p style='margin:0;'>HydroStar Europe Ltd. </p>
    <p style='margin:5px 0 0 0; font-size:12px;'>For inquiries, contact: domanique@hydrostar-eu.com | www.hydrostar-eu.com</p>
</div>
""", unsafe_allow_html=True)
