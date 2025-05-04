from fastapi import APIRouter
from app.agents.product_owner.insight_agent import InsightAgent

from app.settings import settings

router = APIRouter()

# TODO:
# 1. As the stub only. In actual implementation, the interview transcripts are managed
#    through its own CRUD endpoints.
# 2. The interview transcripts are stored in either database or a file system.
# 3. The tools to read the interview transcripts are implemented in the InterviewAgent and
#    are dynamically loaded when the agent is created.


@router.get("/insights")
async def insights():
    # TODO:
    # 1. If the request is part of the interruptible flow, retrieve the session ID from the request
    #    and pass it to the InsightAgent so the context from the previous calls can be used.
    # 2. Otherwise, create a new session ID and pass it to the InsightAgent. The session is stored in
    #    a database table and is associated to the organisation the user belongs to.

    # 3. Pass the OpenAI LLM model instance to the InsightAgent, which is initialised with the
    #    OpenAI API key from the settings.

    insightAgent = InsightAgent(openai_api_key=settings.openai_api_key)

    plan, metrics = insightAgent.make_feature_proposal()

    return {
        "plan": plan,
        "metrics": metrics,
    }
