import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import random
import string
import pandas as pd


# --- 1. DATABASE CONNECTION ---
###################################################################################################
def connect_to_sheet():
    SHEET_NAME = "Library_Booking_DB"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # This tells the app to look in the Secrets vault we just filled!
        creds_info = st.secrets["gspread_creds"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None
############################################################################################

def generate_booking_id():
    return "BOK-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="PTES Library Booking", layout="wide")

# --- 3. SIDEBAR (User Guide & Digital Citizenship) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=100)  # Generic Library Icon
    st.title("📖 PTES User Guide")

    st.info("""
    **How to Book:**
    1. Fill in your details in the 'Reserve' tab.
    2. Save your **Booking ID**.
    3. Check the 'Schedule' to confirm.
    """)

    st.divider()

    st.warning("⚖️ **Digital Citizenship & Rules**")
    st.write("""
    To ensure a productive environment for everyone, please adhere to the following:

    * 👨‍🏫 **Supervision:** A lecturer MUST be present in the room at all times.
    * 🔑 **Access:** The lecturer is responsible for collecting the key from the counter and returning it immediately after use.
    * 🧹 **Cleanliness:** Ensure the room is tidy and whiteboards are cleared before leaving.
    * 🤫 **Silence:** While rooms are sound-proofed, please maintain a reasonable volume. Silence in the library vicinity is a top priority.
    * 🚫 **No Food:** Only drinks allowed inside the discussion rooms.
    """)

    st.divider()
    st.caption("Developed for PTES Lecturers©2026")
    
# --- 4. MAIN CONTENT ---
st.title("📚 Library Discussion Room Booking System")
tab1, tab2, tab3 = st.tabs(["📅 Reserve a Room", "📋 Booking Schedule", "🔐 Admin Management"])

# [The rest of the logic remains the same as your working script...]
# (I will keep the logic below the tabs exactly as we had it before)

# --- TAB 1: NEW RESERVATION ---
with tab1:
    st.subheader("New Reservation Form")
    room_data = {
        "Room 1 (Level 2)": {"capacity": 17},
        "Room 2 (Level 2)": {"capacity": 11},
        "Room 3 (Level 3)": {"capacity": 10},
        "Room 4 (Level 3)": {"capacity": 18}
    }
    time_slots = ["07:45 - 08:45", "08:45 - 09:45", "09:45 - 10:10", "10:10 - 11:10", "11:10 - 12:10", "13:20 - 14:20",
                  "14:20 - 15:20", "15:20 - 16:00", "07:45-08:30 (Ramadhan)", "08:35-09:20 (Ramadhan)", "09:25-10:10 (Ramadhan)",
                  "10:25-11:10 (Ramadhan)", "11:15-12:00 (Ramadhan)"]

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
            st.info(f"📍 Room Capacity: {max_cap} people")
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

# --- TAB 2: SCHEDULE VIEW ---
with tab2:
    st.subheader("Upcoming Room Schedule")
    sheet = connect_to_sheet()
    if sheet:
        data = sheet.get_all_records()
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
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
                else:
                    st.error("Booking ID not found.")

# --- PTES FOOTER IN SIDEBAR ---
# st.divider()
 st.warning("⚖️ **SCHOOL HOLIDAYS: Discussion rooms reservation are between 08:00 to 11:00.** 👨‍🏫")   
# Custom CSS for the shapes and text
st.markdown("""
    <style>
    .footer-line {
        font-size: 12px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    .dev-line {
        font-size: 11px;
        text-align: center;
        color: #888;
    }
    </style>
        
    <div class="footer-line">
        🟥 Perseverance &nbsp; 🟢 Trustworthiness &nbsp; 🔵 Exemplary &nbsp; 🟡 Self-reliance &nbsp; ⬜
    </div>
   
    <div class="dev-line">
        "PORTAL DEVELOPER : Miss Hajah Nurul Haziqah binti Haji Nordin (Computer Science Tutor)"
    </div>
""", unsafe_allow_html=True)
