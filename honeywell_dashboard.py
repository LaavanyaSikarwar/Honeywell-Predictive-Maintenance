import pandas as pd
import streamlit as st
import plotly.express as px

# --- STEP 1: LOAD REAL DATA ---
# Ensure 'ai4i2020.csv' is in your project folder
@st.cache_data # This keeps the app fast by loading data only once
def load_data():
    raw_df = pd.read_csv('ai4i2020.csv')
    
    # Rename columns to match your dashboard logic
    clean_df = raw_df.rename(columns={
        'Product ID': 'Machine_ID',
        'Air temperature [K]': 'Temp_K',
        'Rotational speed [rpm]': 'Vibration', # Using RPM as vibration proxy
        'Torque [Nm]': 'Pressure',             # Using Torque as pressure proxy
        'Tool wear [min]': 'Tool_Wear'
    })
    
    # Data Engineering: Convert Kelvin to Celsius
    clean_df['Temperature'] = clean_df['Temp_K'] - 273.15
    
    # Calculate RUL: Assuming a max tool life of 250 minutes
    clean_df['RUL'] = 250 - clean_df['Tool_Wear']
    clean_df['RUL'] = clean_df['RUL'].clip(lower=0)
    
    return clean_df

df = load_data()

# Create a "History Table" by finding rows where 'Machine failure' == 1
# This shows real past failures from the dataset
df_history = df[df['Machine failure'] == 1][['Machine_ID', 'Type', 'RUL']].copy()
df_history['Date'] = "2025-03-20" # Adding a dummy date for the log
df_history = df_history.rename(columns={'Type': 'Issue', 'RUL': 'Status'})
df_history['Status'] = "Failure Recorded"

# --- STEP 2: USER SELECTION ---
st.set_page_config(page_title="Honeywell PdM Capstone", layout="wide")
st.title("🛡️ Honeywell Asset Performance Monitor (Real-Data Edition)")

# We select from the first 100 unique machine IDs to keep the list manageable
machine_list = df['Machine_ID'].unique()[:100]
selected_machine = st.sidebar.selectbox("Select Asset (Product ID)", machine_list)

# Get the specific data for the selected machine
m_info = df[df['Machine_ID'] == selected_machine].iloc[0].copy()

# --- STEP 3: SENSOR SIMULATOR (Real Data Ranges) ---
st.sidebar.divider()
st.sidebar.subheader("🛠️ Sensor Simulator")
st.sidebar.write("Override real sensor data to test AI")

# Adjusting slider ranges to match real data (Temp ~20-50C, RPM 1000-3000)
sim_temp = st.sidebar.slider("Simulate Temperature (°C)", 20.0, 50.0, float(m_info['Temperature']))
sim_vib = st.sidebar.slider("Simulate Speed (RPM)", 1000, 3000, int(m_info['Vibration']))

# Update simulated values
m_info['Temperature'] = sim_temp
m_info['Vibration'] = sim_vib

# Real-World Threshold Logic:
# Points drop if Temp > 35C or Speed > 2500 RPM
temp_penalty = max(0, sim_temp - 35) * 5
vib_penalty = max(0, sim_vib - 2500) * 0.1
sim_health = 100 - (temp_penalty + vib_penalty)

m_info['Health_Score'] = max(0, min(100, int(sim_health)))

# --- STEP 4: DISPLAY METRICS ---
col1, col2, col3 = st.columns(3)
col1.metric("Health Score", f"{m_info['Health_Score']}%")
col2.metric("Remaining Tool Life", f"{int(m_info['RUL'])} Mins")

# Show temperature delta vs "Normal" 25°C
temp_delta = sim_temp - 25
col3.metric("Current Temp", f"{sim_temp:.1f}°C", delta=f"{temp_delta:.1f}°C", delta_color="inverse")

# --- STEP 5: VISUAL CHART ---
st.subheader(f"📊 Real-Time Sensor Analysis: {selected_machine}")

# Plotting the three main sensors
chart_df = pd.DataFrame({
    'Sensor': ['Temp (°C)', 'Speed (RPM)', 'Torque (Nm)'],
    'Value': [m_info['Temperature'], m_info['Vibration'], m_info['Pressure']]
})

# Dynamic Color Logic
if m_info['Health_Score'] < 50:
    bar_color = "#EE3124" # Honeywell Red
elif m_info['Health_Score'] < 80:
    bar_color = "#FFA421" # Warning Orange
else:
    bar_color = "#0033A0" # Honeywell Blue

fig = px.bar(chart_df, x='Sensor', y='Value', title=f"Real-Time Metrics for {selected_machine}")
fig.update_traces(marker_color=bar_color)
st.plotly_chart(fig, use_container_width=True)

# --- STEP 6: AI PREDICTIVE INSIGHTS ---
st.subheader("🤖 AI Predictive Insight")
fail_prob = 100 - m_info['Health_Score']
# Simplified prediction: 1 day per 10% health
days_to_fail = int(m_info['Health_Score'] / 10)

if m_info['Health_Score'] < 50:
    st.error(f"🚨 CRITICAL: {fail_prob}% Failure Probability!")
    st.write(f"**AI Recommendation:** High thermal/mechanical stress. Shut down {selected_machine} for maintenance.")
elif m_info['Health_Score'] < 80:
    st.warning(f"⚠️ WARNING: {fail_prob}% Failure Probability.")
    st.write(f"**AI Recommendation:** Performance degrading. Schedule inspection within 48 hours.")
else:
    st.success(f"✅ STATUS: Healthy ({fail_prob}% Prob.)")
    st.write("**AI Recommendation:** All sensors within nominal range. No action required.")

# --- STEP 7: MAINTENANCE HISTORY ---
st.divider()
st.subheader("📜 Historical Failure Logs (Real Dataset Records)")
machine_history = df_history[df_history['Machine_ID'] == selected_machine]

if not machine_history.empty:
    st.table(machine_history)
else:
    st.info("No past failures found for this specific asset in the dataset.")

# Sidebar Download
csv_data = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Download Fleet Data", csv_data, "honeywell_pdm_report.csv", "text/csv")