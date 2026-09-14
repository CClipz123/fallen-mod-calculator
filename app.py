import math
import streamlit as st
from datetime import datetime

# ==========================================
# MAINTENANCE TOGGLE
# Change this to True when you want to lock the app!
MAINTENANCE_MODE = False
# ==========================================

st.set_page_config(page_title="Mod Pay Tracker", page_icon="🎫")

if MAINTENANCE_MODE:
    st.error("🚧 This App is Currently Down for Maintenance")
    st.info("We are updating the system. Please check back later!")
    st.stop()

# --- Logic Constants ---
defaultModPay = 4500
weekendMultiplier = 1.5
quota = 150
capsPerExtraTicket = 5

def getModPay(totalTickets):
    if totalTickets <= 150 and totalTickets >= 135:
        return defaultModPay
    elif totalTickets > 150:
        ticketsOverQuota = totalTickets - quota
        return defaultModPay + (ticketsOverQuota * capsPerExtraTicket)
    return 0

# --- User Interface ---
st.title("🎫 Moderator Ticket & Pay Tracker")

moderatorName = st.text_input("Moderator Name")
weekendTickets = st.number_input("Tickets done from Friday to Sunday:", min_value=0, step=1)
weekdayTickets = st.number_input("Tickets done from Monday to Thursday:", min_value=0, step=1)

if st.button("Calculate", type="primary"):
    if not moderatorName.strip():
        st.warning("Please enter a moderator name.")
    else:
        # Exact calculations from your original script
        totalTickets = math.floor((weekendTickets * weekendMultiplier) + weekdayTickets)
        ticketsLeft = math.ceil(quota - totalTickets)

        if ticketsLeft <= 0:
            status = "Completed"
        else:
            status = f"{ticketsLeft} tickets left"

        modPay = getModPay(totalTickets)

        # Display Metrics
        st.success("Calculation Complete!")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tickets", totalTickets)
        col2.metric("Status", status)
        col3.metric("Mod Pay", f"{modPay:,}")

        # Store Entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = (
            f"Name: {moderatorName} | Weekend Tickets: {weekendTickets} | "
            f"Weekday Tickets: {weekdayTickets} | Total Tickets: {totalTickets} | "
            f"Status: {status} | Pay: {modPay} | Timestamp: {timestamp}\n"
        )

        # Store locally or in session history
        with open("datastore.txt", "a", encoding="utf-8") as file:
            file.write(entry)