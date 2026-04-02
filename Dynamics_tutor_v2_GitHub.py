import streamlit as st
import json
import re
import numpy as np
import matplotlib.pyplot as plt
from google.api_core import exceptions  # For rate limit handling
from logic_v2_GitHub import get_gemini_model, load_problems, check_numeric_match, analyze_and_send_report
from render_v2_GitHub import render_problem_diagram, render_lecture_visual

# 1. Page Configuration
st.set_page_config(page_title="Socratic Engineering Tutor", layout="wide")

# 2. CSS: Refined Spacing and UI consistency
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    div.stButton > button {
        height: 60px;
        padding: 5px 10px;
        font-size: 14px;
        white-space: normal;
        word-wrap: break-word;
        line-height: 1.2;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    img {
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Initialize Session State
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_sessions" not in st.session_state: st.session_state.chat_sessions = {}
if "grading_data" not in st.session_state: st.session_state.grading_data = {}
if "user_name" not in st.session_state: st.session_state.user_name = None
if "lecture_topic" not in st.session_state: st.session_state.lecture_topic = None
if "lecture_session" not in st.session_state: st.session_state.lecture_session = None

# Problems are now strictly loaded dynamically
PROBLEMS = load_problems()

# --- Page 0: Name Entry ---
if st.session_state.user_name is None:
    st.title("🛡️ Engineering Mechanics Portal")
    st.markdown("### Texas A&M University - Corpus Christi")
    with st.form("name_form"):
        name_input = st.text_input("Enter your Full Name to begin")
        if st.form_submit_button("Access Tutor"):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                st.rerun()
            else:
                st.warning("Identification is required for academic reporting.")
    st.stop()

# --- Page 1: Main Menu ---
if st.session_state.page == "landing":
    st.title(f"🚀 Welcome, {st.session_state.user_name}!")
    st.info("Texas A&M University - Corpus Christi | Dr. Dugan Um")
    
    # Section A: Interactive Lectures
    st.markdown("---")
    st.subheader("💡 Interactive Learning Agents")
    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    lectures = [
        ("Projectile Motion", "K_2.2"), 
        ("Normal & Tangent", "K_2.3"), 
        ("Polar Coordinates", "K_2.4"),
        ("Relative Motion", "K_2.5")
    ]
    for i, (name, pref) in enumerate(lectures):
        with [col_l1, col_l2, col_l3, col_l4][i]:
            if st.button(f"🎓 Lecture: {name}", key=f"lec_{pref}", use_container_width=True):
                st.session_state.lecture_topic = name
                st.session_state.page = "lecture"
                st.session_state.lecture_session = None 
                st.rerun()

    # Section B: Practice Problems
    st.markdown("---")
    st.subheader("📝 Engineering Review Problems")
    
    categories = {}
    for p in PROBLEMS:
        raw_cat = p.get('category', 'General').split(":")[0].strip()
        clean_cat = raw_cat.replace("HW 6", "").replace("HW 7", "").replace("HW 8", "").strip()
        low_cat = clean_cat.lower()
        
        # Mapping Logic
        if "statics" in low_cat:
            cat_main = "00_Statics"
        elif "kinematics" in low_cat and "rigid" not in low_cat and "rotation" not in low_cat:
            cat_main = "01_Kinematics of Particle"
        elif "rectilinear" in low_cat:
            cat_main = "02_Kinetics of Particles (Rectilinear)"
        elif "curvilinear" in low_cat:
            cat_main = "03_Kinetics of Particles (Curvilinear)"
        elif "work" in low_cat or "energy" in low_cat:
            cat_main = "04_Work and Energy"
        elif "impulse" in low_cat or "momentum" in low_cat:
            cat_main = "05_Impulse and Momentum"
        elif "impact" in low_cat:
            cat_main = "06_Impact"
        elif "rotation" in low_cat or "rigid" in low_cat:
            cat_main = "07_Kinematics of Rigid Body"
        else:
            cat_main = clean_cat
            
        if cat_main not in categories: categories[cat_main] = []
        categories[cat_main].append(p)

    sorted_cat_keys = sorted(categories.keys())
    for cat_key in sorted_cat_keys:
        probs = categories[cat_key]
        display_name = re.sub(r'^[0-9]+_', '', cat_key) 
        
        st.markdown(f"#### {display_name}")
        for i in range(0, len(probs), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(probs):
                    prob = probs[i + j]
                    sub_label = prob["hw_subtitle"].capitalize() if "hw_subtitle" in prob else prob.get('category', '').split(":")[-1].strip()
                    if sub_label == display_name or not sub_label:
                        sub_label = f"Problem {prob['id']}"
                        
                    with cols[j]:
                        if st.button(f"**{sub_label}**\n({prob['id']})", key=f"btn_{prob['id']}", use_container_width=True):
                            st.session_state.current_prob = prob
                            st.session_state.page = "chat"
                            if prob['id'] in st.session_state.chat_sessions:
                                del st.session_state.chat_sessions[prob['id']]
                            st.rerun()
    st.markdown("---")

# --- Page 2: Socratic Chat ---
elif st.session_state.page == "chat":
    prob = st.session_state.current_prob
    p_id = prob['id']
    if p_id not in st.session_state.grading_data: st.session_state.grading_data[p_id] = {'solved': set()}
    solved = st.session_state.grading_data[p_id]['solved']
    
    top_cols = st.columns([1, 1])
    with top_cols[0]:
        st.subheader(f"📌 {prob['category']}")
        st.info(prob['statement'])
        st.image(render_problem_diagram(prob), width=450)
    
    with top_cols[1]:
        st.subheader("💬 Socratic Tutor")
        chat_container = st.container(height=450)
        
        if p_id not in st.session_state.chat_sessions:
            sys_prompt = (
                f"You are the Engineering Tutor for {st.session_state.user_name} at TAMUCC. "
                f"REFERENCE DATA: {prob['statement']}. Guide using Socratic questions."
            )
            try:
                model = get_gemini_model(sys_prompt)
                st.session_state.chat_sessions[p_id] = model.start_chat(history=[])
            except Exception as e:
                st.error(f"Initialization Error: {e}")

        with chat_container:
            if p_id in st.session_state.chat_sessions:
                for message in st.session_state.chat_sessions[p_id].history:
                    with st.chat_message("assistant" if message.role == "model" else "user"):
                        st.markdown(message.parts[0].text)

        if user_input := st.chat_input("Your analysis..."):
            for target, val in prob['targets'].items():
                if target not in solved and check_numeric_match(user_input, val):
                    st.session_state.grading_data[p_id]['solved'].add(target)
                    st.toast(f"✅ Correct!", icon="🎯")
            
            if p_id in st.session_state.chat_sessions:
                st.session_state.chat_sessions[p_id].send_message(user_input)
                st.rerun()

    # --- UPDATED SUBMISSION LOGIC: Fixed Missing chat_history ---
    st.markdown("---")
    if st.button("📊 Submit Progress Report", use_container_width=True):
        try:
            with st.spinner("Processing report..."):
                # Retrieve history for the current session
                current_history = []
                if p_id in st.session_state.chat_sessions:
                    current_history = st.session_state.chat_sessions[p_id].history
                
                # Pass user_name, grading_data, and the retrieved history
                report_text = analyze_and_send_report(
                    st.session_state.user_name, 
                    st.session_state.grading_data,
                    current_history
                )
                
                st.session_state.last_report = report_text
                st.session_state.page = "report_view"
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ Email Delivery Failed: {str(e)}")
            st.info("Check your EMAIL_PASS (App Password) and RECEIVER_EMAIL variables in Railway.")

    if st.button("🏠 Exit to Home", use_container_width=True):
        st.session_state.page = "landing"
        st.rerun()

# --- Page 3: Mastery Report View ---
elif st.session_state.page == "report_view":
    st.title("📊 Session Mastery Report")
    if "last_report" in st.session_state:
        st.markdown(st.session_state.last_report)
    if st.button("🏠 Return to Main Menu", use_container_width=True):
        st.session_state.page = "landing"
        st.rerun()

# --- Page 4: Interactive Lecture ---
elif st.session_state.page == "lecture":
    st.title(f"🎓 Interactive Lecture: {st.session_state.lecture_topic}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⚙️ Simulation Controls")
        
        topic_clean = st.session_state.lecture_topic.lower().strip()
        params = {}
        
        if "projectile" in topic_clean:
            v0 = st.slider("Initial Velocity ($v_0$)", 0.0, 100.0, 50.0)
            angle = st.slider("Launch Angle (θ)", -90, 90, 0, step=5)
            gravity = st.slider("Gravity ($g$)", 0.0, 20.0, 10.0)
            params = {"v0": v0, "angle": angle, "g": gravity}
        elif "normal" in topic_clean or "tangent" in topic_clean:
            v = st.slider("Speed ($v$)", 0.0, 100.0, 50.0)
            rho = st.slider("Radius of Curvature (ρ)", 10.0, 500.0, 255.0)
            at = st.slider("Tangential Accel ($a_t$)", -10.0, 10.0, 0.0)
            params = {"v": v, "rho": rho, "at": at}
        elif "polar" in topic_clean:
            r = st.slider("Radius ($r$)", 0.0, 10.0, 5.0)
            rdot = st.slider("Radial Velocity ($\dot{r}$)", -10.0, 10.0, 0.0)
            theta_dot = st.slider("Angular Velocity ($\dot{θ}$)", -5.0, 5.0, 0.0)
            params = {"r": r, "rdot": rdot, "theta_dot": theta_dot}
        elif "relative" in topic_clean:
            va = st.slider("Velocity A ($v_A$)", -50.0, 50.0, 0.0)
            vb = st.slider("Velocity B ($v_B$)", -50.0, 50.0, 0.0)
            params = {"vA": va, "vB": vb}
        else:
            st.info(f"Interactive knobs for '{st.session_state.lecture_topic}' are under development.")

        st.markdown("### 📈 Visual Overview")
        st.image(render_lecture_visual(st.session_state.lecture_topic, params), use_container_width=True)
        
    with col2:
        st.subheader("💬 Socratic Discussion")
        lecture_chat = st.container(height=500)
        
        if st.session_state.lecture_session is None:
            lec_prompt = (
                f"You are a Socratic Professor teaching {st.session_state.lecture_topic}. "
                "Guide the student by asking conceptual questions. Refer to their simulation parameters if mentioned."
            )
            model = get_gemini_model(lec_prompt)
            st.session_state.lecture_session = model.start_chat(history=[])

        with lecture_chat:
            for message in st.session_state.lecture_session.history:
                with st.chat_message("assistant" if message.role == "model" else "user"):
                    st.markdown(message.parts[0].text)
            if not st.session_state.lecture_session.history:
                st.write(f"Welcome to the lecture on **{st.session_state.lecture_topic}**. Adjust the sliders and let's begin...")

        if lec_input := st.chat_input("Discuss the topic..."):
            st.session_state.lecture_session.send_message(lec_input)
            st.rerun()

    if st.button("🏠 Exit Lecture", use_container_width=True):
        st.session_state.page = "landing"
        st.rerun()
