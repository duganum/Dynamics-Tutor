import streamlit as st
import google.generativeai as genai
import json
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_gemini_model(system_instruction):
    """Gemini 2.0 Flash 모델을 설정하고 반환합니다."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(
            model_name='models/gemini-2.0-flash', 
            system_instruction=system_instruction
        )
    except Exception as e:
        st.error(f"Gemini 초기화 실패: {e}")
        return None

def load_problems():
    """저장소의 JSON 파일에서 문제 목록을 불러오고 새 문제를 병합합니다."""
    # New problems to be integrated (Impact Problems 239, 249, 252 added)
    new_problems = [
        {
            "id": "176",
            "category": "Impulse and Momentum",
            "statement": "A 75-g projectile traveling at 600 m/s strikes and becomes embedded in the 50-kg block, which is initially stationary. Compute the energy lost during the impact. Express your answer as an absolute value |ΔE| and as a percentage n of the original system energy E.",
            "targets": { "|ΔE|": 13480, "n": 99.85 },
            "required_units": ["J", "%"]
        },
        {
            "id": "198",
            "category": "Impulse and Momentum",
            "statement": "The 450-kg ram of a pile driver falls 1.4 m from rest and strikes the top of a 240-kg pile embedded 0.9 m in the ground. Upon impact the ram is seen to move with the pile with no noticeable rebound. Determine the velocity v of the pile and ram immediately after impact.",
            "targets": { "v": 3.42 },
            "required_units": ["m/s"]
        },
        {
            "id": "209",
            "category": "Work and Energy / Momentum",
            "statement": "The cylindrical plug A of mass m_A is released from rest at B and slides down the smooth circular guide. The plug strikes the block C and becomes embedded in it. Write the expression for the distance s which the block and plug slide before coming to rest. The coefficient of kinetic friction between the block and the horizontal surface is μ_k.",
            "targets": { "s": "m_A^2 * r / (μ_k * (m_A + m_C)^2)" },
            "required_units": ["m"]
        },
        {
            "id": "239",
            "category": "Impact",
            "statement": "Tennis balls are usually rejected if they fail to rebound to waist level when dropped from shoulder level. If a ball just passes the test as indicated in the figure, determine the coefficient of restitution $e$ and the percentage $n$ of the original energy lost during the impact.",
            "targets": { "e": 0.829, "n": 31.2 },
            "required_units": ["unitless", "%"]
        },
        {
            "id": "249",
            "category": "Impact",
            "statement": "In the selection of the ram of a pile driver, it is desired that the ram lose all of its kinetic energy at each blow. Hence, the velocity of the ram is zero immediately after impact. The mass of each pile to be driven is 300 kg, and experience has shown that a coefficient of restitution of 0.3 can be expected. What should be the mass $m$ of the ram? Compute the velocity $v$ of the pile immediately after impact if the ram is dropped from a height of 4 m onto the pile. Also compute the energy loss $\Delta E$ due to impact at each blow.",
            "targets": { "m": 90.0, "v": 2.66, "\Delta E|": 3530 },
            "required_units": ["kg", "m/s", "J"]
        },
        {
            "id": "252",
            "category": "Impact",
            "statement": "Determine the value of the coefficient of restitution $e$ which results in the final velocity $v'$ being perpendicular to the initial velocity $v$. The initial velocity $v$ makes an angle of 60° with the wall as shown.",
            "targets": { "e": 0.333 },
            "required_units": ["unitless"]
        }
    ]

    try:
        with open('problems_v2_GitHub.json', 'r') as f:
            problems = json.load(f)
            
        # Merge logic: Add new problems if they don't already exist by ID
        existing_ids = {p['id'] for p in problems}
        for np in new_problems:
            if np['id'] not in existing_ids:
                problems.append(np)
        return problems
    except Exception as e:
        # If file doesn't exist yet, just return the new problems
        return new_problems

def check_numeric_match(user_val, correct_val, tolerance=0.05):
    """숫자를 추출하여 정답과 5% 오차 범위 내에 있는지 확인합니다."""
    try:
        # If correct_val is a string (like the expression in prob 209), skip numeric check
        if isinstance(correct_val, str):
            # Basic string cleanup for expression matching
            u_clean = str(user_val).replace(" ", "").lower()
            c_clean = str(correct_val).replace(" ", "").lower()
            return c_clean in u_clean

        u_match = re.search(r"[-+]?\d*\.\d+|\d+", str(user_val))
        if not u_match: return False
        u = float(u_match.group())
        c = float(correct_val)
        if c == 0: return abs(u) < tolerance
        return abs(u - c) <= abs(tolerance * c)
    except (ValueError, TypeError, AttributeError):
        return False

def get_footer_info(prob):
    """Extracts title and subtitle for the bottom UI line."""
    title = prob.get("hw_title")
    subtitle = prob.get("hw_subtitle")
    if title and subtitle:
        return f"{title} ({subtitle})"
    return prob.get("category", "Engineering Practice")

def evaluate_understanding_score(chat_history):
    """대화 내용을 바탕으로 이해도를 0-10점으로 평가합니다."""
    eval_instruction = (
        "You are a strict Engineering Professor at Texas A&M University - Corpus Christi. "
        "Evaluate the student's level of understanding (0-10) based ONLY on the chat history.\n\n"
        "STRICT SCORING RUBRIC:\n"
        "0-3: Little participation, irrelevant answers.\n"
        "4-5: Good engagement but lacks governing equations or proper LaTeX.\n"
        "6-8: Correctly identifying and using relevant equations in LaTeX.\n"
        "9-10: Complete mastery with flawless physics logic.\n\n"
        "Output ONLY the integer."
    )
    
    model = get_gemini_model(eval_instruction)
    if not model: return 0

    try:
        response = model.generate_content(f"Chat history to evaluate:\n{chat_history}")
        score_match = re.search(r"\d+", response.text)
        if score_match:
            score = int(score_match.group())
            return min(max(score, 0), 10)
        return 0
    except Exception:
        return 0

def analyze_and_send_report(user_name, topic_title, chat_history):
    """세션을 분석하여 이메일 리포트를 전송합니다."""
    score = evaluate_understanding_score(chat_history)
    
    report_instruction = (
        "You are an academic evaluator. Analyze this engineering session.\n"
        "Your report must include: Overview, Score, Mathematical Rigor, Concept Mastery, Engagement, and Student Feedback quote."
    )
    
    model = get_gemini_model(report_instruction)
    if not model: return "AI Analysis Unavailable"

    prompt = (
        f"Student Name: {user_name}\n"
        f"Topic: {topic_title}\n"
        f"Assigned Score: {score}/10\n\n"
        f"DATA:\n{chat_history}\n\n"
        "Format the report professionally for Dr. Dugan Um. Use LaTeX for math."
    )
    
    try:
        response = model.generate_content(prompt)
        report_text = response.text
    except Exception as e:
        report_text = f"Analysis failed: {str(e)}"

    # Email Logic
    try:
        sender = st.secrets["EMAIL_SENDER"]
        password = st.secrets["EMAIL_PASSWORD"] 
        receiver = "dugan.um@gmail.com" 

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = f"Eng. Tutor ({user_name}): {topic_title} [Score: {score}/10]"
        msg.attach(MIMEText(report_text, 'plain'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"SMTP Error: {e}")
    
    return report_text
