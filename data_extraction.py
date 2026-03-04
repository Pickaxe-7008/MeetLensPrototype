import json
import os
from fpdf import FPDF
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

os.environ["GEMINI_API_KEY"] = ""

def text_to_pdf(texts, filename):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for text in texts:
        pdf.add_page()
        pdf.multi_cell(0, 10, txt=text)
    pdf.output(filename)

def clean_json(json_string):
    return json_string.strip("```").replace("json\n", "", 1)

def chunk_transcript(transcript, char_limit=6000, overlap=500):
    chunks = []
    start = 0
    length = len(transcript)

    while start < length:
        end = start + char_limit
        chunk = transcript[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks



UnifiedAgent = Agent(
    model=GoogleModel("gemini-2.5-flash"),
    system_prompt="""You are an executive meeting intelligence extraction system.

Your task is to transform a raw meeting transcript into a SINGLE, STRUCTURED, GOVERNANCE-READY JSON report.

You must distinguish clearly between:
- discussion vs commitment
- tentative vs final decisions
- instructions vs execution
- single-owner accountability vs shared participation

You are NOT a note-taker.
You are a decision, risk, and accountability analyst.

Extract ALL sections below in ONE response.
Output MUST be valid JSON that STRICTLY matches the schema.
NO commentary. NO extra fields. NO prose outside defined fields.

1. Executive Snapshot
executive_snapshot:
- meeting_purpose: string
- overall_outcome: string ["productive","stalled","exploratory","unresolved"]
- major_decisions: list[string]
- key_risks_and_tensions: list[string]
- immediate_next_steps: list[string]

2. Agreements
agreements: list[object]
- agreement_description: string
- agreement_type: string ["strategic","operational","resource"]
- participants_involved: list[string]
- scope_and_conditions: string
- final_or_conditional: string ["final","conditional"]

3. Disagreements
disagreements: list[object]
- core_issue: string
- stakeholders_involved: list[string]
- nature_of_disagreement: string
- resolution_status: string ["resolved","partially_resolved","unresolved"]
- risk_impact: string

4. Action Items
action_items: list[object]
- task_description: string
- owner: string
- supporting_stakeholders: list[string]
- deadline_or_timeline: string
- dependencies: list[string]
- status: string ["new","ongoing","blocked"]

5. Instructions
instructions: list[object]
- issuing_authority: string
- recipients: list[string]
- expected_outcome: string
- timeline: string
- advisory_or_mandatory: string ["advisory","mandatory"]

6. Objections
objections: list[object]
- raised_by: string
- concern: string
- category: string
- addressed: string ["yes","no","partially"]
- remaining_risk_if_unresolved: string

7. Follow-Ups
follow_ups: list[object]
- topic: string
- responsible_party: string
- trigger_condition: string
- expected_date_or_milestone: string

8. Awaiting Approvals
awaiting_approvals: list[object]
- item_requiring_approval: string
- approving_authority: string
- current_status: string
- impact_if_delayed: string

9. Meeting Effectiveness Assessment
meeting_effectiveness_assessment:
- decision_velocity: string
- accountability_clarity: string
- risk_exposure: string
- alignment_level: string
- overall_productivity_score: integer"""
)


SynthesisAgent = Agent(
    model=GoogleModel("gemini-2.5-flash"),
    system_prompt="""
You are given multiple extracted reports from DIFFERENT CHUNKS OF THE SAME MEETING.

Treat them as temporally ordered parts of one meeting.

Your task:
- Merge them into ONE authoritative meeting intelligence report
- Resolve duplicates
- Prefer later commitments over earlier tentative statements
- Produce a FINAL, CLEAN, GOVERNANCE-READY JSON

Output ONE JSON object only.
"""
)




def extract_data(meeting_transcript):
    chunks = chunk_transcript(meeting_transcript)

    chunk_outputs = []

    for i, chunk in enumerate(chunks):
        res = UnifiedAgent.run_sync(chunk)
        cleaned = clean_json(res.output)
        print(f"\n--- CHUNK {i+1} OUTPUT ---\n")
        print(cleaned)
        chunk_outputs.append(cleaned)

    merged_input = json.dumps(chunk_outputs, indent=2)

    final_res = SynthesisAgent.run_sync(merged_input)
    final_json = clean_json(final_res.output)

    print("\n--- FINAL UNIFIED REPORT ---\n")
    print(final_json)

    text_to_pdf(final_json, "meeting_report.pdf")

#example transcript

transcript =    """Alex:
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

extract_data(transcript)
