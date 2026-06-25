"""Schemas del wizard de onboarding (pasos 1–7 y respuestas)."""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from Application.schemas_restaurant_profile import RestaurantMeResponse

PlanType = Literal["starter", "pro", "elite"]
BillingCycle = Literal["monthly", "annual"]


class Step1BasicInfo(BaseModel):
    restaurant_name: str = Field(..., min_length=1)
    legal_name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    social_links: Dict[str, Any] = Field(default_factory=dict)
    restaurant_type: Optional[str] = None


class Step2Location(BaseModel):
    country: Optional[str] = None
    department: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    google_maps: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class Step3Contact(BaseModel):
    owner_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class Step4Operations(BaseModel):
    opening_hours: Optional[time] = None
    closing_hours: Optional[time] = None
    seating_capacity: Optional[int] = Field(None, ge=0)
    number_tables: Optional[int] = Field(None, ge=0)


class Step5Features(BaseModel):
    reservation_types: List[str] = Field(default_factory=list)
    cuisine_types: List[str] = Field(default_factory=list)
    services_offered: List[str] = Field(default_factory=list)


class Step6Files(BaseModel):
    logo_key: Optional[str] = None
    cover_image_keys: List[str] = Field(default_factory=list)
    document_keys: List[str] = Field(default_factory=list)


class Step7Plan(BaseModel):
    plan: PlanType
    billing_cycle: BillingCycle


StepBody = Union[
    Step1BasicInfo,
    Step2Location,
    Step3Contact,
    Step4Operations,
    Step5Features,
    Step6Files,
    Step7Plan,
]

STEP_MODELS: dict[int, type[BaseModel]] = {
    1: Step1BasicInfo,
    2: Step2Location,
    3: Step3Contact,
    4: Step4Operations,
    5: Step5Features,
    6: Step6Files,
    7: Step7Plan,
}


class OnboardingStartResponse(BaseModel):
    restaurant_id: str
    status: Literal["draft"] = "draft"


class OnboardingStatusResponse(BaseModel):
    restaurant_id: str
    step: int
    status: str
    pct: int
    submitted_at: Optional[datetime] = None


class OnboardingStepResponse(BaseModel):
    restaurant_id: str
    step: int
    status: str
    pct: int


FullOnboardingDataResponse = RestaurantMeResponse
