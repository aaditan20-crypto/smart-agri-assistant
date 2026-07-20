import json
from app.utils.llm_client import ask_gemini
from app.models.schemas import FarmerInput

SYSTEM_PROMPT = """You are a Farm Intelligence Agent in an agricultural AI system.
Your job is to infer soil and farm characteristics from simple, non-technical
information a farmer provides — never ask for pH, Nitrogen, Phosphorus, or Potassium values.

Given the farmer's location, farm size, season, and previous crop, infer:
1. Probable soil type for that region (e.g. Red soil, Black/Cotton soil, Alluvial, Laterite, Sandy, Clay)
2. Estimated soil moisture level (Low / Medium / High) based on season and region climate
3. Estimated nutrient status (Low / Medium / High) based on what the previous crop typically depletes
4. 3-5 suitable crop categories for this farm profile (e.g. "cereals", "pulses", "oilseeds", "vegetables")

Respond ONLY with valid JSON in this exact format, no other text:
{
  "soil_type": "...",
  "estimated_soil_moisture": "...",
  "estimated_nutrient_status": "...",
  "suitable_crop_categories": ["...", "..."],
  "reasoning": "one short paragraph explaining your inference"
}
"""

class FarmIntelligenceAgent:
    def analyze(self, farmer_input: FarmerInput) -> dict:
        user_message = f"""
Location: {farmer_input.location}
Farm Size: {farmer_input.farm_size}
Season: {farmer_input.season}
Previous Crop: {farmer_input.previous_crop or "Not specified / first time farming"}
Farmer's Desired Crop: {farmer_input.desired_crop}
"""
        raw_response = ask_gemini(SYSTEM_PROMPT, user_message, agent_name="farm_intelligence")
        cleaned = raw_response.strip().replace("```json", "").replace("```", "").strip()

        try:
            farm_profile = json.loads(cleaned)
        except json.JSONDecodeError:
            farm_profile = {
                "soil_type": "Unknown",
                "estimated_soil_moisture": "Unknown",
                "estimated_nutrient_status": "Unknown",
                "suitable_crop_categories": [],
                "reasoning": raw_response
            }

        farm_profile["previous_crop"] = farmer_input.previous_crop
        return farm_profile

farm_intelligence_agent = FarmIntelligenceAgent()