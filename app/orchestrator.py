import json
from langgraph.graph import StateGraph, END
from app.graph_state import AgentState
from app.agents.farm_intelligence import farm_intelligence_agent
from app.agents.weather import weather_agent
from app.models.schemas import FarmerInput
from app.utils.llm_client import ask_gemini

SYNTHESIS_PROMPT = """You are the Master Orchestrator of an agricultural AI system.
You have received outputs from 2 specialized agents: Farm Intelligence (soil analysis)
and Weather Intelligence, for a farmer who has ALREADY CHOSEN a specific crop they want to grow.

Your job is NOT to recommend a different crop. Instead:
1. Evaluate how suitable the farmer's chosen crop is, given the soil and weather conditions
2. Flag any risks (e.g. water needs vs rainfall forecast, soil type mismatch, timing issues)
3. Give practical, actionable advice to help the farmer succeed with THEIR chosen crop

Respond ONLY with valid JSON in this exact format, no other text:
{
  "chosen_crop": "the crop name the farmer selected",
  "suitability_rating": "Poor / Fair / Good / Excellent",
  "suitability_reasoning": "why this rating, based on soil and weather",
  "risks_to_watch": ["...", "..."],
  "this_week_action_items": ["...", "...", "..."],
  "overall_recommendation": "a clear 3-4 sentence farmer-friendly final recommendation for growing this specific crop"
}
"""


# ---- Node functions: each one is a "step" in the LangGraph pipeline ----

def farm_intelligence_node(state: AgentState) -> dict:
    """Node 1: runs the Farm Intelligence Agent, returns its output to merge into state."""
    farmer_input = FarmerInput(
        location=state["location"],
        farm_size=state["farm_size"],
        season=state["season"],
        previous_crop=state.get("previous_crop"),
        desired_crop=state["desired_crop"]
    )
    farm_profile = farm_intelligence_agent.analyze(farmer_input)
    return {"farm_profile": farm_profile}


def weather_node(state: AgentState) -> dict:
    """Node 2: runs the Weather Agent, using farm_profile already in state."""
    weather_insights = weather_agent.analyze(
        state["location"], state["farm_profile"], state["season"]
    )
    return {"weather_insights": weather_insights}


def synthesis_node(state: AgentState) -> dict:
    """Node 3: combines farm_profile + weather_insights into the final recommendation."""
    combined = {
        "farm_profile": state["farm_profile"],
        "weather_insights": state["weather_insights"],
        "farmer_desired_crop": state["desired_crop"]
    }
    user_message = json.dumps(combined)
    raw_response = ask_gemini(SYNTHESIS_PROMPT, user_message, agent_name="master_orchestrator")
    cleaned = raw_response.strip().replace("```json", "").replace("```", "").strip()

    try:
        final_recommendation = json.loads(cleaned)
    except json.JSONDecodeError:
        final_recommendation = {
            "chosen_crop": state["desired_crop"],
            "suitability_rating": "Unknown",
            "suitability_reasoning": "Unknown",
            "risks_to_watch": [],
            "this_week_action_items": [],
            "overall_recommendation": raw_response
        }

    return {"final_recommendation": final_recommendation}


# ---- Build the graph: define nodes and the edges (order) between them ----

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("farm_intelligence", farm_intelligence_node)
    graph.add_node("weather", weather_node)
    graph.add_node("synthesis", synthesis_node)

    graph.set_entry_point("farm_intelligence")
    graph.add_edge("farm_intelligence", "weather")
    graph.add_edge("weather", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile()


compiled_graph = build_graph()


class MasterOrchestrator:
    def __init__(self):
        self.graph = compiled_graph

    def run(self, farmer_input: FarmerInput) -> dict:
        initial_state: AgentState = {
            "location": farmer_input.location,
            "farm_size": farmer_input.farm_size,
            "season": farmer_input.season,
            "previous_crop": farmer_input.previous_crop,
            "desired_crop": farmer_input.desired_crop,
            "farm_profile": None,
            "weather_insights": None,
            "final_recommendation": None
        }

        result_state = self.graph.invoke(initial_state)

        return {
            "status": "success",
            "farm_profile": result_state["farm_profile"],
            "weather_insights": result_state["weather_insights"],
            "final_recommendation": result_state["final_recommendation"]
        }


orchestrator = MasterOrchestrator()