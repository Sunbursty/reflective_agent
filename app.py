import streamlit as st
import requests

# BACKEND_URL = "http://localhost:8000"
BACKEND_URL = "http://127.0.0.1:8000"

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
        "progress_label": "Reflection Progress",
        "stages": [
            "Meaningful Experience",
            "Specific Actions",
            "Transferable Skills",
            "Motivation",
            "Strengths & Weaknesses",
            "Career Direction",
        ],
        "reset_btn": "Reset Conversation",
        "chat_placeholder": "Type your response here...",
        "summary_btn": "Generate Reflection Summary",
        "summary_title": "Career Reflection Summary",
        "download_btn": "Download Summary (.txt)",
        "initial_message": (
            "Hi! To start, could you tell me about one career-related "
            "experience that felt meaningful to you?"
        ),
        "error_connection": "Cannot connect to backend. Make sure the FastAPI server is running on port 8000.",
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
        "progress_label": "反思进度",
        "stages": [
            "有意义的经历",
            "具体行动",
            "可迁移技能",
            "动机",
            "优势与不足",
            "职业方向",
        ],
        "reset_btn": "重置对话",
        "chat_placeholder": "在此输入你的回答...",
        "summary_btn": "生成反思总结",
        "summary_title": "职业反思总结",
        "download_btn": "下载总结（.txt）",
        "initial_message": "你好！首先，能告诉我一个对你来说有意义的职业相关经历吗？",
        "error_connection": "无法连接后端服务，请确保 FastAPI 服务正在端口 8000 运行。",
        "error_request": "请求失败：{}",
        "error_summary": "生成总结失败：{}",
        "language_label": "语言",
    },
}

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

    st.markdown(f"**{T['progress_label']}**")
    user_msg_count = sum(
        1 for m in st.session_state.get("messages", []) if m["role"] == "user"
    )
    stages = T["stages"]
    current_stage_idx = min(user_msg_count // 2, len(stages) - 1)
    for i, stage_name in enumerate(stages):
        if i < current_stage_idx:
            icon = "✅"
            label = stage_name
        elif i == current_stage_idx:
            icon = "▶"
            label = f"**{stage_name}**"
        else:
            icon = "○"
            label = stage_name
        st.markdown(f"{icon} {label}")

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

# When language switches, update the initial greeting if it's still the only message
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
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "messages": st.session_state.messages,
                "career_interest": career_interest,
                "reflection_style": reflection_style,
                "personality": personality,
                "lang": lang,
            },
            timeout=30,
        )
        response.raise_for_status()
        reply = response.json()["reply"]
    except requests.exceptions.ConnectionError:
        st.error(T["error_connection"])
        st.stop()
    except requests.exceptions.RequestException as e:
        st.error(T["error_request"].format(e))
        st.stop()

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)

    st.rerun()

st.divider()

if st.button(T["summary_btn"], key="summary_btn"):
    try:
        response = requests.post(
            f"{BACKEND_URL}/summary",
            json={
                "messages": st.session_state.messages,
                "career_interest": career_interest,
                "reflection_style": reflection_style,
                "personality": personality,
                "lang": lang,
            },
            timeout=60,
        )
        response.raise_for_status()
        st.session_state.summary_text = response.json()["summary"]
    except requests.exceptions.ConnectionError:
        st.error(T["error_connection"])
    except requests.exceptions.RequestException as e:
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
