
import streamlit as st
import time

satate = st.session_state


try:
    from app import send_request, device_configs # If test.py is in
except ImportError:

    st.error("Could not import shared utilities. Ensure test.py is structured to allow imports or use a shared module.")

    def send_request(endpoint, params):
        """Placeholder for send_request if import fails."""
        st.warning(f"send_request (placeholder) called with: {endpoint}, {params}")
        time.sleep(0.5)
        return f"Mock success for {endpoint}"

    device_configs = {
        "pump1": {"name": "پمپ ۱", "ch": 0, "on_image": "assets/pomp1.png", "off_image": "assets/pomp-off.png"},
        "pump2": {"name": "پمپ ۲", "ch": 3, "on_image": "assets/pomp2.png", "off_image": "assets/pomp-off.png"},
        "pump3": {"name": "پمپ ۳", "ch": 2, "on_image": "assets/pomp3.png", "off_image": "assets/pomp-off.png"},
        "motor": {"name": "موتور DC", "ch": 1, "on_image": "assets/grinder.png", "off_image": "assets/grinder-off.png"},
    }

st.title("عملیات زمان‌دار")
st.header("تنظیم مدت زمان روشن بودن قطعات")

for device_id in device_configs:
    duration_key = f"timed_op_duration_{device_id}"

    if duration_key not in st.session_state:
        st.session_state[duration_key] = 0  # Default duration to 0 seconds

def handle_timed_run_button_on_page(device_id: str, duration_key: str, ch: int, device_name: str):
    
    duration = st.session_state.get(duration_key, 0)
    main_toggle_key = f"device_toggle_{device_id}"
    timed_op_end_time_key = f"{main_toggle_key}_timed_end_time" 

    if duration > 0:
        params = {"ch": ch, "state": 0, "duration": duration} 
        result = send_request("/relay", params)

        if result:
            st.session_state[main_toggle_key] = True 
            st.session_state[timed_op_end_time_key] = time.time() + duration
            st.success(f"{device_name} به مدت {duration} ثانیه روشن خواهد شد. وضعیت در صفحه کنترل مستقیم قابل مشاهده است. پاسخ: {result}")

        else:
            st.error(f"خطا در ارسال دستور اجرای زمان‌دار برای {device_name}.")

    else:
        st.warning("مدت زمان برای اجرای زمان‌دار باید بیشتر از صفر ثانیه باشد.")

for device_id_ui, config_ui in device_configs.items():
    st.subheader(config_ui["name"])
    _duration_key_ui = f"timed_op_duration_{device_id_ui}"
    
    st.number_input(
        label="مدت زمان روشن بودن (ثانیه)",
        min_value=0,
        step=1,
        key=_duration_key_ui, 
        help=f"چه مدت {config_ui['name']} روشن بماند؟"
    )
    
    st.button(
        label=f"روشن کردن {config_ui['name']} به مدت تنظیم شده",
        key=f"button_timed_run_page_{device_id_ui}",
        on_click=handle_timed_run_button_on_page,
        args=(device_id_ui, _duration_key_ui, config_ui["ch"], config_ui["name"])
    )
    st.divider()

st.info("توجه: وضعیت فعلی روشن/خاموش بودن قطعات در صفحه 'پنل کنترل مستقیم' نمایش داده می‌شود.")

