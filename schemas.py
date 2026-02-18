from pydantic import BaseModel, Field
import json
from typing import Any, Literal

class ExecutiveSnapshot(BaseModel):
    meeting_purpose: str = Field(...,
        description="What was the purpose of this meeting?"
    )
    overall_outcome: str = Field(...,
        description="Detail the overall outcome of the meeting, and whether it was productive / stalled / exploratory / unresolved."
    )
    major_decisions: list = Field(...,
        description="List the major decisions made in the meeting."
    )
    key_risks_and_tensions: list = Field(...,
        description="What key risks or tensions were identified in the meeting?"
    )
    immediate_next_steps: list = Field(...,
        description="What are some steps that should be taken immediately next?"
    )

json_schema: dict[str, Any] = ExecutiveSnapshot.model_json_schema()
#print(json.dumps(json_schema, indent=2))