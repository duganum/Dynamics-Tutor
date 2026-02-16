import streamlit as st
import json
import re
import numpy as np
import matplotlib.pyplot as plt
from google.api_core import exceptions  # Added for rate limit handling
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
        
        if "statics" in low_cat:
            cat_main = "00_Statics"
        elif "kinematics" in low_cat and "particle" not in low_cat:
            cat_main = "01_Particle Kinematics"
        elif "curvilinear" in low_cat:
            cat_main = "02_Kinetics of Particles (Curvilinear)"
        elif "rectilinear" in low_cat:
            cat_main = "03_Kinetics of Particles (Rectilinear)"
        elif "work" in low_cat or "energy" in low_cat:
            cat_main = "zzz_Work and Energy"  
        else:
            cat_main = clean_cat
            
        if cat_main not in categories: categories[cat_main] = []
        categories[cat_main].append(p)

    sorted_cat_keys = sorted(categories.keys())
    for cat_key in sorted_cat_keys:
        probs = categories[cat_key]
        display_name = re.sub(r'^[0-9a-z_]+_', '', cat_key) 
        
        st.markdown(f"#### {display_name}")
        for i in range(0, len(probs), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(probs):
                    prob = probs[i + j]
                    sub_label = prob["hw_subtitle"].capitalize() if "hw_subtitle" in prob else prob.get('category', '').split(":")[-1].strip()
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
        st.image(render_problem_diagram(prob), width=350)
    
    with top_cols[1]:
        st.subheader("💬 Socratic Tutor")
        chat_container = st.container(height=400)
        with chat_container:
            if p_id not in st.session_state.chat_sessions:
                sys_prompt = (
                    f"You are the Engineering Tutor for {st.session_state.user_name} at TAMUCC. "
                    f"Context: {prob['statement']}. Use LaTeX for all math. "
                    "STRICT SOCRATIC RULES: 1. NEVER give a full explanation. 2. Guide them step-by-step."
                )
                # Defensive call to model initialization
                try:
                    model = get_gemini_model(sys_prompt)
                    st.session_state.chat_sessions[p_id] = model.start_chat(history=[])
                except Exception:
                    st.error("Could not reach the AI service. Please refresh.")

            if p_id in st.session_state.chat_sessions:
                for message in st.session_state.chat_sessions[p_id].history:
                    with st.chat_message("assistant" if message.role == "model" else "user"):
                        st.markdown(message.parts[0].text)

                if not st.session_state.chat_sessions[p_id].history:
                    st.write(f"👋 **Tutor Ready.** Hello {st.session_state.user_name}. Please describe your first step.")

        if user_input := st.chat_input("Your analysis..."):
            for target, val in prob['targets'].items():
                if target not in solved and check_numeric_match(user_input, val):
                    st.session_state.grading_data[p_id]['solved'].add(target)
            
            # Rate Limit Protection Wrapper
            try:
                with st.spinner("Tutor is thinking..."):
                    st.session_state.chat_sessions[p_id].send_message(user_input)
                st.rerun()
            except exceptions.ResourceExhausted:
                st.error("⚠️ System limit reached. Please wait 60 seconds before sending another message.")
            except Exception as e:
                st.warning("⚠️ The professor is busy right now. Please try again in a moment.")

    st.markdown("---")
    bot_col1, bot_col2 = st.columns([2, 1])
    
    with bot_col1:
        st.markdown("### 📝 Session Analysis")
        feedback = st.text_area("Notes for Dr. Um:", placeholder="Please provide feedback.", height=100)
        
    with bot_col2:
        st.write("Click below to finalize this session.")
        if st.button("🚀 Submit Session", use_container_width=True):
            history_text = ""
            if p_id in st.session_state.chat_sessions:
                for msg in st.session_state.chat_sessions[p_id].history:
                    role = "Tutor" if msg.role == "model" else "Student"
                    history_text += f"{role}: {msg.parts[0].text}\n"
            
            try:
                with st.spinner("Analyzing mastery..."):
                    report = analyze_and_send_report(st.session_state.user_name, prob['category'], history_text + feedback)
                    st.session_state.last_report = report
                    st.session_state.page = "report_view"
                    st.rerun()
            except exceptions.ResourceExhausted:
                st.error("Rate limit hit during reporting. Please wait a minute and try again.")
            except Exception:
                st.error("An error occurred while generating the report.")
        
        if st.button("🏠 Exit to Home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
