# Personalized Career Reflection Agent

## Overview

This project presents a **theory-driven, personalized reflection agent** designed to support career self-exploration through **adaptive multi-turn dialogue**.

Unlike traditional career recommendation systems, this agent does not directly suggest jobs. Instead, it guides users to reflect on their **past experiences, transferable skills, motivations, strengths, and career directions**, helping them build deeper self-understanding.

The system is implemented as a **prompt-driven reflective system**, where the dialogue logic, adaptive questioning strategy, and theoretical frameworks are embedded within the system prompt.

---

## Key Features

### 1. Personalized Reflection
The agent adapts its questions based on:
- Career interests
- Reflection style (structured / open-ended / guided)
- Personality traits

---

### 2. Multi-turn Adaptive Dialogue
- Asks one question at a time
- Dynamically adjusts follow-up questions based on user responses
- Encourages deeper reflection rather than shallow answers

---

### 3. Theory-driven Design
The system is grounded in:

- Career Construction Theory → experience narration & identity building  
- Self-Determination Theory → motivation analysis (autonomy, competence, relatedness)  
- Emotional awareness → detecting uncertainty, stress, and confusion  

---

### 4. Structured Reflection Summary
After the conversation, the system generates a structured report including:
- Career interests
- Meaningful experiences
- Transferable skills
- Motivation patterns
- Strengths and weaknesses
- Potential career directions
- Suggested next steps

---

## System Architecture

This project uses a **prompt-driven architecture**:


- Frontend: Streamlit  
- LLM API: OpenRouter (LLaMA 3.1)  
- Logic Layer: Prompt-driven reflection system  

---
