"""
Agent Utilities
Common helper functions for agents
"""
import json
import re
import logging

logger = logging.getLogger(__name__)

# ==================================================
# UNIVERSAL SCIENTIFIC LAWS (NO LOCALIZATION NEEDED)
# ==================================================
# These laws are universal and don't require country-specific context
UNIVERSAL_LAWS = {
    "newton", "ohm", "kepler", "boyle", "charles", "gay-lussac", "avogadro", "coulomb",
    "faraday", "lenz", "ampere", "gauss", "stokes", "bernoulli", "hooke", "archimedes",
    "law of cooling", "law of motion", "law of thermodynamics", "law of conservation",
    "law of gravitation", "law of inertia", "law of acceleration", "law of action-reaction",
    "law of reflection", "law of refraction", "snell", "dalton", "graham", "henry", "raoult",
    "bragg", "planck", "heisenberg", "schrodinger", "pauli", "dirac"
}

def is_universal_law(topic: str) -> bool:
    """Check if a topic is a universal scientific law that doesn't need localization"""
    topic_lower = topic.lower().strip()
    for law in UNIVERSAL_LAWS:
        if law in topic_lower:
            return True
    return False

# ==================================================
# LOCALIZATION-SENSITIVE TOPIC CATEGORIES
# ==================================================
# Topics in these categories require country-specific context
# The LLM will dynamically use its knowledge for the specific country
LOCALIZED_TOPIC_KEYWORDS = {
    "law": ["law", "legal", "legislation", "court", "judiciary", "constitution", "statute", "regulation", "compliance", "criminal", "civil", "contract", "tort", "litigation"],
    "accounting": ["accounting", "audit", "taxation", "tax", "financial reporting", "gaap", "ifrs", "bookkeeping", "ledger", "balance sheet", "income statement"],
    "commerce": ["commerce", "business law", "trade", "import", "export", "customs", "tariff", "corporate governance", "company law", "partnership"],
    "finance": ["banking", "securities", "investment", "insurance", "pension", "mutual fund", "stock market", "capital market", "monetary policy"],
    "healthcare": ["medical practice", "healthcare regulation", "pharmaceutical", "drug approval", "patient rights", "medical licensing", "health insurance"],
    "education": ["education policy", "curriculum standards", "accreditation", "examination", "grading system", "educational qualification"],
    "labor": ["labor law", "employment", "workplace", "industrial relations", "minimum wage", "workers compensation", "trade union"],
    "real_estate": ["property law", "real estate", "land registration", "tenancy", "lease", "mortgage", "zoning"]
}


def requires_localization(topic: str) -> tuple[bool, str]:
    """
    Check if a topic requires country-specific localization.
    CRITICAL: Check for universal scientific laws FIRST to prevent false positives
    Returns: (needs_localization, category)
    """
    # FIRST: Check if it's a universal scientific law
    if is_universal_law(topic):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Localization: '{topic}' identified as Universal Scientific Law. Skipping country context.")
        return False, "universal_science"

    topic_lower = topic.lower()
    for category, keywords in LOCALIZED_TOPIC_KEYWORDS.items():
        if any(keyword in topic_lower for keyword in keywords):
            return True, category
    return False, "general"


