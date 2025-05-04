from textwrap import dedent
from wsgiref.util import request_uri

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.file import FileTools
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

from app.settings import settings


class KeyFinding(BaseModel):
    category: str = Field(..., description="Key finding categorisation")
    description: str = Field(..., description="Key finding description")


class Interview(BaseModel):
    client_name: str = Field(..., description="Client name")
    summary: str = Field(..., description="Summary of the interview")
    findings: list[KeyFinding] = Field(
        ..., description="Key findings from the interview"
    )


class Interviews(BaseModel):
    interviews: list[Interview] = Field(
        ..., description="List of interviews with key findings"
    )


class Feature(BaseModel):
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")
    business_area: str = Field(..., description="Business area of the feature")
    client_name: str = Field(..., description="Client name interested in the feature")


class FeatureResearch(BaseModel):
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")
    business_area: str = Field(..., description="Business area of the feature")
    client_name: str = Field(..., description="Client name interested in the feature")
    priority: int = Field(..., description="Feature priority (Low/Medium/High)")
    complexity: int = Field(..., description="Feature complexity (Low/Medium/High)")
    market_analysis: str = Field(..., description="Market analysis of the feature")
    competitors: list[str] = Field(..., description="Competitors of the feature")


class Features(BaseModel):
    features: list[Feature] = Field(
        ..., description="List of features proposed based on the interviews"
    )


class FeatureProposals(BaseModel):
    features: list[Feature] = Field(
        ..., description="List of proposed features based on the interviews"
    )
    conclusion: str = Field(
        ...,
        description="Conclusion and next steps based on the feature proposals. Suggest any other areas to explore, if any.",
    )


@dataclass
class InsightAgent:
    openai_api_key: str

    def get_interview_agent(self) -> Agent:
        return Agent(
            name="Interview_Agent",
            model=OpenAIChat(id="gpt-4o-mini", api_key=self.openai_api_key),
            tools=[
                FileTools(base_dir=settings.project_root / "data", save_files=False)
            ],
            show_tool_calls=True,
            debug_mode=True,
            role="Product owner assistant",
            description="You are a product owner assistant. Your job is to help the product owner to carefully summarize the interview transcripts and summarize the key findings.",
            instructions=dedent(
                """                               
                The interview transcripts are int the form of text files which you can read with the FileTools.
                Each file contains a single interview with a client. When reading the file, you should use only
                the filename without the path.
                
                Do not discard too much information, but also do not include too much information.
                
                Include the client_name of the interview in the summary.
                
                Translate everything to english.
                """
            ),
            response_model=Interviews,
        )

    def get_feature_proposal_agent(self) -> Agent:
        return Agent(
            name="Feature_Agent",
            model=OpenAIChat(id="gpt-4o-mini", api_key=self.openai_api_key),
            show_tool_calls=True,
            debug_mode=True,
            role="Product owner",
            instructions=dedent(
                f"""               
                Use only the finding from the Interview_Agent. Do not add additional data.                
                """
            ),
            description=(
                "You are a product owner for an AI application. "
                "You are given the key findings from the client interviews. "
                "Your job is to propose a list of LLM-enabled or AI-enabled features to develop based on the key findings. "
                "In the output, include in the client_name, which the clients might be interested in the proposed features (can be more than one). "
            ),
            response_model=Features,
        )

    def get_research_agent(self) -> Agent:
        return Agent(
            name="Research_Agent",
            model=OpenAIChat(id="gpt-4o-mini", api_key=self.openai_api_key),
            show_tool_calls=True,
            debug_mode=True,
            role="Product Researcher",
            instructions=[
                "Research the competitiveness of the proposed features, and summarize the results. ",
                "Analyse the supply and demand for the proposed features",
                "For each feature, include the client_name for which it may be interesting.",
                "Use the tool to research the competitors, supply and demand analysis for the feature.",
            ],
            description="You are a fact-based market researcher for a AI product.",
            tools=[DuckDuckGoTools(), Newspaper4kTools()],
            response_model=FeatureResearch,
        )

    def make_feature_proposal(self):
        summary_agent = self.get_interview_agent()
        feature_agent = self.get_feature_proposal_agent()
        research_agent = self.get_research_agent()

        planning_agent = Team(
            name="Product Owner Team",
            mode="coordinate",
            model=OpenAIChat(id="gpt-4o-mini", api_key=self.openai_api_key),
            members=[summary_agent, feature_agent, research_agent],
            description=(
                "You are a product owner manager. "
                "You are building a AI-enabled SaaS. ",
                "Given the interview transcripts, your job is to propose a list of LLM-enabled features to be implemented in the product based on the key findings.",
            ),
            success_criteria="Proposed features generated by the Feature_Agent.",
            instructions=[
                "First, ask the Interview_Agent to get and summarize the interview transcripts",
                "Then ask the Feature_Agent to propose a list of LLM-enabled features to be implemented in the product based on the summary provided by Interview_Agent.",
                "Finally, ask the Research_Agent to research the competitiveness of the proposed features, and summarize the results.",
                "In the output, The client_name is the client for which we can propose to the clients in the interview transcripts.",
                "Call each agent only once, in the order specified.",
            ],
            add_datetime_to_instructions=True,
            add_member_tools_to_system_message=False,
            enable_agentic_context=True,
            share_member_interactions=False,
            show_members_responses=True,
            response_model=FeatureProposals,
            debug_mode=True,
        )

        response = planning_agent.run("Do a feature research and make a proposal.")

        return response.content, response.metrics
