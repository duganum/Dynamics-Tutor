import json
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai
import streamlit as st


def get_gemini_model(system_instruction):
    """Configures and returns the Gemini model."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            system_instruction=system_instruction,
        )
    except Exception as e:
        st.error(f"Gemini initialization error: {e}")
        return None


def load_problems():
    """Loads problems from JSON and merges new problems cleanly."""
    new_problems = [
        {
            "id": "176",
            "category": "Impulse and Momentum",
            "statement": (
                r"A 75-g projectile traveling at 600 m/s strikes and becomes embedded in "
                r"the 50-kg block, which is initially stationary. Compute the energy lost during "
                r"the impact. Express your answer as an absolute value |\Delta E| and as a "
                r"percentage n of the original system energy E."
            ),
            "targets": {"|\\Delta E|": 13480, "n": 99.85},
            "required_units": ["J", "%"],
        },
        {
            "id": "198",
            "category": "Impulse and Momentum",
            "statement": (
                r"The 450-kg ram of a pile driver falls 1.4 m from rest and strikes the top "
                r"of a 240-kg pile embedded 0.9 m in the ground. Upon impact the ram is seen "
                r"to move with the pile with no noticeable rebound. Determine the velocity v "
                r"of the pile and ram immediately after impact."
            ),
            "targets": {"v": 3.42},
            "required_units": ["m/s"],
        },
        {
            "id": "209",
            "category": "Work and Energy / Momentum",
            "statement": (
                r"The cylindrical plug A of mass m_A is released from rest at B and slides down "
                r"the smooth circular guide. The plug strikes the block C and becomes embedded in it. "
                r"Write the expression for the distance s which the block and plug slide before coming "
                r"to rest. The coefficient of kinetic friction between the block and the horizontal "
                r"surface is \mu_k."
            ),
            "targets": {"s": "m_A^2 * r / (\mu_k * (m_A + m_C)^2)"},
            "required_units": ["m"],
        },
        {
            "id": "239",
            "category": "Impact",
            "statement": (
                r"Tennis balls are usually rejected if they fail to rebound to waist level "
                r"when dropped from shoulder level. If a ball just passes the test as indicated "
                r"in the figure, determine the coefficient of restitution e and the percentage n "
                r"of the original energy lost during the impact."
            ),
            "targets": {"e": 0.829, "n": 31.2},
            "required_units": ["unitless", "%"],
        },
        {
            "id": "249",
            "category": "Impact",
            "statement": (
                r"In the selection of the ram of a pile driver, it is desired that the ram "
                r"lose all of its kinetic energy at each blow. Hence, the velocity of the ram "
                r"is zero immediately after impact. The mass of each pile to be driven is 300 kg, "
                r"and experience has shown that a coefficient of restitution of 0.3 can be expected. "
                r"What should be the mass m of the ram? Compute the velocity v of the pile "
                r"immediately after impact if the ram is dropped from a height of 4 m onto the pile. "
                r"Also compute the energy loss \Delta E due to impact at each blow."
            ),
            "targets": {"m": 90.0, "v": 2.66, r"|\Delta E|": 3530},
            "required_units": ["kg", "m/s", "J"],
        },
        {
            "id": "252",
            "category": "Impact",
            "statement": (
                r"Determine the value of the coefficient of restitution e which results in "
                r"the final velocity v' being perpendicular to the initial velocity v. The "
                r"initial velocity v makes an angle of 60° with the wall as shown."
            ),
            "targets": {"e": 0.333},
            "required_units": ["unitless"],
        },
        {
            "id": "K_2.6_1",
            "category": "Rigid Body Kinematics (Rotation)",
            "statement": (
                r"For the instant represented, point B crosses the horizontal axis through "
                r"point O with a downward velocity v = 0.6 m/s. Determine the corresponding "
                r"value of the angular velocity \omega_{OA} of link OA. Length OA = 130 mm, "
                r"length AB = 90 mm, horizontal distance OB = 180 mm."
            ),
            "targets": {"omega_OA": 10.0},
            "required_units": ["rad/s"],
        },
        {
            "id": "K_2.6_2",
            "category": "Rigid Body Kinematics (Rotation)",
            "statement": (
                r"The mass center G of the car has a velocity of 40 mi/hr at position A "
                r"and 1.52 seconds later at B has a velocity of 50 mi/hr. The radius of "
                r"curvature of the road at B is 180 ft. Calculate the angular velocity \omega "
                r"of the car at B and the average angular velocity \omega_{av} of the car "
                r"between A and B. Initial angle is 30° from vertical at A."
            ),
            "targets": {"omega_B": 0.407, "omega_av": 0.344},
            "required_units": ["rad/sec"],
        },
        {
            "id": "K_2.6_3",
            "category": "Rigid Body Kinematics (Rotation)",
            "statement": (
                r"The rotating arm starts from rest and acquires a rotational speed N = 600 rev/min "
                r"in 2 seconds with constant angular acceleration. Find the time t after starting "
                r"before the acceleration vector of end P (at radius 6 in) makes an angle of 45° "
                r"with the arm OP."
            ),
            "targets": {"t": 0.1784},
            "required_units": ["s"],
        },
    ]

    try:
        if os.path.exists("problems_v2_GitHub.json"):
            with open("problems_v2_GitHub.json", "r", encoding="utf-8") as f:
                problems = json.load(f)
        else:
            problems = []

        existing_ids = {p["id"] for p in problems}
        for np in new_problems:
            if np["id"] not in existing_ids:
                problems.append(np)
        return problems
    except Exception:
        return new_problems


def check_numeric_match(user_val, correct_val, tolerance=0.05):
    """Compares numeric user entry against correct value within tolerance."""
    try:
        if isinstance(correct_val, str):
            u_clean = str(user_val).replace(" ", "").lower()
            c_clean = str(correct_val).replace(" ", "").lower()
            return c_clean in u_clean

        u_match = re.search(r"[-+]?\d*\.\d+|\d+", str(user_val))
        if not u_match:
            return False
        u = float(u_match.group())
        c = float(correct_val)
        if c == 0:
            return abs(u) < tolerance
        return abs(u - c) <= abs(tolerance * c)
    except (ValueError, TypeError, AttributeError):
        return False


def get_footer_info(prob):
    """Extracts title and subtitle for footer display."""
    title = prob.get("hw_title")
    subtitle = prob.get("hw_subtitle")
    if title and subtitle:
        return f"{title} ({subtitle})"
    return prob.get("category", "Engineering Practice")


def evaluate_understanding_score(chat_history):
    """Evaluates student physical and mathematical understanding (0-10)."""
    if not chat_history or len(str(chat_history).strip()) == 0:
        return 0

    eval_instruction = r"""You are an Engineering Professor at Texas A&M University - Corpus Christi. Evaluate the student's level of physical and mathematical understanding (0-10) on the FIRST attempt based ONLY on the transcript.

