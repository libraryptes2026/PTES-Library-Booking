import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import random
import string
import pandas as pd
import time  # ⏰ Handle the balloon pause!
import calendar

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

# Custom CSS Styling with deep target overrides for absolute text transformation
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
        background-color: #F8E7FE !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1 {
        color: #1E1E1E !important;
    }
    
    /* 4. Deep Target Tab Typography Override Engine */
    .stTabs [data-baseweb="tab-list"] button,
    .stTabs [data-baseweb="tab"],
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-testid="stMarkdownContainer"] p {
        font-size: 12pt !important;
        font-weight: bold !important;
        color: #000000 !important;
    }
    
    /* Target individual tab contents explicitly by structural order */
    div[data-testid="stTab"] {
        padding: 15px;
        border-radius: 8px 8px 0px 0px;
    }
    
    /* TAB 1 Panel Area: Reserve a Room */
    div[data-testid="stTabContent"]:nth-of-type(1) {
        background-color: #ECBBFC !important;
        padding: 25px;
        border-radius: 0px 0px 10px 10px;
        border: 2px solid #E2BBFC;
    }
    div[data-testid="stTabContent"]:nth-of-type(1) * {
        color: #000000 !important;
    }
    
    /* TAB 2 Panel Area: Booking Schedule */
    div[data-testid="stTabContent"]:nth-of-type(2) {
        background-color: #FEE7FD !important;
        padding: 25px;
        border-radius: 0px 0px 10px 10px;
        border: 2px solid #FEE7FD;
    }
    div[data-testid="stTabContent"]:nth-of-type(2) * {
        color: #000000 !important;
    }
    
    /* TAB 3 Panel Area: Admin Management */
    div[data-testid="stTabContent"]:nth-of-type(3) {
        background-color: #FCBBDA !important;
        padding: 25px;
        border-radius: 0px 0px 10px 10px;
        border: 2px solid #FCBBDA;
    }
    div[data-testid="stTabContent"]:nth-of-type(3) * {
        color: #000000 !important;
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

    /* Interactive Calendar Component Enhancements */
    .calendar-banner {
        background-color: #FBC58D !important;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #E2A365;
    }
    .calendar-banner h2 {
        color: #000000 !important;
        margin: 0;
    }
    .weekday-header {
        font-weight: bold;
        color: #4A154B !important;
        text-align: center;
        font-size: 14pt;
        padding-bottom: 10px;
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

# Setup variables
room_options = [
    "Room 1 (Level 2) max.17 ",
    "Room 2 (Level 2) max.11 ",
    "Room 3 (Level 3) max.10 ",
    "Room 4 (Level 3) max.18 "
]

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

# --- TAB 2: SCHEDULE VIEW (WITH INTERACTIVE CALENDAR) ---
with tab2:
    st.markdown("""
        <div class="calendar-banner">
            <h2>📅 Interactive Schedule Calendar</h2>
        </div>
    """, unsafe_allow_html=True)

    sheet = connect_to_sheet()
    df = pd.DataFrame()
    if sheet:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            if 'Booking Date' in df.columns:
                df['Booking Date'] = df['Booking Date'].astype(str).str.strip()

    # Layout Parameters Top Row
    col_refresh, col_room = st.columns([1, 3])
    with col_refresh:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    with col_room:
        selected_room = st.selectbox("Select Room / Venue to Inspect", ["All Rooms"] + room_options)

    # Filter Dataframe by Room Choice early for accurate calendar dots
    if not df.empty and selected_room != "All Rooms":
        df_filtered = df[df['Room'] == selected_room]
    else:
        df_filtered = df.copy()

    # Layout Parameters Middle Row (Month / Year Selection Panel)
    st.write("---")
    c_month, c_year = st.columns(2)
    
    months_list = list(calendar.month_name)[1:]
    current_date = date.today()
    
    with c_month:
        selected_month_str = st.selectbox("Select Month", months_list, index=current_date.month - 1)
        selected_month = months_list.index(selected_month_str) + 1
    with c_year:
        selected_year = st.number_input("Select Year", min_value=2020, max_value=2035, value=current_date.year)

    # Days of the week header matrix block
    days_headers = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    cols_header = st.columns(7)
    for index, day_name in enumerate(days_headers):
        cols_header[index].markdown(f'<div class="weekday-header">{day_name}</div>', unsafe_allow_html=True)

    # Compute Calendar Grid Arrays
    cal = calendar.Calendar(firstweekday=0) # ISO Standard starting on Monday
    month_days = cal.monthdayscalendar(selected_year, selected_month)

    # Session State tracker initialize for target tracking click selection
    if "selected_calendar_day" not in st.session_state:
        st.session_state.selected_calendar_day = current_date.day

    # Render Calendar Day Rows
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("") # Empty padding spaces outside of target month boundaries
            else:
                # Format string target match condition comparison 'YYYY-MM-DD'
                target_date_str = f"{selected_year}-{str(selected_month).zfill(2)}-{str(day).zfill(2)}"
                
                # Check bookings occurrences count
                booking_count = 0
                if not df_filtered.empty and 'Booking Date' in df_filtered.columns:
                    booking_count = len(df_filtered[df_filtered['Booking Date'] == target_date_str])

                # Visual configuration for markers
                if booking_count > 0:
                    btn_label = f"🔴 {str(day).zfill(2)} ({booking_count})"
                else:
                    btn_label = f"⚪ {str(day).zfill(2)}"

                # Check if this button context matches tracked session state select marker
                if cols[i].button(btn_label, key=f"cal-{day}-{selected_month}", use_container_width=True):
                    st.session_state.selected_calendar_day = day

    # --- SHOW CLICK DETAILS BLOCK BELOW GRID (ABOVE FOOTER PART) ---
    st.write("---")
    active_day = st.session_state.selected_calendar_day
    display_date_str = f"{selected_year}-{str(selected_month).zfill(2)}-{str(active_day).zfill(2)}"
    formatted_date_display = f"{str(active_day).zfill(2)}/{str(selected_month).zfill(2)}/{selected_year}"
    
    st.markdown(f"### 🔍 All Reservations for {formatted_date_display}")

    if not df_filtered.empty and 'Booking Date' in df_filtered.columns:
        day_bookings = df_filtered[df_filtered['Booking Date'] == display_date_str]
        if not day_bookings.empty:
            st.success(f"Found {len(day_bookings)} booking(s) matching your view:")
            
            # 🛡️ Error-proof columns selection fallback tracker
            # Maps what you want to what exists in the Google Sheet data headers
            column_mapping = {
                'Name': "Lecturer's Name",
                'Booking Date': "Date Book",
                'Time Slot': "Time Slot",
                'Room': "Type of Discussion Room",
                'Pax': "Number of students",
                'Booking ID': "Booking ID"
            }
            
            # Only use columns that actually exist in the dataframe to avoid key errors
            available_cols = [col for col in column_mapping.keys() if col in day_bookings.columns]
            valid_df = day_bookings[available_cols].copy()
            
            # Rename headers cleanly
            rename_dict = {col: column_mapping[col] for col in available_cols}
            valid_df = valid_df.rename(columns=rename_dict)
            
            # Rearrange columns into your exact desired structural sequence order safely
            final_order = ["Lecturer's Name", "Date Book", "Time Slot", "Type of Discussion Room", "Number of students", "Booking ID"]
            existing_final_order = [c for c in final_order if c in valid_df.columns]
            valid_df = valid_df[existing_final_order]
            
            # Render dataframe view smoothly
            st.dataframe(valid_df.reset_index(drop=True), use_container_width=True)
        else:
            st.info(f"No bookings registered for {formatted_date_display}.")
    else:
        st.info("No interactive database records found.")

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

# --- CUSTOM SCHOOL POLICY NOTICE CONTAINER ---
st.markdown("""
    <div style="background-color: #FAB38F; padding: 15px; border-radius: 8px; border-left: 6px solid #F40B1F; margin-bottom: 20px;">
        <p style="color: #F40B1F !important; font-size: 16px; font-weight: bold; margin: 0; text-align: center;">
            ⚖️ SCHOOL HOLIDAYS : The Library Discussion rooms reservation are between 08:00 to 11:00 only 👨‍🏫
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

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
