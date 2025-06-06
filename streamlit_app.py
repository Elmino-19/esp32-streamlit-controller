
"""
ESP32 Relay Controller - Streamlit Web Application

This application provides a web-based interface for controlling ESP32 relay modules
via HTTP communication. It supports real-time relay control, servo motor management,
and scheduled task automation.

Features:
- Real-time ESP32 connectivity monitoring
- Manual relay control (4 channels)
- Servo motor angle control (45-145 degrees)
- Scheduled relay operations with time-based automation
- Persian (Farsi) user interface
- HTTP-based communication with error handling and retries

Dependencies:
- streamlit: Web application framework
- requests: HTTP client library
- threading: Background task execution
- datetime: Time and scheduling operations

Author: Erfan Mohamadnia
Protocol: HTTP
Target Device: ESP32 with relay and servo modules
"""

import streamlit as st
import requests
import time
import threading
from datetime import datetime, time as dt_time, timedelta
import json

# --- Global Variables ---
state = st.session_state

def init_session_state():
    """Initialize Streamlit session state variables for application state management."""
    # Configuration variables
    if "esp_ip" not in state:
        state.esp_ip = "192.168.1.100"
    if "max_retries" not in state:
        state.max_retries = 3
    if "retry_delay" not in state:
        state.retry_delay = 2
    if "request_timeout" not in state:
        state.request_timeout = 5
    
    # Connection status variables
    if "connection_status" not in state:
        state.connection_status = "Not Connected"
    if "connection_message" not in state:
        state.connection_message = "هنوز متصل نشده است."
    if "connection_status_color" not in state:
        state.connection_status_color = "disconnected"
    if "relay_states" not in state:
        state.relay_states = [False] * 4
    if "initial_status_fetched" not in state:
        state.initial_status_fetched = False
    
    # Relay state variables
    for i in range(1, 5):
        if f"relay_{i}_state" not in state:
            state[f"relay_{i}_state"] = False
        if f"schedule_active_{i}" not in state:
            state[f"schedule_active_{i}"] = False

init_session_state()

# --- Styling ---
def load_css(file_path):
    """Load and apply CSS styles from external file."""
    with open(file_path) as f:
        st.markdown(f"""<style>{f.read()}</style>""", unsafe_allow_html=True)  

load_css("assets/style.css")

# --- HTTP Communication ---
def check_esp_availability():
    """
    Checks if the ESP32 HTTP server is available.
    Manages retries and updates connection status in Streamlit's session state.
    
    Returns:
        bool: True if ESP32 is responsive, False otherwise.
    """
    
    state.connection_message = "در حال بررسی ارتباط با ESP..."
    state.connection_status_color = "connecting"
    
    base_url = f"http://{state.esp_ip}"

    for attempt in range(state.max_retries):
        try:
            response = requests.get(f"{base_url}/status", timeout=state.request_timeout)
            response.raise_for_status()
            
            state.connection_status = "Connected"
            state.connection_status_color = "connected"
            state.connection_message = f"متصل به {state.esp_ip} (HTTP)"
            print("Successfully connected to ESP via HTTP.")
            
            if get_initial_status():
                state.initial_status_fetched = True
                print("Successfully fetched initial relay statuses via HTTP.")
            else:
                state.initial_status_fetched = False
                st.warning("هشدار: دریافت وضعیت اولیه رله‌ها از طریق HTTP ناموفق بود.")
            return True
        except requests.exceptions.RequestException as e:
            state.connection_status = f"Connection Failed: {e} (Attempt {attempt + 1})"
            state.connection_status_color = "disconnected"
            state.connection_message = f"خطا در ارتباط HTTP (تلاش {attempt + 1}): {e}"
            print(state.connection_status)
            if attempt < state.max_retries - 1:
                time.sleep(state.retry_delay)
            else:
                st.error(f"ارتباط با ESP از طریق HTTP ناموفق بود پس از {state.max_retries} تلاش.")
                return False
    return False

