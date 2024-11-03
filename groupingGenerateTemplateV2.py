import pandas as pd
import streamlit as st
import base64
from babel.numbers import format_decimal
from io import BytesIO
import locale



def generate_invoice_number_v2(row, invoice_month_year):
    warehouse = row['WarehouseName'].lower()
    if 'kendari' in warehouse:
        warehouse_name = 'Kendari'
    elif 'kolaka' in warehouse:
        warehouse_name = 'Kolaka'
    else:
        warehouse_name = 'Other'

    # Extracting the phone number part from *Customer column
    customer_number = row['*Customer'].split(' - ')[0]

    invoice_number = f"{warehouse_name}_{customer_number}_{invoice_month_year}_2"
    return invoice_number

def generate_journal_template_v2(input_file, invoice_date, due_date, invoice_month_year):
    # Read input file
    df = pd.read_excel(input_file)

    # Group by Customer and sum Withdrawn and Credit
    grouped = df.groupby('*Customer').agg({
        'Withdrawn': 'sum',
        'Credit': 'sum',
        '*InvoiceDate': 'first',
        'WarehouseName': 'first',
        'Tags (use': 'first'
    }).reset_index()

    # Calculate Quantity and UnitPrice
    grouped['*Quantity'] = grouped['Withdrawn'] / 1000
    grouped['*UnitPrice'] = grouped['Credit'] / grouped['*Quantity']

    # Generate jurnal_template DataFrame
    jurnal_template = pd.DataFrame({
        '*Customer': grouped['*Customer'],
        'Email': '',
        'BillingAddress': '',
        'ShippingAddress': '',
        '*InvoiceDate': invoice_date,
        '*DueDate': due_date,
        'ShippingDate': '',
        'ShipVia': '',
        'TrackingNo': '',
        'CustomerRefNo': '',
        '*InvoiceNumber': grouped.apply(lambda row: generate_invoice_number_v2(row, invoice_month_year), axis=1),  # Generate Invoice Number
        'Message': '',
        'Memo': '',
        '*ProductName': 'Voucherless Bulk 10JT NGRS - Mitra SBP (V841)',
        'Description': '',
        '*Quantity': grouped['*Quantity'],
        'Unit': 'Rupiah',
        '*UnitPrice': grouped['*UnitPrice'],
        'ProductDiscountRate(%)': '',
        'InvoiceDiscountRate(%)': '',
        'TaxName': 'PPN',
        'TaxRate(%)': '11%',
        'ShippingFee': '',
        'WitholdingAccountCode': '',
        'WitholdingAmount(value or %)': '',
        '#paid?(yes/no)': 'YES',
        '#PaymentMethod': 'TRANSFER',
        '#PaidToAccountCode': '1-110006',
        'Tags (use ; to separate tags)': grouped['Tags (use'],
        'WarehouseName': grouped['WarehouseName'],
        '#currency code(example: IDR, USD, CAD)': ''
    })

    # Logging total Credit
    total_credit = grouped['Credit'].sum()
    st.write(f"Total Credit: Rp {format_decimal(total_credit, locale='id_ID')}")

    # Logging total *UnitPrice (Quantity * UnitPrice)
    total_unit_price = (grouped['*Quantity'] * grouped['*UnitPrice']).sum()
    st.write(f"Total *UnitPrice: Rp {format_decimal(total_unit_price, locale='id_ID')}")

    return jurnal_template

def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def main():
    st.title('Generate Journal Template V2')

    uploaded_file = st.file_uploader('Upload input file', type='xlsx')
    if uploaded_file:
        invoice_date = st.date_input('Choose Invoice Date')
        due_date = st.date_input('Choose Due Date')
        invoice_month = st.selectbox('Choose Invoice Month', range(1, 13))
        invoice_year = st.selectbox('Choose Invoice Year', range(2020, 2031))
        invoice_month_year = "{:02d}/{:d}".format(invoice_month, invoice_year)  # Format bulan/tahun disini

        if st.button('Generate Template'):
            # Ensure invoice_date and due_date are converted to the correct format
            invoice_date_str = invoice_date.strftime('%d/%m/%Y')
            due_date_str = due_date.strftime('%d/%m/%Y')

            jurnal_template = generate_journal_template_v2(uploaded_file, invoice_date_str, due_date_str, invoice_month_year)
            
            st.write('Generated Journal Template V2')
            st.dataframe(jurnal_template)

            st.download_button(
                label='Download Journal Template V2 as Excel',
                data=convert_df_to_excel(jurnal_template),
                file_name='journal_template_Fix_LinkAja_V2.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

if __name__ == '__main__':
    main()
