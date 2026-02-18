import json

import schemas
from pydantic_ai import Agent, VideoUrl
from pydantic_ai.models.google import GoogleModel
import os


os.environ["GEMINI_API_KEY"] = "AIzaSyDPSsDdvlCCnX-0KIpvTesBljGvnPyQMT4"

agent: Agent[schemas.ExecutiveSnapshot] = Agent(
    model=GoogleModel("gemini-2.5-flash"),
    system_prompt="""
    You are generating an ExecutiveSnapshot.

    The output schema has the following fields:
    - meeting_purpose (string): why the meeting occurred
    - overall_outcome (string): whether the meeting was productive, stalled, exploratory, or unresolved
    - major_decisions (list): the key decisions made
    - key_risks_and_tensions (list): risks, concerns, or disagreements raised
    - immediate_next_steps (list): agreed follow-up actions
    
    Output ONLY a JSON object that is a valid instance of this schema, without any extra fields or commentary.
    """
)

meeting_str = """
Alex:
Alright, let’s get started. The main goal today is deciding whether we can ship the analytics dashboard in March or if we need to push. Leadership wants clarity by end of week.

Maya:
From an engineering standpoint, the core functionality is mostly done, but the data pipeline is still flaky. We could stabilize it by March, but it would require deprioritizing bug fixes for the mobile app.

Jordan:
That’s a concern. Support is already overwhelmed with mobile issues. If we pause those fixes, ticket volume will spike.

Alex:
Understood. But the dashboard is a strategic priority. We’ve already told Sales to expect it this quarter.

Sam:
Before we commit—do we know if additional infra costs are needed? If we scale usage, cloud spend could exceed the current budget.

Maya:
Yes, there will be additional costs. I don’t have an exact number yet, but it won’t be trivial.

Sam:
That’s an issue. Finance can’t approve open-ended spend.

Alex:
Okay, let’s slow down. No one is approving unlimited budget today. Maya, can you get us an estimate?

Maya:
Yes, I can run projections. I’ll have a rough estimate by Thursday.

Alex:
Good. Jordan, if we do push mobile bug fixes back two weeks, what’s the operational impact?

Jordan:
Worst case, customer satisfaction dips. Best case, we manage with temporary scripts. I don’t recommend it, but it’s survivable.

Alex:
So not ideal, but not catastrophic.

Jordan:
Correct.

Alex:
Alright. Tentatively, we’re aiming for a March release, pending cost confirmation. No final go-live decision until we see the numbers.

Sam:
To be clear, Finance approval is required before any infra expansion.

Alex:
Noted. That’s mandatory.

Maya:
One more thing—QA is already stretched. If March is the target, I’ll need two contractors.

Sam:
That definitely needs approval.

Alex:
Okay. Action items coming out of this: Maya gets cost estimates, Sam reviews budget impact, and Jordan prepares a support risk brief. We’ll reconvene Friday.

Jordan:
Friday works.

Sam:
Fine.

Alex:
Meeting adjourned.
"""

result = agent.run_sync(
    #[VideoUrl(url="https://www.youtube.com/watch?v=53yPfrqbpkE")]
    meeting_str
)

# Parse response into Pydantic model

print(result)
raw = result.output.strip("```").strip("'").replace("json\n", "", 1)
snapshot = schemas.ExecutiveSnapshot.model_validate_json(raw)

print(snapshot.model_dump_json(indent=2))