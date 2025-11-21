import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Data Explorer")

st.write(
    "This page loads a small example dataset from `data/example_data.csv` "
    "and lets you explore it."
)

data_path = Path("data") / "example_data.csv"

try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error(f"Could not find data file at `{data_path}`.")
    st.stop()

st.subheader("Raw data")
st.dataframe(df, use_container_width=True)

st.subheader("Filter by x value")
min_x, max_x = float(df["x"].min()), float(df["x"].max())
selected_range = st.slider(
    "Select x range",
    min_value=min_x,
    max_value=max_x,
    value=(min_x, max_x),
)

mask = (df["x"] >= selected_range[0]) & (df["x"] <= selected_range[1])
filtered_df = df[mask]

st.write(f"Showing {len(filtered_df)} rows in the selected range.")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("Line chart of y over x (filtered)")
st.line_chart(filtered_df.set_index("x")["y"])

