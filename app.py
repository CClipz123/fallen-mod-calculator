import math
import streamlit as st
from datetime import datetime

MAINTENANCE_MODE = False

st.set_page_config(page_title="Mod Pay Tracker", page_icon="🎫")

if MAINTENANCE_MODE:
    st.error("🚧 This App is Currently Down for Maintenance")
    st.info("We are updating the system. Please check back later!")
    st.stop()

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

def getRequiredTicketsForPay(targetPay):
    """Calculates total weighted tickets needed to achieve a target pay amount."""
    if targetPay <= 0:
        return 0
    if targetPay <= defaultModPay:
        return 135  # Minimum tickets required to earn standard pay
    
    # Extra pay above base rate requires extra tickets
    extraPayNeeded = targetPay - defaultModPay
    extraTicketsNeeded = math.ceil(extraPayNeeded / capsPerExtraTicket)
    return quota + extraTicketsNeeded

st.title("🎫 Moderator Ticket & Pay Tracker")

moderatorName = st.text_input("Moderator Name")

# Mode toggle
calc_mode = st.radio("Choose Mode:", ["Calculate Pay from Tickets", "Target Pay Goal Planner"])

if calc_mode == "Calculate Pay from Tickets":
    weekendTickets = st.number_input("Tickets done from Friday to Sunday:", min_value=0, step=1)
    weekdayTickets = st.number_input("Tickets done from Monday to Thursday:", min_value=0, step=1)

    if st.button("Calculate Pay", type="primary"):
        if not moderatorName.strip():
            st.warning("Please enter a moderator name.")
        else:
            totalTickets = math.floor((weekendTickets * weekendMultiplier) + weekdayTickets)
            ticketsLeft = math.ceil(quota - totalTickets)
            status = "Completed" if ticketsLeft <= 0 else f"{ticketsLeft} tickets left to quota"
            modPay = getModPay(totalTickets)

            st.success("Calculation Complete!")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Weighted Tickets", totalTickets)
            col2.metric("Status", status)
            col3.metric("Mod Pay", f"{modPay:,}")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            entry = (
                f"Name: {moderatorName} | Weekend: {weekendTickets} | "
                f"Weekday: {weekdayTickets} | Total: {totalTickets} | "
                f"Status: {status} | Pay: {modPay} | Timestamp: {timestamp}\n"
            )
            with open("datastore.txt", "a", encoding="utf-8") as file:
                file.write(entry)

else:
    targetPay = st.number_input("Target Mod Pay Goal:", min_value=0, step=100, value=4500)

    if st.button("Calculate Needed Tickets", type="primary"):
        if not moderatorName.strip():
            st.warning("Please enter a moderator name.")
        elif targetPay <= 0:
            st.warning("Please enter a valid target pay goal.")
        else:
            requiredTotalTickets = getRequiredTicketsForPay(targetPay)
            
            # Day breakdown calculations
            weekdayOnly = requiredTotalTickets
            weekendOnly = math.ceil(requiredTotalTickets / weekendMultiplier)

            st.success(f"Target Plan for {moderatorName}: {targetPay:,} Pay")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Weighted Tickets Needed", requiredTotalTickets)
            col2.metric("If Weekdays Only (Mon-Thu)", f"{weekdayOnly} tickets")
            col3.metric("If Weekends Only (Fri-Sun)", f"{weekendOnly} tickets")

            st.info(
                f"💡 **Strategy Tip:** Because of the {weekendMultiplier}x weekend multiplier, doing "
                f"**{weekendOnly}** weekend tickets counts as **{math.floor(weekendOnly * weekendMultiplier)}** weighted tickets."
            )

st.divider()
st.subheader("📋 Submitted Entries History")

try:
    with open("datastore.txt", "r", encoding="utf-8") as file:
        logs = file.read()
        
    if logs.strip():
        st.text_area("Log Entries", logs, height=200)
        st.download_button(
            label="📥 Download History File",
            data=logs,
            file_name="datastore.txt",
            mime="text/plain"
        )
    else:
        st.info("No entries recorded in datastore.txt yet.")
except FileNotFoundError:
    st.info("No entries recorded yet. Submit a calculation to start logging!")
