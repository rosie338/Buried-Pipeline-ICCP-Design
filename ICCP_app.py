import numpy as np
import math
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

st.title("ICCP Pipeline Calculator")

#================
#Input parameters
#================
st.header("Input parameters")

pipeline_od = st.number_input(
    "Pipeline OD (m)",
    value=1.6
)

wall_thickness = st.number_input(
    "Wall thickness (m)",
    value=0.0127
)

pipeline_length = st.number_input(
    "Pipeline length (m)",
    value=25693.0
)

steel_resistivity = st.number_input(
    "Steel resistivity (Ωm)",
    value=1.8e-7,
    format="%.2e"
)

soil_resistivity = st.number_input(
    "Soil resistivity (Ωm)",
    value=162.0
)

coating_quality = st.number_input(
    "Coating quality",
    value=10000.0
)

design_current_density = st.number_input(
    "Design current density (A/m²)",
    value=1e-5,
    format="%.2e"
)

coating_bd_factor = st.number_input(
    "Coating breakdown factor",
    value=1.15
)

natural_potential = st.number_input(
    "Natural potential (V)",
    value=-0.5
)

protection_criterion = st.number_input(
    "Protection criterion (V)",
    value=-0.85
)

over_polarisation_limit = st.number_input(
    "Over-polarisation limit (V)",
    value=-1.2
)

anode_separation = st.number_input(
    "Anode-pipeline distance (m)",
    value=25.0
)

back_emf = st.number_input(
    "Back EMF allowance (V)",
    value=2.0
)

cable_resistance = st.number_input(
    "Cable resistance per installation (Ω)",
    value=0.2
)

#============
#Dictionary
#============
parameters = {
    "pipeline_od": pipeline_od,
    "wall_thickness": wall_thickness,
    "pipeline_length": pipeline_length,
    "steel_resistivity": steel_resistivity,
    "soil_resistivity": soil_resistivity,
    "coating_quality": coating_quality,
    "design_current_density": design_current_density,
    "coating_bd_factor": coating_bd_factor,
    "Natural potential": natural_potential,
    "Protection criterion": protection_criterion,
    "Over polarisation limit": over_polarisation_limit,
    "Anode separation-pipeline": anode_separation,
    "Back EMF allowance": back_emf,
    "cable res per instal": cable_resistance
}

#====================
#Chainages dictionary
#====================
st.header("Anode Installation Chainages")

chainage_data = {
    "Chainage (km)": [
        3.44,
        8.33,
        10.20,
        15.64,
        20.91,
        23.60,
        25.693
    ],
    "Use": [
        True,
        True,
        True,
        True,
        True,
        True,
        True
    ]
}

#================================
#Making chainage values tickboxes
#================================
chainage_df = pd.DataFrame(chainage_data)

edited_chainages = st.data_editor(
    chainage_df,
    column_config={
        "Use": st.column_config.CheckboxColumn(
            "Use installation",
            help="Select the anode installations to use"
        )
    },
    hide_index=True
)

#===============================
#Taking non-zero chainage values
#===============================
non_zero_icv = edited_chainages.loc[
    edited_chainages["Use"],
    "Chainage (km)"
].to_numpy()

#============
#Calculations
#============
st.header("Calculated Parameters")

pipeline_sa = math.pi *  parameters["pipeline_od"] * parameters["pipeline_length"]

Itotal = pipeline_sa * parameters["design_current_density"] * parameters["coating_bd_factor"]

pipeline_unit_res = parameters["steel_resistivity"] / (math.pi * (parameters["pipeline_od"] - parameters["wall_thickness"]) * parameters["wall_thickness"])

insulation_res = parameters["coating_quality"] * parameters["soil_resistivity"] / 10

transversal_insulating_res = insulation_res/(math.pi * parameters["pipeline_od"])

attenuation_coeff = math.sqrt(pipeline_unit_res/transversal_insulating_res)

polar_res = ((parameters["Natural potential"]) - (parameters["Protection criterion"]))/ parameters["design_current_density"]

current_density_lim = (parameters["Natural potential"] - parameters["Over polarisation limit"])/polar_res

current_per_installation = Itotal/len(non_zero_icv)


results = pd.DataFrame({
    "Parameter": [
        "Pipeline Surface Area",
        "Total Current Required",
        "Pipeline Unit Resistance",
        "Insulation Resistance",
        "Transversal Insulating Resistance",
        "Attenuation Coefficient",
        "Polarisation Resistance",
        "Current Density Limit",
        "Current Per Installation",
    ],
    "Result":[
        pipeline_sa, 
        Itotal, 
        pipeline_unit_res,
        insulation_res,
        transversal_insulating_res,
        attenuation_coeff,
        polar_res,
        current_density_lim,
        current_per_installation,
        ],
        "Unit": [
            "m²",
            "A",
            "Ω/m",
            "Ωm²",
            "Ωm",
            "m⁻¹",
            "Ωm²",
            "Am⁻²",
            "A",
            ]})

st.dataframe(results, hide_index = True, use_container_width=True)

#======================
#Potential calculations
#======================
#st.header("Earth Potential Calculations at Given Chainage and Anode-Pipeline Distance")

#zeta = st.number_input(
#    "Input Chainage from active anode bed (km)",
#    value=20.91)

def earth_potential_rise(zeta, d):
    distance = np.sqrt(((zeta*1000) - np.array(non_zero_icv) * 1000)**2 + d**2 )
    contribution = (parameters["soil_resistivity"] * current_per_installation / (2 * np.pi * distance))
    return np.sum(contribution) 
Ved = earth_potential_rise(20.91, parameters["Anode separation-pipeline"]) #km, m

def int_sum(d):
    innerexp = np.arcsinh(((parameters["pipeline_length"])-(np.array(non_zero_icv)))/d) + np.arcsinh((np.array(non_zero_icv)/d))
    n_intsum = ((parameters["soil_resistivity"]*current_per_installation)/(2*np.pi))*(innerexp)
    return np.sum(n_intsum)
intsum = int_sum(parameters["Anode separation-pipeline"])

pipe_metal_pot =( intsum - (Itotal * transversal_insulating_res))/ parameters["pipeline_length"]

current_density = ((Ved - pipe_metal_pot)/insulation_res) *1000


potential_resuts = ({
    "Parameters": [
        "Earth Potential Rise",
        "Integral of Earth Potential Rise over Pipeline Length",
        "Pipe Metal Potential Relative to Remote Earth",
        "Current Density",
        ],
    "Value": [
        Ved,
        intsum,
        pipe_metal_pot,
        current_density,
        ],
    "Units": [
        "V",
        " ",
        "V",
        "mAm⁻²",
        ]
                     })
#st.dataframe(potential_resuts, hide_index = True, use_container_width=True)

#======================
#Deriving data for plot
#======================
st.header("IR Free Potential")

x = np.linspace(0, (parameters["pipeline_length"] + 5), 500)
d = parameters["Anode separation-pipeline"] #(set to equal input from above)
Eirf_values = []
for x_value in x:
    distance = np.sqrt(((x_value) - np.array(non_zero_icv) *1000)**2 + d**2)
    contribution = (parameters["soil_resistivity"] * current_per_installation / (2 * np.pi * distance))
    Ved = np.sum(contribution)
    pipe_metal_potential = (intsum - Itotal *transversal_insulating_res)/parameters["pipeline_length"]
    j = (Ved- pipe_metal_potential)/insulation_res
    Eirf = parameters["Natural potential"] - (j*polar_res)
    Eirf_values.append(Eirf)

#==============
#Plotting graph
#==============

fig = go.Figure()

# ============================================================
# Eirf curve
# ============================================================
fig.add_trace(
    go.Scatter(
        x=x / 1000,
        y=Eirf_values,
        mode="lines",
        line=dict(
            color="blue",
            width=2.5
        ),
        name="E<sub>irf</sub>(X)"
    )
)

