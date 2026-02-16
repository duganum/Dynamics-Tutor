import streamlit as st
import json
import re
import numpy as np
import matplotlib.pyplot as plt
from logic_v2_GitHub import get_gemini_model, load_problems, check_numeric_match, analyze_and_send_report
from render_v2_GitHub import render_problem_diagram, render_lecture_visual

# 1. Page Configuration
st.set_page_config(page_title="Socratic Engineering Tutor", layout="wide")

# 2. CSS: Minimal Button Height (60px) and UI consistency
st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

# 3. Initialize Session State
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_sessions" not in st.session_state: st.session_state.chat_sessions = {}
if "grading_data" not in st.session_state: st.session_state.grading_data = {}
if "user_name" not in st.session_state: st.session_state.user_name = None
if "lecture_topic" not in st.session_state: st.session_state.lecture_topic = None
if "lecture_session" not in st.session_state: st.session_state.lecture_session = None

# Updated PROBLEM list including the new Work and Energy problems
# In a production environment, these would be loaded via load_problems() if updated in the source JSON
PROBLEMS = [
    {
        "id": "WE_3.1_1",
        "category": "Work and Energy",
        "statement": "A 2-kg collar is attached to a spring ($k = 30$ N/m, unstretched length = 1.5 m) and is released from rest at A. It slides up a smooth vertical rod under a constant 50-N force acting at a 30-degree angle from the rod. Calculate the velocity $v$ of the collar as it passes position B, located 1.5 m above A. Use $g = 9.81$ m/s$^2$.",
        "targets": { "v": 5.06 },
        "required_units": ["m/s"]
    },
    {
        "id": "WE_3.1_2",
        "category": "Work and Energy",
        "statement": "A 5-kg cylinder is released from rest 100 mm above a spring with stiffness $k = 1.8$ kN/m. Determine the maximum compression $x_{max}$ of the spring. Use $g = 9.81$ m/s$^2$.",
        "targets": { "x_{max}": 0.105 },
        "required_units": ["m", "mm"]
    },
    {
        "id": "WE_3.1_3",
        "category": "Work and Energy",
        "statement": "A 175-lb pole vaulter carries a uniform 16-ft, 10-lb pole. The center of gravity of the vaulter and the horizontal pole are both 42 in. above the ground during the approach. If he barely clears a bar at 18 ft with zero velocity, calculate the minimum initial velocity $v$ required.",
        "targets": { "v": 30.5 },
        "required_units": ["ft/sec"]
    }
] + load_problems()

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
        clean_cat = raw_cat.replace("HW 6", "").replace("HW 7", "").strip()
        
        if "kinematics" in clean_cat.lower() and "particle" not in clean_cat.lower():
            cat_main = "Particle Kinematics"
        elif "curvilinear" in clean_cat.lower():
            cat_main = "Kinetics of Particles (Curvilinear)"
        elif "rectilinear" in clean_cat.lower():
            cat_main = "Kinetics of Particles (Rectilinear)"
        elif "work" in clean_cat.lower() or "energy" in clean_cat.lower():
            cat_main = "Work and Energy"
        else:
            cat_main = clean_cat
            
        if cat_main not in categories: categories[cat_main] = []
        categories[cat_main].append(p)

    for cat_name, probs in categories.items():
        st.markdown(f"#### {cat_name}")
        for i in range(0, len(probs), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(probs):
                    prob = probs[i + j]
                    if "hw_subtitle" in prob:
                        sub_label = prob["hw_subtitle"].capitalize()
                    else:
                        sub_label = prob.get('category', '').split(":")[-1].strip()
                        
                    with cols[j]:
                        if st.button(f"**{sub_label}**\n({prob['id']})", key=f"btn_{prob['id']}", use_container_width=True):
                            st.session_state.current_prob = prob
                            st.session_state.page = "chat"
                            if prob['id'] in st.session_state.chat_sessions:
                                del st.session_state.chat_sessions[prob['id']]
                            st.rerun()
    st.markdown("---")

# --- Page 2: Socratic Chat (Practice Problems) ---
elif st.session_state.page == "chat":
    prob = st.session_state.current_prob
    p_id = prob['id']
    if p_id not in st.session_state.grading_data: st.session_state.grading_data[p_id] = {'solved': set()}
    solved = st.session_state.grading_data[p_id]['solved']
    
    cols = st.columns([2, 1])
    with cols[0]:
        st.subheader(f"📌 {prob['category']}")
        st.info(prob['statement'])
        # Dynamic rendering of diagrams based on ID
        st.image(render_problem_diagram(prob), width=400)
    
    with cols[1]:
        st.markdown("### 📝 Session Analysis")
        st.write("Work through the derivation with the tutor below.")
        
        feedback = st.text_area("Notes for Dr. Um:", placeholder="Please provide a feedback to your professor.")
        if st.button("⬅️ Submit Session", use_container_width=True):
            history_text = ""
            if p_id in st.session_state.chat_sessions:
                for msg in st.session_state.chat_sessions[p_id].history:
                    role = "Tutor" if msg.role == "model" else "Student"
                    history_text += f"{role}: {msg.parts[0].text}\n"
            
            with st.spinner("Analyzing mastery..."):
                report = analyze_and_send_report(st.session_state.user_name, prob['category'], history_text + feedback)
                st.session_state.last_report = report
                st.session_state.page = "report_view"
                st.rerun()

    st.markdown("---")
    
    chat_container = st.container(height=400)
    with chat_container:
        if p_id not in st.session_state.chat_sessions:
            sys_prompt = (
                f"You are the Engineering Tutor for {st.session_state.user_name} at TAMUCC. "
                f"Context: {prob['statement']}. Use LaTeX for all math. "
                "STRICT SOCRATIC RULES: 1. NEVER give a full explanation. 2. Break every concept into tiny steps."
            )
            model = get_gemini_model(sys_prompt)
            st.session_state.chat_sessions[p_id] = model.start_chat(history=[])

        for message in st.session_state.chat_sessions[p_id].history:
            with st.chat_message("assistant" if message.role == "model" else "user"):
                st.markdown(message.parts[0].text)

        if not st.session_state.chat_sessions[p_id].history:
            st.write(f"👋 **Tutor Ready.** Hello {st.session_state.user_name}. Please describe the first step of your analysis to begin.")

    if user_input := st.chat_input("Your analysis..."):
        for target, val in prob['targets'].items():
            if target not in solved and check_numeric_match(user_input, val):
                st.session_state.grading_data[p_id]['solved'].add(target)
        try:
           st.session_state.chat_sessions[p_id].send_message(user_input)
           st.rerun()
        except Exception:
           st.warning("⚠️ The professor is a little busy right now.")

# --- Page 3: Interactive Lecture ---
elif st.session_state.page == "lecture":
    topic = st.session_state.lecture_topic
    st.title(f"🎓 Lab: {topic}")
    col_sim, col_chat = st.columns([1, 1])
    
    with col_sim:
        params = {}
        if topic == "Projectile Motion":
            params['v0'] = st.slider("v0", 5, 100, 30)
            params['angle'] = st.slider("theta", 0, 90, 45)
        elif topic == "Normal & Tangent":
            params['v'] = st.slider("v", 1, 50, 20)
            params['rho'] = st.slider("rho", 5, 100, 50)
            st.latex(r"a_n = \frac{v^2}{\rho}")
        elif topic == "Polar Coordinates":
            params['r'] = st.slider("r", 1, 50, 20)
            params['theta'] = st.slider("theta", 0, 360, 45)
        elif topic == "Relative Motion":
            params['vA'] = [st.slider("vA_x", -20, 20, 15), st.slider("vA_y", -20, 20, 5)]
            params['vB'] = [st.slider("vB_x", -20, 20, 10), st.slider("vB_y", -20, 20, -5)]
            st.latex(r"\vec{v}_A = \vec{v}_B + \vec{v}_{A/B}")
        
        lecture_img = render_lecture_visual(topic, params)
        if lecture_img:
            st.image(lecture_img, use_container_width=False)
        else:
            st.error("Failed to render simulation diagram.")

        st.markdown("---")
        lecture_feedback = st.text_area("Final Summary:", placeholder="Provide feedback to your professor.")
        if st.button("🚀 Submit Lecture Report", use_container_width=True):
            history_text = ""
            if st.session_state.lecture_session:
                for msg in st.session_state.lecture_session.history:
                    role = "Professor" if msg.role == "model" else "Student"
                    history_text += f"{role}: {msg.parts[0].text}\n"
            with st.spinner("Analyzing mastery..."):
                report = analyze_and_send_report(st.session_state.user_name, f"LECTURE: {topic}", history_text + lecture_feedback)
                st.session_state.last_report = report
                st.session_state.page = "report_view"
                st.rerun()

        if st.button("🏠 Exit", use_container_width=True):
            st.session_state.lecture_session = None
            st.session_state.page = "landing"
            st.rerun()

    with col_chat:
        st.subheader("💬 Socratic Discussion")
        
        lecture_chat_container = st.container(height=500)
        with lecture_chat_container:
            initial_greeting = f"Hello {st.session_state.user_name}. Looking at the {topic} simulation, what do you notice about the motion?"
            
            if st.session_state.lecture_session is not None:
                for msg in st.session_state.lecture_session.history:
                    with st.chat_message("assistant" if msg.role == "model" else "user"):
                        st.markdown(msg.parts[0].text)
            else:
                with st.chat_message("assistant"):
                    st.markdown(initial_greeting)
        
        if lecture_input := st.chat_input("Discuss the physics..."):
            try:
                if st.session_state.lecture_session is None:
                    sys_msg = (
                        f"You are a Professor teaching {topic}. Respond only in English and use LaTeX. "
                        "SOCRATIC PEDAGOGY: Do not explain theories directly. Guide them step-by-step."
                    )
                    model = get_gemini_model(sys_msg)
                    st.session_state.lecture_session = model.start_chat(history=[
                        {"role": "user", "parts": ["Hi Professor."]},
                        {"role": "model", "parts": [initial_greeting]}
                    ])
                
                st.session_state.lecture_session.send_message(lecture_input)
                st.rerun()
            except Exception:
                st.warning("⚠️ The professor is a little busy right now.")

# --- Page 4: Report View ---
elif st.session_state.page == "report_view":
    st.title("📊 Performance Summary")
    st.markdown(st.session_state.get("last_report", "No report available."))
    if st.button("Return to Main Menu"):
        st.session_state.page = "landing"
        st.rerun()
