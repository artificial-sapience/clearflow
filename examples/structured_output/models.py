"""Type definitions for structured output example."""

from typing import TypedDict

from pydantic import BaseModel, ConfigDict, Field


def _empty_work_tuple() -> tuple["WorkExperience", ...]:
    """Factory function for empty work experience tuple."""
    return ()


def _empty_education_tuple() -> tuple["Education", ...]:
    """Factory function for empty education tuple."""
    return ()


def _empty_skills_tuple() -> tuple[str, ...]:
    """Factory function for empty skills tuple."""
    return ()


class WorkExperience(BaseModel):
    """A single work experience entry."""

    model_config = ConfigDict(frozen=True)

    company: str = Field(description="Company name")
    role: str = Field(description="Job title/role")
    duration: str = Field(description="Employment period (e.g., 'Jan 2020 - Dec 2022')")
    description: str = Field(
        default="", description="Brief description of responsibilities"
    )


class Education(BaseModel):
    """Education entry."""

    model_config = ConfigDict(frozen=True)

    institution: str = Field(description="School/University name")
    degree: str = Field(description="Degree or certification")
    year: str = Field(description="Graduation year or period")


class ExtractedResume(BaseModel):
    """Structured resume data extracted from text."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Full name")
    email: str = Field(description="Email address")
    phone: str = Field(default="", description="Phone number")
    summary: str = Field(default="", description="Professional summary")
    experiences: tuple[WorkExperience, ...] = Field(
        default_factory=_empty_work_tuple, description="Work experience entries"
    )
    education: tuple[Education, ...] = Field(
        default_factory=_empty_education_tuple, description="Education entries"
    )
    skills: tuple[str, ...] = Field(
        default_factory=_empty_skills_tuple, description="List of skills"
    )


class ExtractorState(TypedDict, total=False):
    """State for the extraction flow."""

    input_text: str
    extracted_data: ExtractedResume | None
    validation_errors: tuple[str, ...]
    formatted_output: str
