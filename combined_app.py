import pandas as pd
import streamlit as st
from io import BytesIO

st.title("CSV Data Processing Tool")

st.write("Upload a CSV file and choose the processing type.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    df["%CHNG"] = pd.to_numeric(df["%CHNG"], errors="coerce")

    tab1, tab2 = st.tabs(["Exclude Zero and Dash", "Positive and Negative Filter"])

    with tab1:
        st.header("Exclude values in %CHNG")
        exclude_nan = st.checkbox("Exclude NaN (dash) values", value=True)
        exclude_zero = st.checkbox("Exclude zero values", value=True)
        
        conditions = []
        if exclude_nan:
            conditions.append(df["%CHNG"].notna())
        if exclude_zero:
            conditions.append(df["%CHNG"] != 0)
        
        if conditions:
            combined_condition = conditions[0]
            for cond in conditions[1:]:
                combined_condition &= cond
            filtered_df = df[combined_condition]
        else:
            filtered_df = df
        
        st.write("Filtered data preview:")
        st.dataframe(filtered_df.head())
        buffer = BytesIO()
        filtered_df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="Download Filtered Excel",
            data=buffer,
            file_name="non_zero_no_dash_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tab2:
        st.header("Filter Positive and Negative %CHNG")
        col1, col2 = st.columns(2)
        with col1:
            min_chng = st.number_input("Min %CHNG (for negative)", value=-0.71, step=0.01)
        with col2:
            max_chng = st.number_input("Max %CHNG (for positive)", value=0.71, step=0.01)
        positive_df = df[
            (df["%CHNG"] > 0) &
            (df["%CHNG"] <= max_chng)
        ]
        negative_df = df[
            (df["%CHNG"] < 0) &
            (df["%CHNG"] >= min_chng)
        ]
        st.write("Positive data preview:")
        st.dataframe(positive_df.head())
        st.write("Negative data preview:")
        st.dataframe(negative_df.head())
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            positive_df.to_excel(writer, sheet_name="Positive", index=False)
            negative_df.to_excel(writer, sheet_name="Negative", index=False)
        buffer.seek(0)
        st.download_button(
            label="Download Filtered Excel",
            data=buffer,
            file_name="filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )