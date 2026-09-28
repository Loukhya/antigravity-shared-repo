"""
JobShield AI - Take-Home Task Fairness Judgment
Narrow LLM call to judge whether an assignment constitutes free production labor or a legitimate interview exercise.
"""

import json
from shared.schemas import TaskFairnessAssessment
from .llm_client import call_llm

TASK_JUDGE_PROMPT = """Analyze this interview take-home task for exploitation:
Determine:
1. "is_excessive": boolean (True if >15 hours or asking candidate to write production features for their product)
2. "is_proprietary_feature": boolean (True if asking to build actual company product code rather than generic/toy architecture)
3. "estimated_hours": integer or null
4. "rationale": one concise sentence summarizing your evaluation

Output ONLY valid JSON.

Task description:
\"\"\"{text}\"\"\"
"""

async def judge_task_fairness_llm(text: str, current_assessment: TaskFairnessAssessment) -> TaskFairnessAssessment:
    """Invokes LLM to assess task fairness if a task is detected."""
    if not current_assessment.has_task:
        return current_assessment

    prompt = TASK_JUDGE_PROMPT.format(text=text[:3000])
    response = await call_llm(prompt)
    if not response:
        return current_assessment

    try:
        clean = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(clean)
        current_assessment.is_excessive = data.get("is_excessive", current_assessment.is_excessive)
        current_assessment.is_proprietary_feature = data.get("is_proprietary_feature", current_assessment.is_proprietary_feature)
        if data.get("estimated_hours"):
            current_assessment.estimated_hours = data["estimated_hours"]
        if data.get("rationale"):
            current_assessment.rationale = data["rationale"]
    except Exception:
        pass

    return current_assessment
