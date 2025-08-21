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
"""
Prompts for Silent Investigator
- System prompt defines the AI's core role and rules.
- User prompt templates are provided for zero-shot, one-shot, and multi-shot (few-shot) prompting.

Usage:
from src.prompting.prompts import build_zero_shot_prompt, build_one_shot_prompt, build_multi_shot_prompt

# Choose the function that best fits the complexity of your task.
# For complex tasks, multi-shot is often the most reliable.
prompt = build_multi_shot_prompt(document_text)
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

# Multi-shot user prompt: provides multiple, varied examples
MULTI_SHOT_USER_PROMPT_TEMPLATE = (
    "MULTI-SHOT INSTRUCTION: Analyze the document in the 'Your Task' section by learning from the multiple examples provided below. Notice how the task applies to different contexts.\n\n"
    "### Example 1 (Medical Context) ###\n"
    "Document:\n"
    "Patient Name: Jane Smith. The patient presents with a persistent cough and fever. Temperature is 101.2°F. Plan: Prescribe antibiotics and recommend rest.\n\n"
    "JSON Output:\n"
    "{\n"
    '  "missing_fields": [\n'
    '    {\n'
    '      "name": "Patient Date of Birth",\n'
    '      "why_missing": "The document identifies the patient by name but does not include their date of birth or age, a critical identifier.",\n'
    '      "evidence_span": "Patient Name: Jane Smith.",\n'
    '      "required_information": "Patient date of birth in YYYY-MM-DD format or their age.",\n'
    '      "priority": "high",\n'
    '      "confidence": 0.98\n'
    '    }\n'
    '  ],\n'
    '  "summary": "The patient record is missing the date of birth, a key identifier.",\n'
    '  "remediation_steps": ["Contact the patient or referring office to obtain the date of birth."]\n'
    "}\n\n"
    "### Example 2 (Business Context) ###\n"
    "Document:\n"
    "To: Team\nFrom: Alex\nSubject: Project Phoenix Update\n\nThe team has completed the UI mockups and the API is now in testing. We are on track to meet the Q3 deadline. Let's sync next week.\n\n"
    "JSON Output:\n"
    "{\n"
    '  "missing_fields": [\n'
    '    {\n'
    '      "name": "Project Budget Status",\n'
    '      "why_missing": "The project update mentions progress and deadlines but completely omits any reference to the budget, spending, or financial status.",\n'
    '      "evidence_span": "We are on track to meet the Q3 deadline.",\n'
    '      "required_information": "A statement on current budget utilization (e.g., on-budget, over-budget, under-budget).",\n'
    '      "priority": "medium",\n'
    '      "confidence": 0.95\n'
    '    }\n'
    '  ],\n'
    '  "summary": "The project status update is missing any mention of the budget.",\n'
    '  "remediation_steps": ["Reply to the email asking for a clarification on the project budget status."]\n'
    "}\n\n"
    "### Your Task ###\n"
    "Document:\n{document_text}\n\n"
    "JSON Output:\n"
)

def build_multi_shot_prompt(document_text: str) -> str:
    """Builds the final prompt string using multiple examples (few-shot)."""
    return MULTI_SHOT_USER_PROMPT_TEMPLATE.format(document_text=document_text)
import json

# --- Example Library ---
# In a real application, this could be a database of high-quality examples.
EXAMPLE_LIBRARY = {
    "medical": {
        "document": "Patient Name: Jane Smith. The patient presents with a persistent cough and fever. Temperature is 101.2°F. Plan: Prescribe antibiotics and recommend rest.",
        "json_output": {
          "missing_fields": [
            {
              "name": "Patient Date of Birth",
              "why_missing": "The document identifies the patient by name but does not include their date of birth or age, a critical identifier.",
              "evidence_span": "Patient Name: Jane Smith.",
              "required_information": "Patient date of birth in YYYY-MM-DD format or their age.",
              "priority": "high",
              "confidence": 0.98
            }
          ],
          "summary": "The patient record is missing the date of birth, a key identifier.",
          "remediation_steps": ["Contact the patient or referring office to obtain the date of birth."]
        }
    },
    "business": {
        "document": "To: Team\nFrom: Alex\nSubject: Project Phoenix Update\n\nThe team has completed the UI mockups and the API is now in testing. We are on track to meet the Q3 deadline. Let's sync next week.",
        "json_output": {
          "missing_fields": [
            {
              "name": "Project Budget Status",
              "why_missing": "The project update mentions progress and deadlines but completely omits any reference to the budget, spending, or financial status.",
              "evidence_span": "We are on track to meet the Q3 deadline.",
              "required_information": "A statement on current budget utilization (e.g., on-budget, over-budget, under-budget).",
              "priority": "medium",
              "confidence": 0.95
            }
          ],
          "summary": "The project status update is missing any mention of the budget.",
          "remediation_steps": ["Reply to the email asking for a clarification on the project budget status."]
        }
    }
}

def get_relevant_examples(document_text: str, num_examples: int) -> str:
    """Selects relevant examples from the library based on document content."""
    examples_str = ""
    # Simple logic to detect context
    if "patient" in document_text.lower() or "medical" in document_text.lower():
        selected_examples = [EXAMPLE_LIBRARY["medical"]]
    elif "project" in document_text.lower() or "team" in document_text.lower():
        selected_examples = [EXAMPLE_LIBRARY["business"]]
    else:
        # Default to a mix if context is unclear
        selected_examples = list(EXAMPLE_LIBRARY.values())

    # Format the selected examples
    for i, example in enumerate(selected_examples[:num_examples]):
        examples_str += f"### Example {i+1} ###\n"
        examples_str += f"Document:\n{example['document']}\n\n"
        examples_str += f"JSON Output:\n{json.dumps(example['json_output'], indent=2)}\n\n"
    
    return examples_str

def build_dynamic_prompt(document_text: str) -> str:
    """
    Builds a prompt dynamically by choosing the best strategy (zero, one, or multi-shot)
    and selecting the most relevant examples at runtime.
    """
    prompt_strategy = ""
    num_examples = 0
    
    # 1. Logic to determine the best strategy based on document length
    doc_length = len(document_text.split())
    if doc_length < 20:
        # For very short documents, zero-shot is often sufficient.
        prompt_strategy = "ZERO-SHOT"
        num_examples = 0
    elif doc_length < 100:
        # For medium documents, one relevant example is helpful.
        prompt_strategy = "ONE-SHOT"
        num_examples = 1
    else:
        # For long or complex documents, multi-shot is the most robust.
        prompt_strategy = "MULTI-SHOT"
        num_examples = 2 # Or more if the library is larger

    # 2. Assemble the prompt components
    instruction = (
        f"{prompt_strategy} INSTRUCTION: Based on the examples provided (if any), "
        "analyze the document in the 'Your Task' section and return the structured JSON."
    )
    
    examples_section = get_relevant_examples(document_text, num_examples)
    
    task_section = f"### Your Task ###\nDocument:\n{document_text}\n\nJSON Output:\n"

    # 3. Construct the final prompt
    final_prompt = f"{instruction}\n\n{examples_section}{task_section}"
    
    return final_prompt

# --- Example Usage ---
short_doc = "Invoice #123 for services rendered. Total due: $500."
long_doc = "Patient Name: John Doe. Age: 45. The patient reports chest pain and shortness of breath. The primary care physician was Dr. Evans. Plan is to run a cardiac enzyme panel and a chest X-ray. Follow-up scheduled for next week."

print("--- DYNAMIC PROMPT FOR SHORT DOCUMENT (Chooses ZERO-SHOT) ---")
print(build_dynamic_prompt(short_doc))
print("\n" + "="*50 + "\n")
print("--- DYNAMIC PROMPT FOR LONG MEDICAL DOCUMENT (Chooses MULTI-SHOT with relevant example) ---")
print(build_dynamic_prompt(long_doc))