def get_localization_guidance(topic: str, country: str) -> str:
    """
    Generate localization guidance for a topic based on user's country.
    Uses dynamic LLM knowledge instead of hardcoded country data.
    For topics like law, accounting, commerce - instructs LLM to use country-specific context.
    For general topics - provides global accessibility guidance.
    """
    needs_local, category = requires_localization(topic)
    
    if not country or country.strip() == "":
        country = "Global"  # Default to global if no country specified
    
    if needs_local and country != "Global":
        return f"""
LOCALIZATION REQUIREMENTS (Topic requires country-specific context):
- Country: {country}
- Topic Category: {category.replace('_', ' ').title()}

IMPORTANT: This topic requires {country}-specific content. You MUST:

1. REGULATORY FRAMEWORK:
   - Reference {country}'s specific laws, acts, and regulations for {category}
   - Cite the relevant regulatory bodies and authorities in {country}
   - Use the correct legal/professional terminology used in {country}

2. CURRENCY & UNITS:
   - Use {country}'s local currency for all monetary examples
   - Use the measurement system commonly used in {country}

3. EXAMPLES & CASE STUDIES:
   - Use {country}-based companies, institutions, and scenarios
   - Reference well-known {country} cases or precedents where relevant
   - Use names, places, and contexts familiar to {country} learners

4. PROFESSIONAL STANDARDS:
   - Reference {country}'s professional bodies and certification requirements
   - Use industry terminology as practiced in {country}

5. ACCURACY:
   - Draw from your knowledge of {country}'s {category} framework
   - If specific details are uncertain, use general principles applicable to {country}
   - Avoid mixing regulations from different countries
"""
    else:
        # Global context for non-localized topics
        return f"""
GLOBAL ACCESSIBILITY (Topic is universally applicable):
- Use metric units (km, kg, °C) as primary measurement system
- Reference international standards where applicable (ISO, IEEE, etc.)
- Include examples from multiple geographic regions
- Avoid culture-specific idioms or references
- Use globally recognized terminology
- Make content accessible to learners worldwide
"""


# ==================================================
# LEVEL DEFINITIONS FOR CONSISTENT CURRICULUM DESIGN
# ==================================================
LEVEL_PROFILES = {
    "School": {
        "age_range": "14-18 years",
        "depth": "foundational",
        "vocabulary": "simple, clear language avoiding jargon",
        "prerequisites": "basic literacy and numeracy",
        "examples": "everyday life, relatable scenarios for teenagers",
        "complexity": "introduce concepts gradually with concrete examples",
        "assessment": "recall, basic understanding, simple application",
        "cognitive_load": "low to moderate",
        "global_context": "examples from diverse cultures and regions worldwide"
    },
    "Undergraduate": {
        "age_range": "18-24 years",
        "depth": "intermediate to advanced",
        "vocabulary": "academic terminology with clear definitions",
        "prerequisites": "high school foundation in the subject area",
        "examples": "industry case studies, research findings, professional scenarios",
        "complexity": "theoretical frameworks with practical applications",
        "assessment": "analysis, application, critical evaluation",
        "cognitive_load": "moderate to high",
        "global_context": "international case studies, cross-cultural perspectives"
    },
    "Postgraduate": {
        "age_range": "22-40 years",
        "depth": "advanced and specialized",
        "vocabulary": "specialized terminology, assumes prior knowledge",
        "prerequisites": "undergraduate degree or equivalent experience",
        "examples": "cutting-edge research, complex real-world problems, scholarly debates",
        "complexity": "nuanced analysis, synthesis of multiple perspectives",
        "assessment": "critical evaluation, creation, research methodology",
        "cognitive_load": "high",
        "global_context": "global research landscape, international standards and practices"
    },
    "Professional": {
        "age_range": "25+ years",
        "depth": "practical and application-focused",
        "vocabulary": "industry-standard terminology, practical jargon",
        "prerequisites": "working experience in related field",
        "examples": "workplace scenarios, ROI-focused, immediate applicability",
        "complexity": "decision-making frameworks, best practices, trade-offs",
        "assessment": "problem-solving, strategic thinking, implementation",
        "cognitive_load": "variable based on experience",
        "global_context": "international standards, cross-border considerations, diverse market contexts"
    }
}

def get_level_profile(level: str) -> dict:
    """Get the profile for a specific education level"""
    # Normalize level string
    level_key = level.replace("LessonLevel.", "").strip()
    return LEVEL_PROFILES.get(level_key, LEVEL_PROFILES["Undergraduate"])

def get_level_guidance(level: str) -> str:
    """Generate detailed guidance string for a level"""
    profile = get_level_profile(level)
    return f"""
TARGET AUDIENCE PROFILE:
- Age Range: {profile['age_range']}
- Content Depth: {profile['depth']}
- Language Style: {profile['vocabulary']}
- Prerequisites: {profile['prerequisites']}
- Example Types: {profile['examples']}
- Complexity Level: {profile['complexity']}
- Cognitive Load: {profile['cognitive_load']}
- Global Context: {profile['global_context']}
"""

