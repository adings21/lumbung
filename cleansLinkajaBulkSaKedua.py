import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

def process_digipos_Bulk2(df, location):
    df['Completion Time'] = df['Completion Time'].astype(str).str.strip()
    df['Opposite Party'] = df['Opposite Party'].astype(str).str.strip()
    df['Receipt No.'] = df['Receipt No.'].astype(str).str.strip()
    df['Initiation Time'] = df['Initiation Time'].astype(str).str.strip()
    
    df_filtered = df.dropna(subset=['Completion Time', 'Opposite Party'])

    def parse_datetime_Bulk2(datetime_str):
        formats = [
            '%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S',
            '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M',
            '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y',
        ]
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str.strip(), fmt)
            except ValueError:
                pass
        raise ValueError(f"no valid datetime format found for {datetime_str}")

    df_filtered['custom_transaction_id'] = df_filtered.apply(
        lambda row: f"{row['Opposite Party'].split(' - ')[0].strip()}_{parse_datetime_Bulk2(row['Completion Time']).strftime('%d/%m/%Y')}_{parse_datetime_Bulk2(row['Completion Time']).strftime('%H.%M')}", axis=1)

    cols = df_filtered.columns.tolist()
    cols = [cols[-1]] + cols[:-1]
    df_filtered = df_filtered[cols]

    return df_filtered

def convert_df_to_excel_Bulk2(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

def main_Bulk2():
    st.title('Data Cleansing dan Custom ID Generator Tahap 3')

    # Upload file Digipos
    uploaded_file_digipos = st.file_uploader("Upload File BulkSA", type=['csv', 'xlsx'], key="file_uploader_digipos_v2")
    if uploaded_file_digipos is not None:
        if uploaded_file_digipos.name.endswith('.csv'):
            df_digipos = pd.read_csv(uploaded_file_digipos, dtype={'Receipt No.': str})
        elif uploaded_file_digipos.name.endswith('.xlsx'):
            df_digipos = pd.read_excel(uploaded_file_digipos, dtype={'Receipt No.': str})
        st.session_state.df_digipos_v2 = df_digipos

    cleaned_digipos = st.session_state.get('cleaned_digipos_v2', None)

    # Tombol untuk melakukan cleansing dan membuat custom ID
    if st.button("Lakukan Cleansing dan Custom ID (v2)"):
        loc_prefix = 'custom_v2'  # Ganti dengan prefiks yang sesuai dengan kebutuhan Anda

        if 'df_digipos_v2' in st.session_state:
            try:
                cleaned_digipos = process_digipos_Bulk2(st.session_state.df_digipos_v2, loc_prefix)
                st.session_state.cleaned_digipos_v2 = cleaned_digipos
                st.success("Cleansing dan pembuatan Custom ID untuk Digipos berhasil!")
            except ValueError as e:
                st.error(f"Error processing Digipos data: {e}")

    # Tambahkan tombol untuk mengunduh hasil Digipos
    if cleaned_digipos is not None:
        excel_digipos = convert_df_to_excel_Bulk2(cleaned_digipos)
        st.download_button(
            label="Download Hasil BulkSA (v2)",
            data=excel_digipos,
            file_name=f'CleansedV2_{uploaded_file_digipos.name}.xlsx',  # Ubah ekstensi menjadi .xlsx
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key='download_digipos_v2'
        )

if __name__ == "__main__":
    main_Bulk2()
