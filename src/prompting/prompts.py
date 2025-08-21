"""
Prompts for Silent Investigator
- System prompt defines role, task, format, context (RTFC)
- User prompt template provides the general instruction

Usage:
from src.prompting.prompts import SYSTEM_PROMPT, build_prompt
prompt = build_prompt(document_text)
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

# General user prompt template (RTFC applied in the user-level instruction)
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


def build_prompt(document_text: str, max_items: int = 10) -> str:
    """Builds the final prompt string to send to an LLM.

    Parameters:
        document_text: The text to analyze.
        max_items: The maximum number of missing items to request.
    Returns:
        The full prompt string.
    """
    return USER_PROMPT_TEMPLATE.format(document_text=document_text, max_items=max_items)


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