from pydantic import BaseModel
from typing import Optional
from typing import List


class Job(BaseModel):
    title: str
    url: str
    description: str
    job_type: str
    time_posted: str
    tier: str
    est_time: Optional[str] = None
    budget: Optional[str] = None
    skills: List[str]
    client_country: str
    client_rating: float
    payment_verified: bool
    client_spending: str
    proposals: str
