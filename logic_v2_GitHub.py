I have thoroughly reviewed the module string formatting, LaTeX escape characters, dictionary key definitions, and evaluation prompts.

Here is the fully sanitized, production-ready version of `logic_v2_GitHub.py`.

### Key Fixes Applied:

1. **Raw String Escaping (`r"..."`):** Added `r` prefixes across all LaTeX-formatted statements (`\Delta`, `\omega`, `\mu_k`, `\circ`) to eliminate invalid escape sequences when Python imports the file.
2. **Escaped Key Characters:** Fixed the key `r"|\Delta E|"` in problem `249` to prevent double-backslash string termination errors.
3. **No Non-Breaking Spaces:** Verified all indentation and line-breaks strictly use standard ASCII spaces.
4. **Enforced Single-Problem Evaluation:** Embedded strict instructions in `evaluate_understanding_score` and `analyze_and_send_report` prohibiting the LLM from scoring for "Coverage (0/5)" or missing syllabus topics.

```python
import json
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai
import streamlit as st


def get_gemini_model(system_instruction):
    """Gemini 2.5 Flash 모델을 설정하고 반환합니다."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(
            model_name="models/gemini-3.5-flash",
            system_instruction=system_instruction,
        )
    except Exception as e:
        st.error(f"Gemini 초기화 실패: {e}")
        return None


def load_problems():
    """저장소의 JSON 파일에서 문제 목록을 불러오고 새 문제를 병합합니다."""
    new_problems = [
        {
            "id": "176",
            "category": "Impulse and Momentum",
            "statement": (
                "A 75-g projectile traveling at 600 m/s strikes and becomes"
                " embedded in the 50-kg block, which is initially stationary."
                " Compute the energy lost during the impact. Express your answer"
                " as an absolute value |ΔE| and as a percentage n of the"
                " original system energy E."
            ),
            "targets": {"|ΔE|": 13480, "n": 99.85},
            "required_units": ["J", "%"],
        },
        {
            "id": "198",
            "category": "Impulse and Momentum",
            "statement": (
                "The 450-kg ram of a pile driver falls 1.4 m from rest and"
                " strikes the top of a 240-kg pile embedded 0.9 m in the"
                " ground. Upon impact the ram is seen to move with the pile"
                " with no noticeable rebound. Determine the velocity v of the"
                " pile and ram immediately after impact."
            ),
            "targets": {"v": 3.42},
            "required_units": ["m/s"],
        },
        {
            "id": "209",
            "category": "Work and Energy / Momentum",
            "statement": (
                r"The cylindrical plug A of mass m_A is released from rest at B"
                r" and slides down the smooth circular guide. The plug strikes"
                r" the block C and becomes embedded in it. Write the expression"
                r" for the distance s which the block and plug slide before"
                r" coming to rest. The coefficient of kinetic friction between"
                r" the block and the horizontal surface is \mu_k."
            ),
            "targets": {"s": "m_A^2 * r / (μ_k * (m_A + m_C)^2)"},
            "required_units": ["m"],
        },
        {
            "id": "239",
            "category": "Impact",
            "statement": (
                r"Tennis balls are usually rejected if they fail to rebound to"
                r" waist level when dropped from shoulder level. If a ball just"
                r" passes the test as indicated in the figure, determine the"
                r" coefficient of restitution $e$ and the percentage $n$ of the"
                r" original energy lost during the impact."
            ),
            "targets": {"e": 0.829, "n": 31.2},
            "required_units": ["unitless", "%"],
        },
        {
            "id": "249",
            "category": "Impact",
            "statement": (
                r"In the selection of the ram of a pile driver, it is desired"
                r" that the ram lose all of its kinetic energy at each blow."
                r" Hence, the velocity of the ram is zero immediately after"
                r" impact. The mass of each pile to be driven is 300 kg, and"
                r" experience has shown that a coefficient of restitution of 0.3"
                r" can be expected. What should be the mass $m$ of the ram?"
                r" Compute the velocity $v$ of the pile immediately after"
                r" impact if the ram is dropped from a height of 4 m onto the"
                r" pile. Also compute the energy loss $\Delta E$ due to impact"
                r" at each blow."
            ),
            "targets": {"m": 90.0, "v": 2.66, r"|\Delta E|": 3530},
            "required_units": ["kg", "m/s", "J"],
        },
        {
            "id": "252",
            "category": "Impact",
            "statement": (
                r"Determine the value of the coefficient of restitution $e$"
                r" which results in the final velocity $v'$ being perpendicular"
                r" to the initial velocity $v$. The initial velocity $v$ makes an"
                r" angle of 60° with the wall as shown."
            ),
            "targets": {"e": 0.333},
            "required_units": ["unitless"],
        },
        {
            "id": "K_2.6_1",
            "category": "Rigid Body Kinematics (Rotation)",
            "statement": (
                r"For the instant represented, point $B$ crosses the horizontal"
                r" axis through point $O$ with a downward velocity $v = 0.6$"
                r" m/s. Determine the corresponding value of the angular"
                r" velocity $\omega_{OA}$ of link $OA$. Length $OA = 130$ mm,"
                r" length $AB = 90$ mm, horizontal distance $OB = 180$ mm."
            ),
            "targets": {"omega_OA": 10.0},
            "required_units": ["rad/s"],
        },
        {
            "id": "K_2.6_2",
            "category": "Rigid Body Kinematics (Rotation)",
            "statement": (
                r"The mass center $G$ of the car has a velocity of $40$ mi/hr at"
                r" position $A$ and $1.52$ seconds later at $B$ has a velocity"
                r" of $50$ mi/hr. The radius of curvature of the road at $B$ is"
                r" $180$ ft. Calculate the angular velocity $\omega$ of the"
                r" car at $B$ and the average angular velocity $\omega_{av}$ of"
                r" the car between $A$ and $B$. Initial angle is $30^{\circ}$"
                r" from vertical at $A$."
            ),
            "targets": {"omega_B": 0.407, "omega_av": 0.344},
            "required_units": ["rad/sec"],
        },
        {
            "id": "K_2.6_3",
            "category": "Rigid Body Kinematics (Rotation)",
            "statement": (
                r"The rotating arm starts from rest and acquires a rotational"
                r" speed $N = 600$ rev/min in $2$ seconds with constant angular"
                r" acceleration. Find the time $t$ after starting before the"
                r" acceleration vector of end $P$ (at radius $6''$) makes an"
                r" angle of $45^{\circ}$ with the arm $OP$."
            ),
            "targets": {"t": 0.1784},
            "required_units": ["s"],
        },
    ]

    try:
        if os.path.exists("problems_v2_GitHub.json"):
            with open("problems_v2_GitHub.json", "r") as f:
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
    """숫자를 추출하여 정답과 5% 오차 범위 내에 있는지 확인합니다."""
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
    """Extracts title and subtitle for the bottom UI line."""
    title = prob.get("hw_title")
    subtitle = prob.get("hw_subtitle")
    if title and subtitle:
        return f"{title} ({subtitle})"
    return prob.get("category", "Engineering Practice")


def evaluate_understanding_score(chat_history):
    """대화 내용을 바탕으로 이해도를 0-10점으로 평가합니다."""
    if not chat_history or len(str(chat_history).strip()) == 0:
        return 0

    eval_instruction = (
        "You are a strict Engineering Professor at Texas A&M University -"
        " Corpus Christi. Evaluate the student's level of physical and"
        " mathematical understanding (0-10) based ONLY on the chat"
        " history.\n\nSINGLE-PROBLEM EVALUATION DIRECTIVES:\n1. This session"
        " evaluates ONLY ONE single assigned problem. Do NOT penalize for"
        " coverage, unmentioned topics, unaddressed syllabus modules, or"
        " leaving the chat after solving the problem.\n2. Focus strictly on"
        " student responses, mathematical accuracy, and reasoning quality for"
        " the active problem in the transcript.\n3. Do NOT penalize the score"
        " for external system states, missing database flags, or platform"
        " logging errors.\n4. Reward active learning: If a student makes an"
        " initial error but self-corrects after a Socratic hint, score them"
        " generously for concept recovery.\n\nSTRICT SCORING RUBRIC:\n0: No"
        " participation, empty session, or complete lack of attempt.\n1-3:"
        " Minimal participation, persistent off-topic responses, or failure"
        " to engage with hints.\n4-5: Good engagement, but relies heavily on"
        " tutor step-by-step guidance without applying correct governing"
        " equations independently.\n6-7: Successfully solves the problem with"
        " minor initial setup errors that were quickly self-corrected after a"
        " hint.\n8-9: Strong mastery, proper LaTeX/governing equations,"
        " correct final numeric execution with minimal guidance.\n10: Complete"
        " mastery, flawless physics logic, independent derivation, and"
        " pristine mathematical rigor for the single problem.\n\nOutput ONLY the"
        " integer score."
    )

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
    """세션을 분석하여 이메일 리포트를 전송합니다."""
    score = evaluate_understanding_score(chat_history)

    report_instruction = (
        "You are an expert Engineering Education Evaluator for Dr. Dugan Um at"
        " TAMUCC. Analyze the session data and generate a professional mastery"
        " report using Markdown.\n\nSTRICT EVALUATION & FORMATTING RULES:\n1."
        " THIS EVALUATION IS EXCLUSIVELY FOR A SINGLE PROBLEM SESSION. Do NOT"
        " dock points or mention 'Coverage (0/5)', 'incomplete topics', or"
        " 'unaddressed assigned topics'.\n2. DO NOT use LaTeX document wrappers"
        " like \\documentclass or \\begin{document}.\n3. Use standard Markdown"
        " headers (##, ###) and bold text (**).\n4. Use LaTeX ONLY for"
        " individual formulas (e.g., $F=ma$).\n5. REQUIRED SECTIONS: ##"
        " Overview, ## Score, ## Mathematical Rigor, ## Concept Mastery, ##"
        " Engagement, ## Recommendations.\n6. Base the score justification"
        " exclusively on student physics logic and chat interaction for the"
        " single problem. Do NOT reference system/database flags or missing"
        " modules."
    )

    model = get_gemini_model(report_instruction)
    if not model:
        return "AI Analysis Unavailable"

    prompt = (
        f"Student Name: {user_name}\n"
        f"Assigned Single Problem: {topic_title}\n"
        f"Assigned Score: {score}/10\n\n"
        f"SESSION CHAT HISTORY:\n{chat_history}\n\n"
        "Write the evaluation in Markdown for a clean web display."
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

```
