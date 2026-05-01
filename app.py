import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # local dev: reads from .env file; no-op on Streamlit Cloud

TRANSLATIONS = {
    "en": {
        "page_title": "Career Reflection Agent",
        "title": "Personalized Career Reflection Agent",
        "description": (
            "This chatbot helps you reflect on your career interests, past experiences, "
            "motivations, strengths, weaknesses, and possible career directions through "
            "adaptive multi-turn dialogue."
        ),
        "user_profile": "User Profile",
        "career_interest_label": "Career Interest",
        "career_interest_options": [
            "User Research", "Operations", "Product Management", "Consulting",
            "AI", "Computer Science", "Business Development", "Not sure",
        ],
        "reflection_style_label": "Reflection Style",
        "reflection_style_options": ["Structured", "Open-ended", "Example-guided"],
        "personality_label": "Personality Trait",
        "personality_options": ["Analytical", "Creative", "Organized", "Social", "Others"],
        "reset_btn": "Reset Conversation",
        "chat_placeholder": "Type your response here...",
        "summary_btn": "Generate Reflection Summary",
        "summary_title": "Career Reflection Summary",
        "download_btn": "Download Summary (.txt)",
        "initial_message": (
            "Hi! To start, could you tell me about one career-related "
            "experience that felt meaningful to you?"
        ),
        "error_request": "Request failed: {}",
        "error_summary": "Summary generation failed: {}",
        "language_label": "Language",
    },
    "zh": {
        "page_title": "职业反思助手",
        "title": "个性化职业反思助手",
        "description": "这个聊天机器人通过自适应的多轮对话，帮助你反思职业兴趣、过往经历、动机、优缺点和可能的职业方向。",
        "user_profile": "用户信息",
        "career_interest_label": "职业兴趣",
        "career_interest_options": [
            "用户研究", "运营", "产品管理", "咨询",
            "人工智能", "计算机科学", "商业发展", "尚不确定",
        ],
        "reflection_style_label": "反思风格",
        "reflection_style_options": ["结构化", "开放式", "示例引导"],
        "personality_label": "性格特点",
        "personality_options": ["分析型", "创造型", "组织型", "社交型", "其他"],
        "reset_btn": "重置对话",
        "chat_placeholder": "在此输入你的回答...",
        "summary_btn": "生成反思总结",
        "summary_title": "职业反思总结",
        "download_btn": "下载总结（.txt）",
        "initial_message": "你好！首先，能告诉我一个对你来说有意义的职业相关经历吗？",
        "error_request": "请求失败：{}",
        "error_summary": "生成总结失败：{}",
        "language_label": "语言",
    },
}

MODEL_NAME = "llama-3.1-8b"


def get_client():
    try:
        api_key = st.secrets.get("XIAOHUMINI_API_KEY")
    except Exception:
        api_key = None
    api_key = api_key or os.getenv("XIAOHUMINI_API_KEY") or ""
    return OpenAI(base_url="https://xiaohumini.site/v1", api_key=api_key)


def build_system_prompt(career_interest: str, reflection_style: str, personality: str, lang: str = "en") -> str:
    language_instruction = "Please respond in Chinese (中文)." if lang == "zh" else "Please respond in English."
    return f"""
    You are a Personalized Career Reflection Agent.

    {language_instruction}

    The user's profile is:
    - Career interest: {career_interest}
    - Reflection style: {reflection_style}
    - Personality trait: {personality}

    Your goal is to guide the user through a structured, adaptive, multi-turn career reflection process.

    You should NOT directly recommend jobs too early.
    Your main task is to help the user reflect on past experiences, transferable skills, motivations, strengths, weaknesses, and possible career directions.

    The reflection should be theory-driven:
    - Career Construction Theory: help the user narrate meaningful experiences and connect them to career identity.
    - Self-Determination Theory: explore motivation through autonomy, competence, and relatedness.
    - Emotional awareness: notice uncertainty, stress, or confusion and respond supportively.

    Conversation rules:
    - Ask ONLY ONE question at a time.
    - Always base your next question on the user's previous answer.
    - Do NOT ask a list of questions.
    - Do NOT jump to career recommendations too early.
    - Keep your tone natural, supportive, and conversational.
    - Keep each response concise, around 2-5 sentences.

    Adaptive questioning rules:
    - If the user's answer is vague, ask for a specific example.
    - If the user describes an experience, ask what they specifically did.
    - If the user describes actions, ask what skills those actions reflect.
    - If the user describes skills, ask why those skills matter to their career interests.
    - If the user mentions motivation, explore autonomy, competence, or relatedness.
    - If the user mentions stress, confusion, or uncertainty, ask about coping strategies or support needs.
    - If the user gives a deep answer, briefly synthesize it and move one step forward.

    Adapt to the user's reflection style:
    - If Structured: ask clear, step-by-step questions.
    - If Open-ended: ask broader exploratory questions.
    - If Example-guided: provide a short example before asking the question.

    Adapt to the user's personality trait:
    - If Analytical: focus on logic, evidence, skills, and patterns.
    - If Creative: focus on meaning, imagination, values, and future possibilities.
    - If Organized: focus on goals, planning, progress, and next steps.
    - If Social: focus on collaboration, communication, people, and relationships.
    - If Others: use a balanced and supportive style.

    Conversation stages:
    1. Meaningful experience
    2. Specific actions
    3. Transferable skills
    4. Motivation
    5. Strengths and weaknesses
    6. Possible career direction

    Do not explicitly mention these stages to the user.
    Only move forward when enough information is collected.

    Start by asking the user to describe one meaningful career-related experience.
    """


