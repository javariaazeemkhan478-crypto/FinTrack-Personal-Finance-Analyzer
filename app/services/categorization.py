from typing import Tuple

RULES = {
    "mcdonald's": "Food",
    "mcdonalds": "Food",
    "uber": "Transport",
    "netflix": "Entertainment",
    "electricity": "Utilities",
    "amazon": "Shopping",
    "hospital": "Healthcare",
    "university": "Education",
    "salary": "Salary",
    "freelance": "Freelance"
}

def suggest_category(description: str) -> Tuple[str, str, str]:
    if not description:
        return "Other", "Low", "No description provided"
    
    desc_lower = description.lower()
    for key, category in RULES.items():
        if key in desc_lower:
            return category, "High", f"Matched keyword: {key}"
            
    return "Other", "Low", "No matches found"