CORE EVALUATION RULE:
If the student successfully solves the assigned problem and arrives at the correct physics principles/solution, assign a 10/10. Do NOT dock points for receiving tutor guidance, taking multiple steps, or solving only a single problem.

SCORING DIRECTIVES:
10/10: Problem solved correctly. The student completed the required physics steps, applied correct equations, and obtained the correct final target values.
7-9/10: Correct setup and physics reasoning, but minor arithmetic/conversion errors prevented exact final execution.
4-6/10: Partial setup achieved, but key governing equations were missed or incomplete.
1-3/10: Minimal participation, off-topic, or refused to engage with hints.
0/10: No attempt or empty history.

STRICT FORMAT DIRECTIVE:
Output ONLY the integer score (e.g., 10). Do not include any explanation or extra text."""

    model = get_gemini_model(eval_instruction)
    if not model:
        return 0

    try:
        response = model.generate_content(
            f"Chat history to evaluate:\n{chat_history}"
        )
        score_match = re.search(r"\d+", response.text)
        if score_match:
            score = int(score_match.group())
            return min(max(score, 0), 10)
        return 0
    except Exception:
        return 0


def analyze_and_send_report(user_name, topic_title, chat_history):
    """Generates session analysis report and emails results."""
    score = evaluate_understanding_score(chat_history)

    report_instruction = r"""You are an expert Engineering Education Evaluator for Dr. Dugan Um at TAMUCC. Analyze the session data and generate a concise mastery report in Markdown.

EVALUATION RULES:
1. If the score is 10/10, explicitly highlight that the student mastered the problem requirements on the first attempt.
2. Never mention 'score reconciliation', 'syllabus coverage', 'missing topics', or 'database errors'.
3. DO NOT use LaTeX document wrappers like \documentclass or \begin{document}.
4. Use standard Markdown headers (##, ###) and bold text (**).
5. Use inline LaTeX ONLY for math/physics formulas (e.g., $F=ma$).
6. REQUIRED SECTIONS: ## Overview, ## Score, ## Mathematical Rigor, ## Concept Mastery, ## Engagement, ## Recommendations."""

    model = get_gemini_model(report_instruction)
    if not model:
        return "AI Analysis Unavailable"

    prompt = (
        f"Student Name: {user_name}\n"
        f"Assigned Single Problem: {topic_title}\n"
        f"Assigned Score: {score}/10\n\n"
        f"SESSION CHAT HISTORY:\n{chat_history}\n\n"
        "Write the evaluation report."
    )

    try:
        response = model.generate_content(prompt)
        report_text = response.text
    except Exception as e:
        report_text = f"Analysis failed: {str(e)}"

    # Email Notification
    try:
        sender = st.secrets.get("EMAIL_SENDER")
        password = st.secrets.get("EMAIL_PASSWORD")
        receiver = "dugan.um@gmail.com"

        if sender and password:
            msg = MIMEMultipart()
            msg["From"] = sender
            msg["To"] = receiver
            msg["Subject"] = (
                f"Eng. Tutor ({user_name}): {topic_title} [Score: {score}/10]"
            )
            msg.attach(MIMEText(report_text, "plain"))

            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
    except Exception as e:
        print(f"SMTP Error: {e}")

    return report_text
