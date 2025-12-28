"""Organization schemas."""

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class OrganizationOut(BaseModel):
    """Organization response schema."""

    id: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationWithRole(BaseModel):
    """Organization with user's role."""

    id: str
    name: str
    role: str
    location_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrgMeResponse(BaseModel):
    """Response for GET /org/me endpoint."""

    organization: OrganizationOut
    role: str
    location_id: str | None
    location_name: str | None = None


# Branding schemas
class BrandingOut(BaseModel):
    """Branding settings for an organization."""

    brand_name: str | None = None
    brand_logo_url: str | None = None
    brand_primary_color: str | None = None

    model_config = {"from_attributes": True}


class BrandingUpdate(BaseModel):
    """Update branding settings."""

    brand_name: str | None = Field(default=None, max_length=100)
    brand_logo_url: str | None = Field(default=None, max_length=500)
    brand_primary_color: str | None = Field(default=None, max_length=7)

    @field_validator("brand_logo_url")
    @classmethod
    def validate_logo_url(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not v.startswith(("http://", "https://")):
                raise ValueError("La URL del logo debe empezar con http:// o https://")
        return v

    @field_validator("brand_primary_color")
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
                raise ValueError("El color debe ser un HEX válido (#RRGGBB)")
        return v


class LocationBrandingOut(BaseModel):
    """Branding overrides for a location."""

    location_id: str
    location_name: str
    brand_name_override: str | None = None
    brand_logo_url_override: str | None = None
    brand_primary_color_override: str | None = None

    model_config = {"from_attributes": True}


class LocationBrandingUpdate(BaseModel):
    """Update location branding overrides."""

    brand_name_override: str | None = Field(default=None, max_length=100)
    brand_logo_url_override: str | None = Field(default=None, max_length=500)
    brand_primary_color_override: str | None = Field(default=None, max_length=7)

    @field_validator("brand_logo_url_override")
    @classmethod
    def validate_logo_url(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not v.startswith(("http://", "https://")):
                raise ValueError("La URL del logo debe empezar con http:// o https://")
        return v

    @field_validator("brand_primary_color_override")
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
                raise ValueError("El color debe ser un HEX válido (#RRGGBB)")
        return v


# Onboarding schemas
class OnboardingStatusOut(BaseModel):
    """Onboarding status response."""

    onboarding_step: int
    onboarding_completed_at: datetime | None = None
    has_location: bool
    has_statuses: bool
    has_services: bool
    has_branding: bool


class OnboardingStepUpdate(BaseModel):
    """Update onboarding step."""

    onboarding_step: int = Field(..., ge=0, le=5)
