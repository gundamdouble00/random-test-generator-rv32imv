import json
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from rtg.ga.main_ga import FINAL_GEN, FIRST_GEN

REPORTS_PATH: str = "./coverage_analyzer/"
FILE_NAME: str = "rv_assembly"
LOG: str = ".log"
OUTPUTS: str = "./outputs"
SPIKE_LOG_FILES: str = OUTPUTS + "/spike_log_files"
SUMMARY_FILE: str = "summary.txt"
STREAMLIT: str = "streamlit"
RUN: str = "run"
STREAMLIT_DOT_PY: str = REPORTS_PATH + "analyzer/coverage.py"
TEMP_DATA_JSON: str = "./coverage_analyzer/analyzer/temp_data.json"
FITNESS_SCORE_JSON: str = "./rtg/fitness_score.json"

_ = st.title("Coverage Analyzer")


if os.path.exists(TEMP_DATA_JSON) and os.path.exists(FITNESS_SCORE_JSON):
    with open(TEMP_DATA_JSON, "r") as temp_data:
        received_data = json.load(temp_data)
    with open(FITNESS_SCORE_JSON, "r") as fitness_score:
        fitness_data = json.load(fitness_score)

    df_first_gen = pd.DataFrame(
        {"Fitness Score": fitness_data[FIRST_GEN], "Generation": "First Generation"}
    )
    df_final_gen = pd.DataFrame(
        {"Fitness Score": fitness_data[FINAL_GEN], "Generation": "Final Generation"}
    )
    df_boxplot = pd.concat([df_first_gen, df_final_gen])
    fig = px.box(
        df_boxplot,
        x="Generation",
        y="Fitness Score",
        color="Generation",
        points="all",
        color_discrete_sequence=["#ef553b", "#636efa"],
    )
    _ = st.subheader("Fitness score Comparison")
    _ = fig.update_layout(showlegend=False)
    _ = st.plotly_chart(fig, use_container_width=True)

    df = pd.DataFrame.from_dict(received_data, orient="columns")
    df.columns = df.columns.astype(int)
    df = df.sort_index(axis=1)
    _ = st.subheader("Data Overview (Table)")
    _ = st.dataframe(df)
    df_flat = df.reset_index().rename(columns={"index": "Type"})
    df_long = df_flat.melt(
        id_vars=["Type"], var_name="Test cases", value_name="Percent"
    )
    df_long["Test cases"] = df_long["Test cases"].astype(int)
    all_types = list(df_long["Type"].unique())
    selected_types = st.multiselect(
        "Select type to visualize:", options=all_types, default=all_types
    )
    filtered_long_df = df_long[df_long["Type"].isin(selected_types)]
    _ = st.subheader("Cumulative Coverage")

    if selected_types:
        _ = st.line_chart(
            data=filtered_long_df,
            x="Test cases",  # Custom X-axis
            y="Percent",  # Custom Y-axis
            color="Type",  # Custom line grouping/color
        )
    else:
        _ = st.warning("Please select at least one line type.")
else:
    _ = st.error(
        "No data found! Please check temp_data.json and fitness_score.json first!!!"
    )
