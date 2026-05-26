from pydantic import BaseModel, Field
from typing import List

class InterviewAnalysis(BaseModel):
    communication_score: float = Field(description="Score from 0.0 to 1.0 rating how clearly the candidate communicates their ideas. Judge on whether answers are coherent, well-structured, and easy to follow. A score of 1.0 is achievable for any candidate whose ideas come across clearly.")
    engagement_score: float = Field(description="Score from 0.0 to 1.0 rating how interested the candidate appears in this specific role. Judge on whether they asked thoughtful questions, referenced specific aspects of the role or company, and gave answers tailored to this position rather than generic responses. A score of 1.0 is achievable for any candidate who demonstrates genuine interest through the substance of what they said.")
    specificity_score: float = Field(description="Score from 0.0 to 1.0 rating use of concrete examples from past experience. A score of 1.0 is achievable when the candidate provides specific examples that directly relate to the role.")
    highlights: List[str] = Field(description="List of strong moments or impressive answers that demonstrate fit for the role")
    concerns: List[str] = Field(description="List of areas of concern or weak answers that raise doubts about the candidate's fit")
    red_flags: List[str] = Field(description="List of serious issues that may disqualify the candidate from the role")
    recommendation: str = Field(description="Overall hiring recommendation: 'Strong Yes', 'Yes', 'Maybe', 'No', or 'Strong No'")
    summary: str = Field(description="2-3 sentence overall summary of the candidate's fit for the role")
    score_breakdown: str = Field(description="Explanation of what drove each score up or down. For each score, briefly note the specific moments or answers that influenced it.")
