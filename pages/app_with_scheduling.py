import streamlit as st
import requests
from datetime import datetime, timedelta
from pathlib import Path

state = st.session_state
side = st.sidebar

# Define the base path for assets
base_path = Path(__file__).resolve().parent.parent / "assets"


if "esp_ip" not in state:
    state.esp_ip = "192.168.1.100"  # Default IP

def send_to_supabase(data):
    """
    Sends data to the Supabase database.

    Args:
        data (dict): The data to send to Supabase.

    Returns:
        str or None: The response from Supabase if successful, None otherwise.
    """
    supabase_url = "https://your-supabase-url.supabase.co/rest/v1/your-table"  # Replace with your Supabase URL
    supabase_key = "your-supabase-key"  # Replace with your Supabase API key

    headers = {
        "Content-Type": "application/json",
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}"
    }

    try:
        response = requests.post(supabase_url, json=data, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        st.error(f"Error sending data to Supabase: {e}")
        return None

def load_css(file_name):
    """Loads a CSS file into the Streamlit app."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file '{file_name}' not found.")

load_css(f"{base_path}/test_style.css")

with side:
    with st.form(key="ip_form", clear_on_submit=True):
        ip_input = st.text_input("ESP32 IP Address", value=state.esp_ip)
        submitted = st.form_submit_button("Submit", help="Connect to Device")
        if submitted:
            state.esp_ip = ip_input
            st.success(f"IP address updated to {ip_input}.")

device_configs = {
    "pump1": {"name": "Pump 1", "ch": 0},
    "pump2": {"name": "Pump 2", "ch": 3},
    "pump3": {"name": "Pump 3", "ch": 2},
    "motor": {"name": "DC Motor", "ch": 1},
}


# Arrange devices into two rows: three pumps in one row, two motors in another row
st.header("Device and Servo Motor Scheduling")

# First row: Pumps
with st.container():
    pump_cols = st.columns(3, vertical_alignment="bottom")  # Three columns for pumps
    pump_idx = 0
    for device_id, config in device_configs.items():
        if "pump" in device_id:
            current_col = pump_cols[pump_idx % 3]
            with current_col:
                st.image(
                    str(base_path / f"{config['name'].lower().replace(' ', '')}.png"), 
                    width=100, 
                    caption=config["name"]
                )
                st.subheader(config["name"])

                # Input fields for scheduling
                start_date = st.date_input(f"Start Date for {config['name']}", key=f"start_date_{device_id}")
                start_time = st.time_input(f"Start Time for {config['name']}", key=f"start_time_{device_id}")
                duration = st.number_input(f"Duration (seconds) for {config['name']}", min_value=1, step=1, key=f"duration_{device_id}")

                if st.button(f"Schedule {config['name']}", key=f"schedule_button_{device_id}"):
                    start_datetime = datetime.combine(start_date, start_time)
                    end_datetime = start_datetime + timedelta(seconds=duration)

                    data = {
                        "device_id": device_id,
                        "device_name": config["name"],
                        "start_datetime": start_datetime.isoformat(),
                        "end_datetime": end_datetime.isoformat(),
                        "duration": duration,
                        "channel": config["ch"]
                    }

                    response = send_to_supabase(data)

                    if response:
                        st.success(f"{config['name']} scheduled successfully. Response: {response}")
                    else:
                        st.error(f"Failed to schedule {config['name']}.")

            pump_idx += 1

# Second row: Motors (DC Motor and Servo Motor)
with st.container():
    motor_cols = st.columns(2, vertical_alignment="bottom")  # Two columns for motors
    motor_idx = 0
    for device_id, config in device_configs.items():
        if "motor" in device_id:
            current_col = motor_cols[motor_idx % 2]
            with current_col:
                st.image(
                    str(base_path / f"{config['name'].lower().replace(' ', '')}.png"), 
                    width=150, 
                    caption=config["name"]
                )
                st.subheader(config["name"])

                # Input fields for scheduling
                start_date = st.date_input(f"Start Date for {config['name']}", key=f"start_date_{device_id}")
                start_time = st.time_input(f"Start Time for {config['name']}", key=f"start_time_{device_id}")
                duration = st.number_input(f"Duration (seconds) for {config['name']}", min_value=1, step=1, key=f"duration_{device_id}")

                if st.button(f"Schedule {config['name']}", key=f"schedule_button_{device_id}"):
                    start_datetime = datetime.combine(start_date, start_time)
                    end_datetime = start_datetime + timedelta(seconds=duration)

                    data = {
                        "device_id": device_id,
                        "device_name": config["name"],
                        "start_datetime": start_datetime.isoformat(),
                        "end_datetime": end_datetime.isoformat(),
                        "duration": duration,
                        "channel": config["ch"]
                    }

                    response = send_to_supabase(data)

                    if response:
                        st.success(f"{config['name']} scheduled successfully. Response: {response}")
                    else:
                        st.error(f"Failed to schedule {config['name']}.")

            motor_idx += 1

    # Add Servo Motor to the same row as DC Motor
    current_col = motor_cols[motor_idx % 2]
    with current_col:
        st.image(str(base_path / "grinder.png"), width=150, caption="Servo Motor")
        st.subheader("Servo Motor")

        # Input fields for servo motor scheduling
        servo_start_date = st.date_input("Start Date for Servo Motor", key="servo_start_date")
        servo_start_time = st.time_input("Start Time for Servo Motor", key="servo_start_time")
        servo_duration = st.number_input("Duration (seconds) for Servo Motor", min_value=1, step=1, key="servo_duration")
        servo_angle = st.slider(
            "Servo Angle (degrees)", 
            min_value=0, 
            max_value=90, 
            step=1, 
            key="servo_angle", 
            help="Set the angle of the servo motor (0 to 90 degrees)."
        )

        if st.button("Schedule Servo Motor", key="schedule_servo_button"):
            servo_start_datetime = datetime.combine(servo_start_date, servo_start_time)
            servo_end_datetime = servo_start_datetime + timedelta(seconds=servo_duration)

            servo_data = {
                "device_id": "servo_motor",
                "device_name": "Servo Motor",
                "start_datetime": servo_start_datetime.isoformat(),
                "end_datetime": servo_end_datetime.isoformat(),
                "duration": servo_duration,
                "angle": servo_angle
            }

            servo_response = send_to_supabase(servo_data)

            if servo_response:
                st.success(f"Servo Motor scheduled successfully. Response: {servo_response}")
            else:
                st.error("Failed to schedule Servo Motor.")
