"""
Prompts for Silent Investigator
- System prompt defines role, task, format, context (RTFC)
- User prompt templates (general and zero-shot)

Usage:
from src.prompting.prompts import SYSTEM_PROMPT, build_prompt, build_zero_shot_prompt

# For a general prompt
prompt = build_prompt(document_text)

# For a zero-shot specific prompt
zero_shot_prompt = build_zero_shot_prompt(document_text)
"""

# System prompt using RTFC (Role, Task, Format, Context)
SYSTEM_PROMPT = (
    "You are Silent Investigator — an automated document investigator.\n"
    "Role: Expert analyst that inspects documents for missing, incomplete, or inconsistent information.\n"
    "Task: Given a document, identify any missing required fields or facts, explain why each item is missing, point to evidence spans in the text (if any), estimate confidence, and recommend concrete remediation steps.\n"
    "Format: Return ONLY a JSON object (no surrounding commentary) with the following keys:\n"
    "  - missing_fields: list of objects with {name, why_missing, evidence_span, required_information, priority, confidence} \n"
    "  - summary: short plain-text summary of the overall issues (1-2 sentences)\n"
    "  - remediation_steps: ordered list of concrete next steps to fix gaps\n"
    "Context: Use ONLY the provided document_text. Do NOT invent facts or fabricate sources. If the document does not contain enough information to decide, mark the relevant item as 'insufficient_information' in required_information and set confidence to 0.0.\n"
)

# General user prompt template
USER_PROMPT_TEMPLATE = (
    "Document:\n{document_text}\n\n"
    "Instruction (RTFC):\n"
    "Role: You are the investigator.\n"
    "Task: Find missing or incomplete information in the document and return the structured JSON described in the system prompt.\n"
    "Format: JSON only, follow the schema exactly.\n"
    "Context: Use only the document_text provided.\n"
    "Return up to {max_items} missing field entries.\n"
    "If nothing is missing, return missing_fields as an empty list."
)

# Zero-shot user prompt: explicit about zero-shot (no examples provided)
ZERO_SHOT_USER_PROMPT_TEMPLATE = (
    "ZERO-SHOT INSTRUCTION:\n"
    "You will analyze the document below and return the requested structured JSON. Do NOT use any examples — this is zero-shot.\n\n"
    "Document:\n{document_text}\n\n"
    "Task: Identify missing or incomplete information. For each missing item return:\n"
    "  - name: short identifier of the missing info (string)\n"
    "  - why_missing: brief rationale why it is missing or ambiguous (string)\n"
    "  - evidence_span: exact quote or nearest sentence from the document that indicates the gap (string or null)\n"
    "  - required_information: what must be provided to consider this present (string, or 'insufficient_information')\n"
    "  - priority: one of [low, medium, high]\n"
    "  - confidence: float between 0.0 and 1.0\n\n"
    "Format: Return ONLY a JSON object with keys: missing_fields, summary, remediation_steps.\n"
    "Important constraints:\n"
    "  - Use only the document_text; do not hallucinate sources or values.\n"
    "  - Keep the JSON stable (same schema) so it can be parsed by downstream tools.\n"
    "Return up to {max_items} items."
)


def build_prompt(document_text: str, max_items: int = 10) -> str:
    """Builds the general prompt string."""
    return USER_PROMPT_TEMPLATE.format(document_text=document_text, max_items=max_items)

def build_zero_shot_prompt(document_text: str, max_items: int = 10) -> str:
    """Builds the final prompt string for zero-shot evaluation."""
    return ZERO_SHOT_USER_PROMPT_TEMPLATE.format(document_text=document_text, max_items=max_items)


# Example JSON schema (for implementers/tests):
# {
#   "missing_fields": [
#       {
#           "name": "Patient Age",
#           "why_missing": "No age or DOB is present in header or body.",
#           "evidence_span": "Patient: John Doe\nSymptoms: cough...",  # or null
#           "required_information": "Numeric age or date of birth",
#           "priority": "high",
#           "confidence": 0.92
#       }
#   ],
#   "summary": "The document lacks patient identifiers and consent information.",
#   "remediation_steps": ["Request DOB from source", "Verify patient consent section"]
# }
"""
Prompts for Silent Investigator
- System prompt defines role, task, format, context (RTFC)
- User prompt templates (general, zero-shot, and one-shot)

Usage:
from src.prompting.prompts import build_prompt, build_zero_shot_prompt, build_one_shot_prompt

# Choose the appropriate function based on your needs
prompt = build_one_shot_prompt(document_text)
"""

# System prompt using RTFC (Role, Task, Format, Context)
SYSTEM_PROMPT = (
    "You are Silent Investigator — an automated document investigator.\n"
    "Role: Expert analyst that inspects documents for missing, incomplete, or inconsistent information.\n"
    "Task: Given a document, identify any missing required fields or facts, explain why each item is missing, point to evidence spans in the text (if any), estimate confidence, and recommend concrete remediation steps.\n"
    "Format: Return ONLY a JSON object (no surrounding commentary) with the following keys:\n"
    "  - missing_fields: list of objects with {name, why_missing, evidence_span, required_information, priority, confidence} \n"
    "  - summary: short plain-text summary of the overall issues (1-2 sentences)\n"
    "  - remediation_steps: ordered list of concrete next steps to fix gaps\n"
    "Context: Use ONLY the provided document_text. Do NOT invent facts or fabricate sources. If the document does not contain enough information to decide, mark the relevant item as 'insufficient_information' in required_information and set confidence to 0.0.\n"
)

# One-shot user prompt: provides one complete example
ONE_SHOT_USER_PROMPT_TEMPLATE = (
    "ONE-SHOT INSTRUCTION: Analyze the document provided in the 'Your Task' section by following the single example provided below.\n\n"
    "### Example ###\n"
    "Document:\n"
    "Patient Name: Jane Smith. The patient presents with a persistent cough and fever. Temperature is 101.2°F. Plan: Prescribe antibiotics and recommend rest.\n\n"
    "JSON Output:\n"
    "{\n"
    '  "missing_fields": [\n'
    '    {\n'
    '      "name": "Patient Date of Birth",\n'
    '      "why_missing": "The document identifies the patient by name but does not include their date of birth or age, which is a critical identifier for medical records.",\n'
    '      "evidence_span": "Patient Name: Jane Smith.",\n'
    '      "required_information": "Patient date of birth in YYYY-MM-DD format or their age.",\n'
    '      "priority": "high",\n'
    '      "confidence": 0.98\n'
    '    }\n'
    '  ],\n'
    '  "summary": "The patient record is missing the date of birth, a key identifier.",\n'
    '  "remediation_steps": ["Contact the patient or referring office to obtain the date of birth and update the record."]\n'
    "}\n\n"
    "### Your Task ###\n"
    "Document:\n{document_text}\n\n"
    "JSON Output:\n"
)


def build_one_shot_prompt(document_text: str) -> str:
    """Builds the final prompt string using a one-shot example."""
    return ONE_SHOT_USER_PROMPT_TEMPLATE.format(document_text=document_text)

# Previous functions for zero-shot and general prompts can also be kept for comparison
# ZERO_SHOT_USER_PROMPT_TEMPLATE = (...)
# def build_zero_shot_prompt(...)