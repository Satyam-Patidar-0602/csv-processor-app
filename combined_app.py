import pandas as pd
import streamlit as st
from io import BytesIO

st.title("CSV Data Processing Tool")

st.write("Upload CSV files and choose the processing type.")

uploaded_file1 = st.file_uploader("Choose first CSV file", type="csv", key="file1")
uploaded_file2 = st.file_uploader("Choose second CSV file (for highlighting)", type="csv", key="file2")

if uploaded_file1 is not None and uploaded_file2 is not None:
    df1 = pd.read_csv(uploaded_file1)
    df1.columns = df1.columns.str.strip()
    df1["%CHNG"] = pd.to_numeric(df1["%CHNG"], errors="coerce")
    
    df2 = pd.read_csv(uploaded_file2)
    df2.columns = df2.columns.str.strip()
    df2["%CHNG"] = pd.to_numeric(df2["%CHNG"], errors="coerce")

    st.subheader("Set the %CHNG range for filtering the first file")
    col1, col2 = st.columns(2)
    with col1:
        min_chng = st.number_input("Min %CHNG (for negative)", value=-0.71, step=0.01, key="global_min")
    with col2:
        max_chng = st.number_input("Max %CHNG (for positive)", value=0.71, step=0.01, key="global_max")

    tab1, tab2 = st.tabs(["Filter and Highlight", "Positive and Negative Filter"])

    with tab1:
        st.header("Filter first CSV for positive/negative in range, then highlight in second CSV")
        
        # Filter first CSV for positive/negative in range, excluding NaN and 0
        positive_df1 = df1[
            (df1["%CHNG"] > 0) &
            (df1["%CHNG"] <= max_chng) &
            df1["%CHNG"].notna() &
            (df1["%CHNG"] != 0)
        ]
        negative_df1 = df1[
            (df1["%CHNG"] < 0) &
            (df1["%CHNG"] >= min_chng) &
            df1["%CHNG"].notna() &
            (df1["%CHNG"] != 0)
        ]
        filtered_df1 = pd.concat([positive_df1, negative_df1])
        
        st.write(f"Filtered first file has {len(filtered_df1)} rows with symbols in range.")
        
        # Get symbols from filtered first
        symbols = set(filtered_df1["SYMBOL"])
        
        st.write(f"Unique symbols: {len(symbols)}")
        st.write(f"Sample symbols: {list(symbols)[:5]}")
        
        # Filter second CSV: SYMBOL in symbols and not blank
        filtered_df2 = df2[
            df2["SYMBOL"].isin(symbols) &
            df2["SYMBOL"].notna() &
            (df2["SYMBOL"] != "")
        ]
        
        st.write(f"Filtered second file has {len(filtered_df2)} matching rows.")
        
        def style_chng(val):
            if val > 0:
                return 'background-color: lightgreen'
            elif val < 0:
                return 'background-color: lightcoral'
            else:
                return ''
        
        st.write("Filtered second CSV preview (green: positive %CHNG, red: negative %CHNG):")
        st.dataframe(filtered_df2.style.map(style_chng, subset=['%CHNG']))
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            filtered_df1.to_excel(writer, sheet_name="Filtered First", index=False)
            filtered_df2.to_excel(writer, sheet_name="Highlighted Second", index=False)
        buffer.seek(0)
        st.download_button(
            label="Download Combined Excel",
            data=buffer,
            file_name="combined_filtered_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tab2:
        st.header("Filter Positive and Negative %CHNG")
        col1, col2 = st.columns(2)
        with col1:
            min_chng = st.number_input("Min %CHNG (for negative)", value=-0.71, step=0.01)
        with col2:
            max_chng = st.number_input("Max %CHNG (for positive)", value=0.71, step=0.01)
        positive_df = df1[
            (df1["%CHNG"] > 0) &
            (df1["%CHNG"] <= max_chng)
        ]
        negative_df = df1[
            (df1["%CHNG"] < 0) &
            (df1["%CHNG"] >= min_chng)
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