# ============================================================
# Protection criterion
# ============================================================
fig.add_trace(
    go.Scatter(
        x=x / 1000,
        y=np.full_like(x, parameters["Protection criterion"]),
        mode="lines",
        line=dict(
            color="green",
            width=1.8,
            dash="dash"
        ),
        name="Protection criterion = -0.85 V"
    )
)

# ============================================================
# Over-polarisation limit
# ============================================================
fig.add_trace(
    go.Scatter(
        x=x / 1000,
        y=np.full_like(x, parameters["Over polarisation limit"]),
        mode="lines",
        line=dict(
            color="red",
            width=1.8,
            dash="dash"
        ),
        name="Over-polarisation limit = -1.2 V"
    )
)

# ============================================================
# Layout
# ============================================================
fig.update_layout(

    title=dict(
        text="IR-Free Pipe-to-Soil Potential Along Pipeline",
        x=0.5,
        xanchor="center",
        font=dict(
            size=20
        )
    ),

    xaxis=dict(
        title=dict(
            text="Pipeline chainage (km)",
            font=dict(size=15)
        ),
        tickfont=dict(size=12),
        showgrid=True,
        gridcolor="lightgray",
        zeroline=False
    ),

    yaxis=dict(
        title=dict(
            text="IR-Free Pipe-to-Soil Potential, E<sub>irf</sub> (V)",
            font=dict(size=15)
        ),
        tickfont=dict(size=12),
        showgrid=True,
        gridcolor="lightgray",
        zeroline=False
    ),

    legend=dict(
        title="",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(size=12)
    ),

    hovermode="x unified",

    template="simple_white",

    margin=dict(
        l=80,
        r=40,
        t=100,
        b=80
    ),

    height=600
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="eirf_graph"
)

#================
#Finding Minimums
#================
min_index = np.argmin(Eirf_values)

minE = Eirf_values[min_index]

x_at_min = x[min_index]

minimum_points = ({
    "Parameters": [
        "Minimum IR Free Potential/Worst E",
        "Chainage at Minimum  E<sub>irf</sub>",
        ],
    "Value": [
        minE,
        x_at_min,   
        ],
    "Units": [
        "V",
        "km",
        ]
                     })
#st.dataframe(minimum_points, hide_index = True, use_container_width=True)


#=========================
#Deriving data for 3D plot
#=========================
x = np.linspace(0, parameters["pipeline_length"] + 5, 600)

d = np.linspace(5, 200, 600)

X, D = np.meshgrid(x, d)
Eirf_values2 = np.zeros((len(d), len(x)))

def int_sum(d):
    CH = np.array(non_zero_icv) * 1000
    Length = parameters["pipeline_length"]
    innerexp = (np.arcsinh((Length - CH) / d) + np.arcsinh(CH / d))
    n_intsum = (parameters["soil_resistivity"] * current_per_installation / (2 * np.pi)) * innerexp
    return np.sum(n_intsum)

for i, d_value in enumerate(d):
    intsum = int_sum(d_value)

    pipe_metal_potential = (intsum - Itotal * transversal_insulating_res) / parameters["pipeline_length"]

    for j, x_value in enumerate(x):
        distance = np.sqrt((x_value - np.array(non_zero_icv) * 1000)**2 + d_value**2)

        contribution = (parameters["soil_resistivity"] * current_per_installation / (2 * np.pi * distance))

        Ved = np.sum(contribution)

        current_density = (Ved - pipe_metal_potential) / insulation_res

        Eirf2 = (parameters["Natural potential"]- current_density * polar_res)

        Eirf_values2[i, j] = Eirf2

worst_index = np.argmin(Eirf_values2, axis=1)
x_worst = X[np.arange(len(d)), worst_index]
E_worst = Eirf_values2[np.arange(len(d)), worst_index]



fig3d = go.Figure()

# ============================================================
# Eirf surface
# ============================================================
fig3d.add_trace(
    go.Surface(
        x=X / 1000,
        y=D,
        z=Eirf_values2,
        name=r"$E_{irf}$",
        colorbar=dict(
            title="E<sub>irf</sub> (V)"
        )
    )
)