# ==================================================
# DURATION-BASED CURRICULUM STRUCTURE
# ==================================================
def duration_profile(minutes: int) -> dict:
    """Return lesson structure based on duration with detailed guidance"""
    if minutes <= 30:
        return {
            "objectives": 3, 
            "sections": ["Introduction", "Core Concepts"], 
            "takeaways": 3,  # Scale with duration
            "quiz": 1,
            "scenarios": 3,  # Quiz scenarios scale with duration
            "depth_guidance": "Focus on essential concepts only. Prioritize clarity over breadth.",
            "pacing": "Quick introduction (3 min), core content (20 min), summary (5 min), quiz (2 min)"
        }
    elif minutes <= 45:
        return {
            "objectives": 4, 
            "sections": ["Introduction", "Core Concepts", "Practical Examples"], 
            "takeaways": 4,  # Scale with duration
            "quiz": 1,
            "scenarios": 4,
            "depth_guidance": "Cover fundamentals with one practical example. Balance theory and practice.",
            "pacing": "Introduction (5 min), core concepts (20 min), practical examples (12 min), summary (5 min), quiz (3 min)"
        }
    elif minutes <= 60:
        return {
            "objectives": 5, 
            "sections": ["Introduction", "Core Concepts", "Practical Examples", "Real-World Applications"], 
            "takeaways": 5,  # Scale with duration
            "quiz": 2,
            "scenarios": 5,
            "depth_guidance": "Comprehensive coverage with multiple examples and real-world applications.",
            "pacing": "Introduction (5 min), core concepts (20 min), examples (15 min), applications (10 min), summary (5 min), quiz (5 min)"
        }
    else:
        return {
            "objectives": 6, 
            "sections": ["Introduction", "Core Concepts", "Practical Examples", "Real-World Applications", "Case Studies"], 
            "takeaways": 6,  # Scale with duration
            "quiz": 3,
            "scenarios": 6,
            "depth_guidance": "In-depth exploration with case studies, discussions, and advanced applications.",
            "pacing": "Introduction (5 min), core concepts (25 min), examples (20 min), applications (15 min), case study (15 min), summary (5 min), quiz (5 min)"
        }


async def call_llm_and_parse_list(client, prompt, max_items=6, temperature=0.4):
    """
    Calls LLM and safely extracts a list of strings.
    Works with JSON, bullets, numbered text.
    Async implementation for compatibility with AsyncOpenAI.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return a clean list only."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )

        text = response.choices[0].message.content.strip()

        # Try JSON parsing first
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [str(x).strip() for x in data[:max_items]]
        except Exception:
            pass

        # Fallback: bullet or numbered text
        lines = re.split(r"\n|•|-|\d+\.", text)
        cleaned = [l.strip() for l in lines if len(l.strip()) > 3]

        return cleaned[:max_items]
        
    except Exception as e:
        logger.error(f"Error in call_llm_and_parse_list: {e}")
        return []

# ==================================================
# RBT LOGIC & INTELLIGENCE
# ==================================================
RBT_ORDER = {
    "Remember": 1,
    "Understand": 2,
    "Apply": 3,
    "Analyze": 4,
    "Evaluate": 5,
    "Create": 6
}

def extract_rbt_levels(text: str) -> list[str]:
    """Extract Bloom's Taxonomy levels from text"""
    t = text.lower()
    levels = []
    if any(v in t for v in ["remember", "list", "define", "recall", "state"]): levels.append("Remember")
    if any(v in t for v in ["understand", "explain", "describe", "summarize", "discuss"]): levels.append("Understand")
    if any(v in t for v in ["apply", "use", "implement", "demonstrate", "solve"]): levels.append("Apply")
    if any(v in t for v in ["analyze", "compare", "contrast", "investigate", "examine"]): levels.append("Analyze")
    if any(v in t for v in ["evaluate", "assess", "justify", "critique", "judge"]): levels.append("Evaluate")
    if any(v in t for v in ["create", "design", "develop", "formulate", "construct"]): levels.append("Create")
    return list(set(levels))

def dominant_rbt(text: str) -> str:
    """Determine the highest order cognitive skill in the text"""
    levels = extract_rbt_levels(text)
    return max(levels, key=lambda l: RBT_ORDER[l]) if levels else "Understand"