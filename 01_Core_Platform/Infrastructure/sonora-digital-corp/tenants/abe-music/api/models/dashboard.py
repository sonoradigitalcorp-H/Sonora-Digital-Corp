from pydantic import BaseModel

class DashboardResponse(BaseModel):
    total_streams: int
    revenue: float
    campaigns: int
    engagement: float
