from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Career Reflection Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("OPENROUTER_API_KEY"),
# )

# MODEL_NAME = "meta-llama/llama-3.1-8b-instruct"

client = OpenAI(
    base_url="https://xiaohumini.site/v1",
    api_key=os.getenv("XIAOHUMINI_API_KEY"),
)

MODEL_NAME = "llama-3.1-8b"


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    career_interest: str
    reflection_style: str
    personality: str
    lang: str = "en"


class SummaryRequest(BaseModel):
    messages: list[Message]
    career_interest: str
    reflection_style: str
    personality: str
    lang: str = "en"


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


# SUMMARY_PROMPT = """
# Please generate a structured Career Reflection Summary based on the conversation.
#
# Include:
# 1. Career Interests
# 2. Meaningful Experiences
# 3. Key Transferable Skills
# 4. Motivation Pattern
#    - Autonomy
#    - Competence
#    - Relatedness
# 5. Strengths
# 6. Areas for Improvement
# 7. Possible Career Directions
# 8. Suggested Next Actions
#
# Please make the summary specific to the user's answers.
# Avoid generic advice.
# """

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


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        system_msg = {"role": "system", "content": build_system_prompt(
            req.career_interest, req.reflection_style, req.personality, req.lang
        )}
        messages = [system_msg] + [m.model_dump() for m in req.messages]
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summary")
def summary(req: SummaryRequest):
    try:
        system_msg = {"role": "system", "content": build_system_prompt(
            req.career_interest, req.reflection_style, req.personality, req.lang
        )}
        messages = (
            [system_msg]
            + [m.model_dump() for m in req.messages]
            + [{"role": "user", "content": SUMMARY_PROMPT}]
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5,
        )
        return {"summary": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