SUMMARY_PROMPT = """
Based on the conversation, generate an insightful Career Reflection Summary.
Your goal is NOT to simply repeat what the user said — it is to surface patterns,
tensions, and implications that the user may not have explicitly articulated.

The conversation followed a structured reflection framework with six stages:
Stage 1 — Meaningful Experience: What experience felt significant to the user?
Stage 2 — Specific Actions: What did they concretely do in that experience?
Stage 3 — Transferable Skills: What skills did those actions demonstrate?
Stage 4 — Motivation: What drives them (autonomy, competence, relatedness)?
Stage 5 — Strengths & Weaknesses: What do they do well, and where do they struggle?
Stage 6 — Career Direction: What career paths align with their profile?

Structure your summary to reflect this framework:

1. Reflection Journey Overview
   Briefly trace how the conversation unfolded across the six stages.
   Note which stages produced rich insights and which felt underdeveloped.

2. Core Identity Thread
   Identify the underlying theme that connects the user's experiences, skills, and motivations.
   What does this pattern reveal about who they are as a professional?

3. Key Transferable Skills (with evidence)
   List 3–5 skills, each tied to a specific moment or example from the conversation.
   Avoid generic labels — describe how the skill manifested.

4. Motivation Analysis
   - What drives them intrinsically (autonomy, mastery, purpose)?
   - Are there any tensions between what they enjoy and what they think they "should" pursue?

5. Hidden Strengths & Blind Spots
   - What strengths did the user downplay or not fully recognize?
   - What recurring challenges or avoidance patterns emerged?

6. Career Direction Fit (ranked)
   Suggest 2–3 specific career directions that align with their profile.
   For each: explain WHY it fits based on their specific answers, and what the tradeoff is.

7. Concrete Next Steps (personalized)
   Give 3 specific, actionable steps the user can take in the next 1–4 weeks.
   Ground each step in something they actually said — no generic advice.

8. One Reframe
   Offer one perspective shift — something the user might be underestimating about themselves
   or a limiting belief that came through in the conversation.

Be direct, specific, and insightful. Prioritize depth over completeness.
"""

# Language selector — must come before everything else so T is defined
lang = st.sidebar.selectbox(
    "Language / 语言",
    options=["en", "zh"],
    format_func=lambda x: "English" if x == "en" else "中文",
    key="lang",
)
T = TRANSLATIONS[lang]

st.set_page_config(page_title=T["page_title"], page_icon="💬")

st.title(T["title"])
st.write(T["description"])

with st.sidebar:
    st.header(T["user_profile"])

    career_interest = st.selectbox(
        T["career_interest_label"],
        T["career_interest_options"],
        key="career_interest",
    )

    reflection_style = st.selectbox(
        T["reflection_style_label"],
        T["reflection_style_options"],
        key="reflection_style",
    )

    personality = st.selectbox(
        T["personality_label"],
        T["personality_options"],
        key="personality",
    )

    st.divider()

    if st.button(T["reset_btn"]):
        st.session_state.messages = [
            {"role": "assistant", "content": T["initial_message"]}
        ]
        if "summary_text" in st.session_state:
            del st.session_state.summary_text
        st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": T["initial_message"]}
    ]
    st.session_state._last_lang = lang

if st.session_state.get("_last_lang") != lang:
    if len(st.session_state.messages) == 1:
        st.session_state.messages = [
            {"role": "assistant", "content": T["initial_message"]}
        ]
    st.session_state._last_lang = lang

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input(T["chat_placeholder"])

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    try:
        client = get_client()
        system_msg = {"role": "system", "content": build_system_prompt(
            career_interest, reflection_style, personality, lang
        )}
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[system_msg] + st.session_state.messages,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        st.error(T["error_request"].format(e))
        st.stop()

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)

    st.rerun()

st.divider()

if st.button(T["summary_btn"], key="summary_btn"):
    try:
        client = get_client()
        system_msg = {"role": "system", "content": build_system_prompt(
            career_interest, reflection_style, personality, lang
        )}
        messages = (
            [system_msg]
            + st.session_state.messages
            + [{"role": "user", "content": SUMMARY_PROMPT}]
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5,
        )
        st.session_state.summary_text = response.choices[0].message.content
    except Exception as e:
        st.error(T["error_summary"].format(e))

if "summary_text" in st.session_state:
    st.subheader(T["summary_title"])
    st.write(st.session_state.summary_text)
    st.download_button(
        label=T["download_btn"],
        data=st.session_state.summary_text,
        file_name="career_reflection_summary.txt",
        mime="text/plain",
        key="download_summary_btn",
    )
