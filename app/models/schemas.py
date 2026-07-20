from pydantic import BaseModel
from typing import Optional

class FarmerInput(BaseModel):
    location: str
    farm_size: str
    season: str
    previous_crop: Optional[str] = None
    desired_crop: str          # the crop the farmer wants to grow