def send_http_request(endpoint, params=None, method="GET", expected_response_type="json"):
    """
    Sends an HTTP request to the ESP32 and returns its response.
    Handles request errors and updates connection status if issues arise.
    
    Args:
        endpoint (str): The API endpoint (e.g., "/relay", "/status").
        params (dict, optional): Query parameters for the request.
        method (str, optional): HTTP method ("GET", "POST", etc.). Defaults to "GET".
        expected_response_type (str, optional): "json" or "text". Defaults to "json".
        
    Returns:
        dict, str, or None: The response from ESP32, or None if an error occurred.
    """
    
    if state.connection_status != "Connected":
        st.error("ارتباط با ESP برقرار نیست. لطفاً ابتدا متصل شوید.")
        state.connection_status_color = "disconnected"
        state.connection_message = "ارتباط با ESP برقرار نیست."
        return None

    url = f"http://{state.esp_ip}{endpoint}"
    
    try:
        print(f"Sending HTTP {method} request to {url} with params: {params}")
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=state.request_timeout)
        elif method.upper() == "POST":
            response = requests.post(url, params=params, timeout=state.request_timeout)
        else:
            st.error(f"متد HTTP پشتیبانی نشده: {method}")
            return None
            
        response.raise_for_status()
        
        print(f"Received HTTP response: {response.status_code} - {response.text}")
        
        if expected_response_type == "json":
            try:
                return response.json()
            except json.JSONDecodeError:
                st.warning(f"پاسخ JSON نامعتبر از دستگاه: {response.text}")
                return {"raw_text": response.text}
        else:
            return response.text
            
    except requests.exceptions.Timeout:
        st.error(f"پاسخ از دستگاه برای درخواست به {endpoint} دریافت نشد (timeout).")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"خطا در ارسال درخواست HTTP به {endpoint}: {e}")
        return None

def get_initial_status():
    """
    Fetches the initial status of all relays from the ESP32 via HTTP.
    Updates Streamlit's session state for each relay.
    
    Returns:
        bool: True if status was successfully parsed, False otherwise.
    """
    
    response_data = send_http_request("/status", expected_response_type="json")
    
    if response_data:
        try:
            if "relay_states" in response_data and isinstance(response_data["relay_states"], list) and len(response_data["relay_states"]) == 4:
                new_states = [bool(s) for s in response_data["relay_states"]]
            elif all(f"relay{i+1}" in response_data for i in range(4)):
                new_states = [bool(response_data[f"relay{i+1}"]) for i in range(4)]
            elif isinstance(response_data, str) and "raw_text" not in response_data:
                 parts = response_data.strip().split(',')
                 if len(parts) == 4:
                     new_states = [p == "1" or p.lower() == "true" for p in parts]
                 else:
                    st.error(f"خطا در تجزیه پاسخ وضعیت متنی از ESP: {response_data}")
                    return False
            elif "raw_text" in response_data and isinstance(response_data["raw_text"], str):
                 parts = response_data["raw_text"].strip().split(',')
                 if len(parts) == 4:
                     new_states = [p == "1" or p.lower() == "true" for p in parts]
                 else:
                    st.error(f"خطا در تجزیه پاسخ وضعیت متنی (fallback) از ESP: {response_data['raw_text']}")
                    return False
            else:
                st.error(f"فرمت پاسخ وضعیت از ESP نامعتبر است: {response_data}")
                return False

            state.relay_states = new_states
            for i in range(4):
                state[f"relay_{i+1}_state"] = state.relay_states[i]  
            print(f"Initial relay states (HTTP): {state.relay_states}")
            return True
        except Exception as e:
            print(f"Exception parsing status response (HTTP) \'{response_data}\': {e}")
            st.error(f"خطای داخلی هنگام تجزیه پاسخ وضعیت دستگاه (HTTP): {e}")
            return False
    else:
        print(f"Could not get initial status via HTTP. Response: {response_data}")
        return False

