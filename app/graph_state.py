from typing import TypedDict, Optional

class AgentState(TypedDict):
    """
    This is the shared state that flows through the LangGraph pipeline.
    Each node (agent) reads what it needs from this state and adds its
    own output back into it before passing it to the next node.
    """
    location: str
    farm_size: str
    season: str
    previous_crop: Optional[str]
    desired_crop: str
    farm_profile: Optional[dict]
    weather_insights: Optional[dict]
    final_recommendation: Optional[dict]