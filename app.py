import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# GOOGLE AUTH
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

# OPEN GOOGLE SHEET
sheet = client.open_by_key("1qU4zQucj2n9mTFDeZ_86PJndHM7B3nTEkW6M4x-CXdM")

materials_ws = sheet.worksheet("Materials")
submissions_ws = sheet.worksheet("Submissions")
wtg_ws = sheet.worksheet("WTG_List")
teams_ws = sheet.worksheet("Teams")

# LOAD DATA
materials_data = materials_ws.get_all_records()
materials_df = pd.DataFrame(materials_data)

wtg_list = wtg_ws.col_values(1)[1:]
team_list = teams_ws.col_values(1)[1:]

# APP TITLE
st.title("Material Checklist")

# HEADER
site = st.text_input("Site")

wo = st.selectbox("WO", team_list)

wtg = st.selectbox("WTG", wtg_list)

technician = st.text_input("Technician")

st.divider()

st.subheader("Materials")

quantities = {}

# MATERIAL LIST
for index, row in materials_df.iterrows():

    col1, col2, col3 = st.columns([3,3,1])

    with col1:
        st.write(row["English"])

    with col2:
        st.write(row["Portuguese"])

    with col3:
        qty = st.number_input(
            f"qty_{index}",
            min_value=0,
            step=1,
            label_visibility="collapsed"
        )

    quantities[row["Material_ID"]] = {
        "english": row["English"],
        "portuguese": row["Portuguese"],
        "qty": qty
    }

# SUBMIT BUTTON
if st.button("Submit Checklist"):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    submission_id = datetime.now().strftime("%Y%m%d%H%M%S")

    rows_to_insert = []

    for material_id, data in quantities.items():

        if data["qty"] > 0:

            rows_to_insert.append([
                timestamp,
                submission_id,
                site,
                wo,
                wtg,
                technician,
                material_id,
                data["english"],
                data["portuguese"],
                data["qty"]
            ])

    if rows_to_insert:

        submissions_ws.append_rows(rows_to_insert)

        st.success("Checklist submitted successfully!")

    else:
        st.warning("No quantities entered.")