# --- Relay Control Logic ---
def toggle_relay(relay_num):
    """
    Toggles the state of a specific relay via HTTP.
    Sends ON/OFF command to ESP and updates session state.
    
    Args:
        relay_num (int): The relay number to toggle (1-4)
    """
    
    current_state_key = f"relay_{relay_num}_state"  
    esp_relay_index = relay_num - 1
    target_state_bool = not state.get(current_state_key, False)
    target_state_str = "on" if target_state_bool else "off"
    
    endpoint = f"/relay/{esp_relay_index}/{target_state_str}"
    response = send_http_request(endpoint, method="GET")
    
    if response and (response.get("status") == "success" or "success" in response.get("raw_text", "")):
        state[current_state_key] = target_state_bool
        state.relay_states[esp_relay_index] = target_state_bool
        st.success(f"رله {relay_num} {'روشن' if target_state_bool else 'خاموش'} شد (HTTP).")
    else:
        st.error(f"خطا در تغییر وضعیت رله {relay_num} (HTTP). Response: {response}")

def scheduled_task(relay_num, delay_seconds, duration_seconds):
    """
    Task executed in a separate thread to control a relay on a schedule via HTTP.
    
    Args:
        relay_num (int): The relay number to control (1-4)
        delay_seconds (float): Seconds to wait before turning ON
        duration_seconds (float): How long to keep the relay ON before turning OFF
    """
    
    esp_relay_index = relay_num - 1
    base_url = f"http://{state.esp_ip}"

    try:
        if delay_seconds > 0:
            print(f"Relay {relay_num} (HTTP): Waiting for {delay_seconds}s to turn ON.")
            time.sleep(delay_seconds)

        print(f"Relay {relay_num} (HTTP): Turning ON for {duration_seconds}s.")
        on_endpoint = f"/relay/{esp_relay_index}/on"
        on_url = f"{base_url}{on_endpoint}"
        try:
            on_response = requests.get(on_url, timeout=state.request_timeout)
            on_response.raise_for_status()
            print(f"Relay {relay_num} ON command response (HTTP): {on_response.text}")
            print(f"Relay {relay_num} turned ON via schedule (HTTP).")
        except requests.exceptions.RequestException as e:
            print(f"HTTP error in scheduled_task (ON) for relay {relay_num}: {e}")
            return

        time.sleep(duration_seconds)

        print(f"Relay {relay_num} (HTTP): Turning OFF.")
        off_endpoint = f"/relay/{esp_relay_index}/off"
        off_url = f"{base_url}{off_endpoint}"
        try:
            off_response = requests.get(off_url, timeout=state.request_timeout)
            off_response.raise_for_status()
            print(f"Relay {relay_num} OFF command response (HTTP): {off_response.text}")
            print(f"Relay {relay_num} turned OFF via schedule (HTTP).")
        except requests.exceptions.RequestException as e:
            print(f"HTTP error in scheduled_task (OFF) for relay {relay_num}: {e}")

    except Exception as e:
        print(f"Error in scheduled_task (HTTP) for relay {relay_num}: {e}")


# --- UI Layout ---
st.title("کنترلر رله ESP (HTTP)")

# Connection Area
st.subheader("وضعیت اتصال (HTTP)")
connect_button_text = "اتصال به ESP (HTTP)"
if state.connection_status_color == "connected":
    connect_button_text = "بررسی مجدد اتصال / قطع اتصال"
elif state.connection_status_color == "connecting":
    connect_button_text = "در حال بررسی..."

if st.button(connect_button_text, disabled=(state.connection_status_color == "connecting")):
    if state.connection_status_color != "connected":
        check_esp_availability()
    else:
        state.connection_status = "Disconnected"
        state.connection_status_color = "disconnected"
        state.connection_message = "ارتباط HTTP قطع شد (به صورت دستی)."
        state.initial_status_fetched = False
        for i in range(1, 5):
            state[f"relay_{i}_state"] = False  
            state[f"schedule_active_{i}"] = False  
    st.rerun()


