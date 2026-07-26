import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import random
import string
import pandas as pd
import time  # ⏰ Added to handle the balloon pause!

# --- 1. DATABASE CONNECTION ---
def connect_to_sheet():
    SHEET_NAME = "Library_Booking_DB"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds_info = st.secrets["gspread_creds"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

def generate_booking_id():
    return "BOK-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- 2. PAGE CONFIG & THEMING INJECTION ---
st.set_page_config(page_title="PTES Library Booking", layout="wide")

# Custom CSS Styling to inject your specific color codes safely
st.markdown("""
    <style>
    /* 1. Main Background Window Color */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #BC63F8 !important;
    }
    
    /* Global text enhancement for readability over the purple background */
    .main h1, .main h2, .main h3, .main p, .main label {
        color: #FFFFFF !important;
        font-weight: 500;
    }
    
    /* 2. Top Header Section Accent */
    header[data-testid="stHeader"] {
        background-color: #8FFAE1 !important;
    }
    
    /* 3. Sidebar Custom Layout Color & Text Contrast */
    [data-testid="stSidebar"] {
        background-color: #FAF68F !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1 {
        color: #1E1E1E !important;
    }
    
    /* 4. Tab Container Control Configurations */
    /* Ensure the tab navigation buttons have clear visibility */
    button[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-weight: bold;
    }
    
    /* Target individual tab contents explicitly by structural order */
    div[data-testid="stTab"] {
        padding: 15px;
        border-radius: 8px 8px 0px 0px;
    }
    
    /* TAB 1 Panel Area: Reserve a Room */
    div[data-testid="stTabContent"]:nth-of-type(1) {
        background-color: #E2BBFC !important;
        padding: 25px;
        border-radius: 0px 0px 10px 10px;
        border: 2px solid #E2BBFC;
    }
    div[data-testid="stTabContent"]:nth-of-type(1) * {
        color: #000000 !important; /* Black text for high visibility on light purple */
    }
    
    /* TAB 2 Panel Area: Booking Schedule */
    div[data-testid="stTabContent"]:nth-of-type(2) {
        background-color: #FEE7FD !important;
        padding: 25px;
        border-radius: 0px 0px 10px 10px;
        border: 2px solid #FEE7FD;
    }
    div[data-testid="stTabContent"]:nth-of-type(2) * {
        color: #000000 !important; /* Dark text for high contrast on dusty pink */
    }
    
    /* TAB 3 Panel Area: Admin Management */
    div[data-testid="stTabContent"]:nth-of-type(3) {
        background-color: #FCBBDA !important;
        padding: 25px;
        border-radius: 0px 0px 10px 10px;
        border: 2px solid #FCBBDA;
    }
    div[data-testid="stTabContent"]:nth-of-type(3) * {
        color: #000000 !important; /* Dark text for high contrast on light pink */
    }
    
    /* 5. Footer Layout Container Section */
    .custom-footer-container {
        background-color: #C4F863 !important;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .custom-footer-container .footer-line {
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        color: #000000 !important;
        margin-bottom: 10px;
    }
    .custom-footer-container .dev-line {
        font-size: 13px;
        font-weight: bold;
        text-align: center;
        color: #222222 !important;
    }
    
    /* Form fields interior color cleanup for accessibility */
    input, select, textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR (User Guide & Digital Citizenship) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=100)
    st.title("📖 PTES User Guide")

    st.info("""
    **How to Book:**
    1. Fill in your details in the 'Reserve' tab.
    2. Save your **Booking ID**.
    3. Check the 'Schedule' to confirm.
    4. Only The Librarian can DELETE bookings.
    """)

    st.divider()

    st.warning("⚖️ **Digital Citizenship & Rules**")
    st.write("""
    To ensure a productive environment for everyone, please adhere to the following:

    * 👨‍🏫 **Supervision:** A lecturer MUST be present in the room at all times.
    * 🔑 **Access:** The lecturer is responsible for collecting the key from the counter and returning it immediately after use.
    * 🧹 **Cleanliness:** Ensure the room is tidy and whiteboards are cleared before leaving.
    * 🤫 **Silence:** Please maintain a reasonable volume. Silence in the library vicinity is a top priority.
    * 🚫 **No Food:** Only Mineral Water bottle allowed inside the room.
    """)

    st.divider()
    st.caption("Developed for PTES Lecturers©2026")
    
# --- 4. MAIN CONTENT ---
st.title("📚 Library Discussion Room Booking System")
tab1, tab2, tab3 = st.tabs(["📅 Reserve a Room", "📋 Booking Schedule", "🔐 Admin Management"])

# --- TAB 1: NEW RESERVATION ---
with tab1:
    st.subheader("New Reservation Form")
    room_data = {
        "Room 1 (Level 2) max.17 ": {"capacity": 17},
        "Room 2 (Level 2) max.11 ": {"capacity": 11},
        "Room 3 (Level 3) max.10 ": {"capacity": 10},
        "Room 4 (Level 3) max.18 ": {"capacity": 18}
    }
    time_slots = ["07:45 - 08:45", "08:45 - 09:45", "09:45 - 10:10", "10:10 - 11:10", "11:10 - 12:10", "13:20 - 14:20",
                  "14:20 - 15:20", "15:20 - 16:00", "07:45-08:30 (Ramadhan)", "08:35-09:20 (Ramadhan)", "09:25-10:10 (Ramadhan)",
                  "10:25-11:10 (Ramadhan)", "11:15-12:00 (Ramadhan)", "08:00-09:00 (Sch.Hldy)", "09:00-10:00 (Sch.Hldy)", "10:00-11:00 (Sch.Hldy)"]

    with st.form("booking_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name (Lecturer/Staff)")
            phone = st.text_input("Telephone Number")
            dept = st.text_input("Department / Subject Taught")
            booking_date = st.date_input("Date of Booking", min_value=date.today())
        with c2:
            room_choice = st.selectbox("Select Room", list(room_data.keys()))
            max_cap = room_data[room_choice]["capacity"]
            slot = st.selectbox("Select Time Slot", time_slots)
            pax = st.number_input("Number of People Coming", min_value=1, value=1)
            purpose = st.text_area("Purpose of Booking", height=68)

        if st.form_submit_button("CONFIRM BOOKING"):
            sheet = connect_to_sheet()
            if sheet:
                existing_records = sheet.get_all_records()
                is_clashed = any(
                    str(r.get('Booking Date')) == str(booking_date) and str(r.get('Room')) == room_choice and str(
                        r.get('Time Slot')) == slot for r in existing_records)
                if is_clashed:
                    st.error(f"🚫 CLASH: {room_choice} is already booked on {booking_date} at {slot}.")
                elif pax > max_cap:
                    st.error(f"⚠️ CAPACITY EXCEEDED: {room_choice} only holds {max_cap} people.")
                elif not name or not phone:
                    st.warning("Please fill in contact information.")
                else:
                    booking_id = generate_booking_id()
                    new_entry = [str(datetime.now()), booking_id, name, phone, dept, str(booking_date), room_choice,
                                 slot, pax, purpose, "Confirmed"]
                    sheet.append_row(new_entry)
                    
                    st.success(f"✅ Booking Confirmed! ID: {booking_id}")
                    st.balloons()
                    
                    time.sleep(1.0)
                    st.rerun()

# --- TAB 2: SCHEDULE VIEW ---
with tab2:
    st.subheader("Upcoming Room Schedule")
    sheet = connect_to_sheet()
    if sheet:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            
            if 'Booking Date' in df.columns:
                df['sort_date'] = pd.to_datetime(df['Booking Date'], errors='coerce')
                df = df.sort_values(by='sort_date', ascending=False).drop(columns=['sort_date'])
                
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No bookings currently in the database.")

# --- TAB 3: ADMIN & CANCELLATION ---
with tab3:
    st.subheader("Admin Control Panel")
    admin_pass = st.text_input("Enter Admin Password", type="password")
    if admin_pass == st.secrets["admin_password"]:
        st.divider()
        st.write("### 🗑️ Cancel a Booking")
        cancel_id = st.text_input("Enter Booking ID to Delete")
        if st.button("DELETE BOOKING"):
            if cancel_id:
                sheet = connect_to_sheet()
                records = sheet.get_all_records()
                row_to_delete = next((i + 2 for i, r in enumerate(records) if str(r.get('Booking ID')) == cancel_id),
                                     None)
                if row_to_delete:
                    sheet.delete_rows(row_to_delete)
                    st.success(f"Successfully deleted booking {cancel_id}!")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    st.error("Booking ID not found.")

# --- SCHOOL POLICY NOTICE & BRANDING ---
st.warning("⚖️ SCHOOL **HOLIDAYS** : The Library Discussion rooms reservation are between **08:00 to 11:00 only** 👨‍🏫")   
st.divider()

# Styled wrapper utilizing the specified Minty Green hex code background
st.markdown("""
    <div class="custom-footer-container">
        <div class="footer-line">
            🟥 Perseverance &nbsp; 🟢 Trustworthiness &nbsp; 🔵 Exemplary &nbsp; 🟡 Self-reliance &nbsp; ⬜
        </div>
        <div class="dev-line">
            "PORTAL DEVELOPER : Miss Hajah Nurul Haziqah binti Haji Nordin (Computer Science Tutor)"
        </div>
    </div>
""", unsafe_allow_html=True)
