from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

src_file = Path.cwd() / "users" / "sebas" / "jiji.xlsx"

df= pd.read_csv(src_file)

fig = px.histogram(
    df,
    x="make",
    color="class_summary",
    labes={"price":"Per Vehicle"},
    nbins = 40,
    title="Per Vehicle Make Price"
)
st.title("Example Using Streamlit")
st.write(fig)

print(src_file)