st.markdown(f'<div class="stConnectionStatus {state.connection_status_color}">{state.connection_message}</div>', unsafe_allow_html=True)  

st.subheader("کنترل رله‌ها (HTTP)")

relay_names = {
    1: "پمپ ۱",
    2: "پمپ ۲",
    3: "پمپ ۳",
    4: "آرمیچر"
}

for i in range(1, 5):
    with st.container():
        st.markdown(f'<div class="stRelayControl"><h3>{relay_names[i]} (رله {i})</h3></div>', unsafe_allow_html=True)  
        
        col1, col2 = st.columns(2)
        with col1:
            button_label = "خاموش کردن" if state[f"relay_{i}_state"] else "روشن کردن"  
            if st.button(button_label, key=f"toggle_relay_{i}", help=f"وضعیت رله {i} را تغییر دهید", type="primary" if not state[f"relay_{i}_state"] else "secondary", use_container_width=True):  
                if state.connection_status == "Connected":
                    toggle_relay(i)
                    st.rerun()
                else:
                    st.error("لطفا ابتدا به ESP متصل شوید.")
        
        with col2:
            current_state_text = "روشن" if state[f"relay_{i}_state"] else "خاموش"
            current_color = "green" if state[f"relay_{i}_state"] else "red"
            st.markdown(f"وضعیت فعلی: <span style='color:{current_color}; font-weight:bold;'>{current_state_text}</span>", unsafe_allow_html=True)

        with st.expander(f"زمان‌بندی برای {relay_names[i]}"):
            if state[f"schedule_active_{i}"]:
                st.info(f"یک زمان‌بندی برای {relay_names[i]} فعال است.")
                if st.button(f"لغو زمان‌بندی {relay_names[i]}", key=f"cancel_schedule_{i}"):
                    state[f"schedule_active_{i}"] = False  
                    st.warning(f"زمان‌بندی {relay_names[i]} در UI لغو شد (توجه: اگر نخ شروع شده باشد ممکن است کامل اجرا شود).")
                    st.rerun()
            else:
                schedule_time_dt = st.time_input(f"زمان روشن شدن برای {relay_names[i]}", value=None, key=f"time_{i}")
                duration_minutes = st.number_input(f"مدت زمان روشن بودن (دقیقه) برای {relay_names[i]}", min_value=1, value=5, key=f"duration_{i}")
                if st.button(f"تنظیم زمان‌بندی برای {relay_names[i]}", key=f"schedule_{i}"):
                    if state.connection_status != "Connected":
                        st.error("برای زمان‌بندی، ابتدا به ESP متصل شوید.")
                    elif schedule_time_dt and duration_minutes > 0:
                        now = datetime.now()
                        scheduled_datetime = now.replace(hour=schedule_time_dt.hour, minute=schedule_time_dt.minute, second=schedule_time_dt.second, microsecond=0)
                        if scheduled_datetime < now:
                            scheduled_datetime += timedelta(days=1)
                            st.info(f"زمان انتخاب شده برای گذشته است، برای فردا ({scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')}) تنظیم شد.")
                        
                        delay_seconds = (scheduled_datetime - now).total_seconds()
                        duration_total_seconds = duration_minutes * 60
                        
                        if delay_seconds < 0:
                            delay_seconds = 0 
                        
                        thread = threading.Thread(target=scheduled_task, args=(i, delay_seconds, duration_total_seconds))
                        thread.daemon = True
                        thread.start()
                        state[f"schedule_active_{i}"] = True  
                        st.success(f"{relay_names[i]} برای روشن شدن در ساعت {schedule_time_dt.strftime('%H:%M:%S')} به مدت {duration_minutes} دقیقه زمان‌بندی شد (HTTP).")  
                        st.rerun()
                    else:
                        st.warning("لطفاً زمان روشن شدن و مدت زمان را به درستی وارد کنید.")
        st.markdown("---")