# ============================================================
# Protection criterion surface
# ============================================================
protection = np.full_like(
    X,
    parameters["Protection criterion"]
)

fig3d.add_trace(
    go.Surface(
        x=X / 1000,
        y=D,
        z=protection,
        name="Protection criterion",
        opacity=0.35,
        showscale=False
    )
)

# ============================================================
# Over-polarisation limit surface
# ============================================================
over_polarisation = np.full_like(
    X,
    parameters["Over polarisation limit"]
)

fig3d.add_trace(
    go.Surface(
        x=X / 1000,
        y=D,
        z=over_polarisation,
        name="Over-polarisation limit",
        opacity=0.35,
        showscale=False
    )
)

# ============================================================
# Layout
# ============================================================
fig3d.update_layout(

    title=dict(
        text="IR-Free Pipe-to-Soil Potential Along Pipeline",
        x=0.5,
        xanchor="center",
        font=dict(size=20)
    ),

    scene=dict(

        xaxis=dict(
            title=dict(
                text="Pipeline chainage (km)",
                font=dict(size=15)
            ),
            tickfont=dict(size=11),
            showgrid=True,
            gridcolor="lightgray"
        ),

        yaxis=dict(
            title=dict(
                text="Anode-pipeline distance (m)",
                font=dict(size=15)
            ),
            tickfont=dict(size=11),
            showgrid=True,
            gridcolor="lightgray"
        ),

        zaxis=dict(
            title=dict(
                text="E<sub>irf</sub> (V)",
                font=dict(size=15)
            ),
            tickfont=dict(size=11),
            showgrid=True,
            gridcolor="lightgray"
        )
    ),

    template="simple_white",

    height=750,

    margin=dict(
        l=20,
        r=20,
        t=100,
        b=20
    )
)

st.plotly_chart(
    fig3d,
    use_container_width=True,
    key="eirf_3d_graph"
)

fig2 = go.Figure()

# ============================================================
# Worst-case E curve
# ============================================================
fig2.add_trace(
    go.Scatter(
        x=d,
        y=E_worst,
        mode="lines",
        line=dict(
            color="blue",
            width=2.5
        ),
        name=r" E<sub>irf, worst</sub>"
    )
)

# ============================================================
# Protection criterion
# ============================================================
fig2.add_trace(
    go.Scatter(
        x=d,
        y=np.full_like(d, parameters["Protection criterion"]),
        mode="lines",
        line=dict(
            color="green",
            width=1.8,
            dash="dash"
        ),
        name="Protection criterion = -0.85 V"
    )
)

# ============================================================
# Over-polarisation limit
# ============================================================
fig2.add_trace(
    go.Scatter(
        x=d,
        y=np.full_like(d, parameters["Over polarisation limit"]),
        mode="lines",
        line=dict(
            color="red",
            width=1.8,
            dash="dash"
        ),
        name="Over-polarisation limiT = -1.2 V"
    )
)

# ============================================================
# Layout
# ============================================================
fig2.update_layout(

    title=dict(
        text="Worst-Case IR-Free Pipe-to-Soil Potential vs Anode-Pipeline Distance",
        x=0.5,
        xanchor="center",
        font=dict(
            size=20
        )
    ),

    xaxis=dict(
        title=dict(
            text="Anode-pipeline distance (m)",
            font=dict(size=15)
        ),
        tickfont=dict(size=12),
        showgrid=True,
        gridcolor="lightgray",
        zeroline=False
    ),

    yaxis=dict(
        title=dict(
            text="E<sub>irf</sub> (V)",
            font=dict(size=15)
        ),
        tickfont=dict(size=12),
        showgrid=True,
        gridcolor="lightgray",
        zeroline=False
    ),

    legend=dict(
        title="",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(size=12)
    ),

    hovermode="x unified",

    template="simple_white",

    margin=dict(
        l=80,
        r=40,
        t=100,
        b=80
    ),

    height=600
)

st.plotly_chart(
    fig2,
    use_container_width=True,
    key="eworst_graph"
)