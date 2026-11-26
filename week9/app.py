from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "world_happiness_2023.csv"
df = pd.read_csv(DATA_PATH)

st.set_page_config(
    page_title="World Happiness Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 World Happiness Dashboard")
st.caption("World Happiness Report 2023 | 137 countries")

with st.sidebar:
    st.header("Filters")
    regions = ["All Regions"] + sorted(df["Region"].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Top countries", min_value=5, max_value=25, value=15)

filtered = (
    df.copy()
    if selected_region == "All Regions"
    else df.loc[df["Region"] == selected_region].copy()
)

global_mean = df["Happiness_Score"].mean()
regional_mean = filtered["Happiness_Score"].mean()
leader = filtered.loc[filtered["Happiness_Score"].idxmax(), "Country"]
top = filtered.nlargest(top_n, "Happiness_Score").sort_values("Happiness_Score")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Countries", f"{len(filtered):,}")
k2.metric("Mean happiness", f"{regional_mean:.2f}", f"{regional_mean - global_mean:+.2f} vs global")
k3.metric("Highest score", f"{filtered['Happiness_Score'].max():.2f}")
k4.metric("Highest-scoring country", leader)

st.divider()

fig_top = px.bar(
    top,
    x="Happiness_Score",
    y="Country",
    orientation="h",
    text="Happiness_Score",
    labels={"Happiness_Score": "Happiness score (0–10)", "Country": ""},
    title=f"Top {len(top)} happiness scores — {selected_region}",
    template="plotly_white",
    color="Happiness_Score",
    color_continuous_scale="Blues"
)
fig_top.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
fig_top.update_layout(
    height=max(520, 30 * len(top)),
    coloraxis_showscale=False,
    margin=dict(l=10, r=55, t=65, b=35),
    xaxis=dict(range=[0, min(10, top["Happiness_Score"].max() + 0.9)])
)
st.plotly_chart(fig_top, width="stretch")

st.divider()

diverging = filtered[["Country", "Happiness_Score"]].copy()
diverging["Difference_from_global_mean"] = diverging["Happiness_Score"] - global_mean
diverging = diverging.sort_values("Difference_from_global_mean")
limit = max(abs(diverging["Difference_from_global_mean"].min()),
            abs(diverging["Difference_from_global_mean"].max()))

fig_diverging = px.scatter(
    diverging,
    x="Difference_from_global_mean",
    y="Country",
    color="Difference_from_global_mean",
    color_continuous_scale="RdBu",
    range_color=[-limit, limit],
    labels={
        "Difference_from_global_mean": "Difference from global mean (score points)",
        "Country": "",
    },
    title=f"Country happiness relative to the global mean ({global_mean:.2f})",
    template="plotly_white",
    hover_data={"Happiness_Score": ":.2f", "Difference_from_global_mean": ":+.2f"}
)
fig_diverging.update_traces(marker=dict(size=11, line=dict(width=0.5, color="white")))
fig_diverging.add_vline(
    x=0,
    line_width=2,
    line_dash="dash",
    line_color="#222222",
    annotation_text=f"Global mean = {global_mean:.2f}",
    annotation_position="top"
)
fig_diverging.update_layout(
    height=max(600, 25 * len(diverging)),
    coloraxis_colorbar=dict(title="Δ from<br>global mean"),
    margin=dict(l=10, r=25, t=80, b=45)
)
st.plotly_chart(fig_diverging, width="stretch")

st.caption("Source: World Happiness Report 2023 (137 country records).")