st.subheader("کنترل سروو موتور (HTTP)")
servo_angle = st.slider("زاویه سروو (درجه)", 45, 145, 90, key="servo_angle_slider")
if st.button("تنظیم زاویه سروو", key="set_servo_angle_btn"):
    if state.connection_status == "Connected":
        endpoint = f"/servo/{servo_angle}"
        response = send_http_request(endpoint, method="GET")
        
        if response and (response.get("status") == "success" or "success" in response.get("raw_text","")):
            st.success(f"سروو به زاویه {servo_angle} درجه تنظیم شد (HTTP).")
        else:
            st.error(f"خطا در تنظیم زاویه سروو (HTTP): {response}")
    else:
        st.error("ابتدا به ESP متصل شوید.")

# --- Sidebar Settings ---
st.sidebar.header("⚙️ تنظیمات اتصال")

# Display current connection info
st.sidebar.info(f"""
📡 **اطلاعات فعلی:**
- IP: `{state.esp_ip}`
- Timeout: {state.request_timeout}s
- تلاش مجدد: {state.max_retries}
- تاخیر: {state.retry_delay}s
""")

with st.sidebar.expander("پیکربندی شبکه", expanded=False):
    new_esp_ip = st.text_input(
        "آدرس IP دستگاه ESP32:",
        value=state.esp_ip,
        help="آدرس IP دستگاه ESP32 در شبکه محلی",
        key="esp_ip_input"
    )
    
    new_request_timeout = st.number_input(
        "زمان انتظار درخواست (ثانیه):",
        min_value=1,
        max_value=30,
        value=state.request_timeout,
        help="حداکثر زمان انتظار برای دریافت پاسخ از ESP32",
        key="timeout_input"
    )
    
    new_max_retries = st.number_input(
        "تعداد تلاش مجدد:",
        min_value=1,
        max_value=10,
        value=state.max_retries,
        help="تعداد دفعات تلاش مجدد در صورت خطا",
        key="retries_input"
    )
    
    new_retry_delay = st.number_input(
        "تاخیر بین تلاش‌ها (ثانیه):",
        min_value=0.5,
        max_value=10.0,
        value=float(state.retry_delay),
        step=0.5,
        help="زمان انتظار بین تلاش‌های مجدد",
        key="delay_input"
    )
    
    if st.button("💾 ذخیره تنظیمات", key="save_settings", use_container_width=True):
        # Check if IP changed to reset connection
        ip_changed = new_esp_ip != state.esp_ip
        
        # Update session state with new values
        state.esp_ip = new_esp_ip
        state.request_timeout = new_request_timeout
        state.max_retries = new_max_retries
        state.retry_delay = new_retry_delay
        
        # Reset connection if IP changed
        if ip_changed:
            state.connection_status = "Not Connected"
            state.connection_status_color = "disconnected"
            state.connection_message = "تنظیمات تغییر کرد. لطفاً مجدداً متصل شوید."
            state.initial_status_fetched = False
        
        st.sidebar.success("✅ تنظیمات ذخیره شد!")
        st.rerun()

st.sidebar.markdown("---")

if st.sidebar.button("به‌روزرسانی وضعیت از ESP (HTTP)"):
    if state.connection_status == "Connected":
        st.sidebar.info("در حال به‌روزرسانی وضعیت از طریق HTTP...")
        if get_initial_status():
            state.initial_status_fetched = True
            st.sidebar.success("وضعیت با موفقیت از طریق HTTP به‌روز شد.")
        else:
            state.initial_status_fetched = False
            st.sidebar.error("به‌روزرسانی وضعیت از طریق HTTP ناموفق بود.")
        st.rerun()
    else:
        st.sidebar.warning("برای به‌روزرسانی، ابتدا از طریق HTTP متصل شوید.")

st.sidebar.markdown("---")
st.sidebar.markdown("ساخته شده با Streamlit")
st.sidebar.markdown("توسعه دهنده: عرفان محمدنیا")
