"""
AI prompts for challenge analysis.
"""

# System prompt for challenge analysis
SYSTEM_PROMPT = """You are an AI assistant helping analyze societal challenges for the SamadhanX platform in Jharkhand, India.

Your role is to:
1. Understand challenges submitted by citizens (may be in English, Hindi, or Hinglish)
2. Classify challenges into appropriate domains
3. Assess severity and urgency
4. Extract required skills
5. Recommend solution approaches

IMPORTANT RULES:
- Use ONLY facts provided in the challenge
- Do NOT invent population numbers, locations, or other data
- Provide concise, clear explanations
- Return structured JSON output
- Map to existing domain taxonomy when possible
- Be culturally aware of Jharkhand context"""

# Available domains
DOMAIN_TAXONOMY = [
    "Education",
    "Healthcare",
    "Agriculture",
    "Water Management",
    "Sanitation",
    "Environment",
    "Energy",
    "Urban Infrastructure",
    "Accessibility",
    "Public Administration",
    "Rural Livelihoods",
    "Disaster Management"
]

# Available skills
SKILL_TAXONOMY = [
    "AI/ML",
    "IoT",
    "GIS",
    "Computer Vision",
    "Embedded Systems",
    "Agricultural Engineering",
    "Water Engineering",
    "Civil Engineering",
    "Environmental Science",
    "Renewable Energy",
    "Electronics",
    "Data Science",
    "Mobile Development",
    "Web Development",
    "Robotics",
    "Mechanical Engineering",
    "Biotechnology",
    "Public Health",
    "Telemedicine"
]

def build_analysis_prompt(title: str, description: str, district: str, categories: list) -> str:
    """
    Build analysis prompt for challenge.
    
    Args:
        title: Challenge title
        description: Challenge description
        district: District name
        categories: Existing categories (may be citizen-selected)
        
    Returns:
        Formatted prompt
    """
    
    category_info = f"Citizen selected categories: {', '.join(categories)}" if categories else "No categories selected"
    
    prompt = f"""Analyze the following societal challenge from Jharkhand, India.

CHALLENGE INFORMATION:
Title: {title}
Description: {description}
Location: {district} district, Jharkhand
{category_info}

ANALYSIS REQUIRED:

1. **Language & Summary**
   - Detect the input language
   - Provide a concise English summary (2-3 sentences max)
   - Normalize the problem statement

2. **Classification**
   - Choose ONE primary domain from: {', '.join(DOMAIN_TAXONOMY)}
   - Optionally identify secondary domains
   - Provide classification reasoning (1-2 sentences)
   - Provide confidence score (0.0-1.0)

3. **Severity Assessment** (0-100)
   Consider: safety risk, health impact, environmental impact, infrastructure failure, population affected
   - Provide severity score
   - Provide reasoning (1-2 sentences)
   - Use ONLY facts from the challenge

4. **Urgency Assessment** (0-100)
   Consider: immediate risks, seasonal dependency, time sensitivity, recurring damage
   - Provide urgency score
   - Provide reasoning (1-2 sentences)
   - Use ONLY facts from the challenge

5. **Skill Extraction**
   - Identify required technical skills from: {', '.join(SKILL_TAXONOMY)}
   - Provide confidence for each skill (0.0-1.0)
   - List 3-5 most relevant skills

6. **Solution Recommendations**
   - Suggest 2-4 solution APPROACHES (not final solutions)
   - Examples: "IoT monitoring system", "Mobile application", "GIS platform", "Sensor network"
   - Provide confidence for each (0.0-1.0)

7. **Affected Population**
   - If explicitly stated, use that number
   - If NOT stated, return null
   - Do NOT invent numbers

8. **Overall Confidence**
   - Provide overall analysis confidence (0.0-1.0)

Return valid JSON matching this structure:
{{
  "summary": "string",
  "detected_language": "string or null",
  "classification": {{
    "primary_domain": "string",
    "secondary_domains": ["string"],
    "confidence_score": 0.0-1.0,
    "classification_reason": "string"
  }},
  "severity": {{
    "severity_score": 0-100,
    "severity_reason": "string"
  }},
  "urgency": {{
    "urgency_score": 0-100,
    "urgency_reason": "string"
  }},
  "skills": [
    {{
      "name": "string",
      "confidence": 0.0-1.0
    }}
  ],
  "solution_types": [
    {{
      "type": "string",
      "confidence": 0.0-1.0
    }}
  ],
  "affected_population_estimate": integer or null,
  "confidence_score": 0.0-1.0
}}

Respond with ONLY valid JSON. No additional text."""

    return prompt


def build_embedding_text(title: str, description: str, summary: str, primary_domain: str) -> str:
    """
    Build text for embedding generation.
    
    Args:
        title: Challenge title
        description: Challenge description
        summary: AI-generated summary
        primary_domain: Primary domain
        
    Returns:
        Combined text for embedding
    """
    return f"{title}. {summary}. {description}. Domain: {primary_domain}"
