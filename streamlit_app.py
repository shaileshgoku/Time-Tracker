import streamlit as st
from datetime import datetime, timedelta

# --- Page Config ---
st.set_page_config(
    page_title="Time Tracker",
    page_icon="⏳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    /* Dark Theme Base */
    .stApp {
        background-color: #0f172a;
        font-family: 'Inter', sans-serif;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        color: #f8fafc;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        transform: translateY(-2px);
    }

    /* Titles and Metrics */
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #e0e7ff !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #a5b4fc !important;
    }

    /* Custom Container Card */
    .css-1r6slb0 {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Logic ---
def parse_time(time_str):
    formats = ["%I:%M %p", "%I:%M%p", "%H:%M"]
    for fmt in formats:
        try:
            return datetime.strptime(time_str.strip(), fmt)
        except ValueError:
            continue
    return None

def calculate_intervals(intervals_list):
    total_seconds = 0
    breakdown = []
    
    for item in intervals_list:
        start_str = item['start']
        end_str = item['end']
        
        if not start_str or not end_str:
            continue
            
        start_dt = parse_time(start_str)
        end_dt = parse_time(end_str)
        
        if not start_dt or not end_dt:
            breakdown.append("Invalid format")
            continue
            
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
            
        duration = end_dt - start_dt
        seconds = int(duration.total_seconds())
        total_seconds += seconds
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        label_parts = []
        if hours > 0: label_parts.append(f"{hours}h")
        if minutes > 0: label_parts.append(f"{minutes}m")
        breakdown.append(" ".join(label_parts) if label_parts else "0m")
        
    return total_seconds, breakdown

# --- Session State ---
if 'intervals' not in st.session_state:
    st.session_state.intervals = [{'start': '', 'end': ''}]

def add_row():
    st.session_state.intervals.append({'start': '', 'end': ''})

def remove_row(index):
    if len(st.session_state.intervals) > 1:
        st.session_state.intervals.pop(index)

# --- UI ---
st.title("⏳ Time Tracker")
st.markdown("Champions always will be in transition phase")

with st.container():
    # Loop through intervals
    for i, interval in enumerate(st.session_state.intervals):
        cols = st.columns([3, 3, 2, 1])
        
        # Conditional Placeholder
        start_ph = "1:10 pm" if i == 0 else ""
        end_ph = "1:20 pm" if i == 0 else ""
        
        with cols[0]:
            st.session_state.intervals[i]['start'] = st.text_input(
                f"Start Time #{i+1}", 
                value=interval['start'], 
                placeholder=start_ph,
                key=f"start_{i}",
                label_visibility="collapsed"
            )
            
        with cols[1]:
            st.session_state.intervals[i]['end'] = st.text_input(
                f"End Time #{i+1}", 
                value=interval['end'], 
                placeholder=end_ph,
                key=f"end_{i}",
                label_visibility="collapsed"
            )
            
        # Inline Duration Calculation
        duration_text = ""
        s_str = st.session_state.intervals[i]['start']
        e_str = st.session_state.intervals[i]['end']
        
        if s_str and e_str:
            s_dt = parse_time(s_str)
            e_dt = parse_time(e_str)
            if s_dt and e_dt:
                if e_dt < s_dt:
                    e_dt += timedelta(days=1)
                diff = e_dt - s_dt
                mins = int(diff.total_seconds() / 60)
                h = mins // 60
                m = mins % 60
                parts = []
                if h > 0: parts.append(f"{h}h")
                if m > 0: parts.append(f"{m}m")
                duration_text = " ".join(parts) if parts else "0m"
        
        with cols[2]:
            if duration_text:
                st.markdown(f"<div style='padding-top: 10px; color: #a5b4fc; font-weight: bold;'>{duration_text}</div>", unsafe_allow_html=True)
            
        with cols[3]:
            # Cross Mark Icon
            if st.button("✕", key=f"del_{i}", help="Remove Row"):
                remove_row(i)
                st.rerun()

    # Add Button
    st.button("➕ Add Interval", on_click=add_row)

    st.markdown("---")

    if st.button("Calculate Total Duration", type="primary"):
        total_sec, breakdown = calculate_intervals(st.session_state.intervals)
        
        total_h = total_sec // 3600
        total_m = (total_sec % 3600) // 60
        
        if total_h > 0 or total_m > 0:
            st.metric(label="Grand Total", value=f"{total_h}h {total_m}m")
            
            # Prepare Report
            current_date = datetime.now().strftime("%Y-%m-%d")
            report_lines = ["Time Tracker Report", f"Date: {current_date}", "="*20, ""]
            for i, (interval, dur_str) in enumerate(zip(st.session_state.intervals, breakdown)):
                s = interval['start']
                e = interval['end']
                if s and e:
                    report_lines.append(f"Interval {i+1}: {s} - {e} ({dur_str})")
            
            report_lines.append("")
            report_lines.append(f"Grand Total: {total_h}h {total_m}m")
            report_text = "\n".join(report_lines)
            
            st.download_button(
                label="Download Report",
                data=report_text,
                file_name="time_tracker_report.txt",
                mime="text/plain"
            )
            
        else:
            st.info("Enter times to see the calculation.")

# Footer
st.markdown("---")
st.caption("Deployable to Streamlit Cloud ☁️")
