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


class Address(BaseModel):
    line1: str
    line2: Optional[str]
    city: str
    state: Optional[str]
    postal_code: Optional[str]
    country: str


class Profile(BaseModel):
    id: str
    account: str
    employer: Optional[str]
    created_at: str
    updated_at: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone_number: str
    birth_date: Optional[str]
    picture_url: str
    address: Address
    ssn: Optional[int]
    marital_status: Optional[str]
    gender: Optional[str]
    metadata: dict = {}
