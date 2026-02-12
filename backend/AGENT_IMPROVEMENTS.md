# Agent Improvements Documentation

## Overview

This document details the comprehensive improvements made to the Teach-Genie agent system to achieve **consistent, expert-level curriculum generation** that is:
- Level-appropriate (School → Professional)
- Duration-aware (15 → 120+ minutes)
- **Country-localized** for topics requiring regional context (law, accounting, commerce, etc.)
- Globally accessible for universal topics (science, mathematics, technology)

---

## NEW: Country-Based Localization System

### Problem Statement
Topics like law, accounting, commerce, taxation, and healthcare require country-specific context. A lesson on "Contract Law" for an Indian user must reference the Indian Contract Act 1872, while the same topic for a US user should reference the Uniform Commercial Code.

### Solution Implemented

#### Localization-Sensitive Topic Categories
Topics in these categories automatically trigger country-specific content generation:

| Category | Keywords Detected |
|----------|------------------|
| Law | law, legal, legislation, court, judiciary, constitution, statute |
| Accounting | accounting, audit, taxation, tax, financial reporting, GAAP, IFRS |
| Commerce | commerce, business law, trade, import, export, corporate governance |
| Finance | banking, securities, investment, insurance, pension, stock market |
| Healthcare | medical practice, healthcare regulation, pharmaceutical, drug approval |
| Education | education policy, curriculum standards, accreditation, examination |
| Labor | labor law, employment, workplace, industrial relations, minimum wage |
| Real Estate | property law, real estate, land registration, tenancy, lease |

#### Dynamic LLM-Based Localization
Instead of hardcoding country-specific laws (which is not scalable), the system:
1. Detects if a topic requires localization based on keywords
2. Passes the user's country to the LLM with clear instructions
3. Lets the LLM use its comprehensive knowledge to generate country-appropriate content
4. Includes guidance for regulatory framework, currency, units, and examples

**Benefits of this approach:**
- Works for any country (not limited to pre-defined list)
- Always uses the LLM's up-to-date knowledge
- No maintenance required for country-specific data
- Scalable and future-proof

#### Key Functions Added to `utils.py`

| Function | Purpose |
|----------|---------|
| `requires_localization(topic)` | Checks if topic needs country-specific context |
| `get_localization_guidance(topic, country)` | Generates dynamic localization prompt for LLM |

---

## 1. Utils Module (`app/agents/utils.py`)

### New Additions

#### LEVEL_PROFILES Dictionary
A comprehensive profile system defining characteristics for each educational level:

```python
LEVEL_PROFILES = {
    "School": {
        "age_range": "13-18 years",
        "depth": "Foundational understanding with concrete examples",
        "vocabulary": "Simple, everyday language; avoid jargon",
        "prerequisites": "Basic literacy and numeracy",
        "examples": "Relatable scenarios from daily life, school, family",
        "complexity": "Single-step reasoning, clear cause-effect",
        "assessment": "Recognition and recall, basic application",
        "cognitive_load": "Low - one concept at a time",
        "global_context": "Universal examples accessible across cultures"
    },
    "Undergraduate": {...},
    "Postgraduate": {...},
    "Professional": {...}
}
```

#### Helper Functions

| Function | Purpose |
|----------|---------|
| `get_level_profile(level)` | Returns the complete profile dict for a given level |
| `get_level_guidance(level)` | Generates formatted guidance string for prompts |

#### Enhanced `duration_profile()` Function

**Before:**
```python
def duration_profile(minutes: int) -> Dict[str, Any]:
    return {
        "sections": 4,
        "depth": "moderate",
        "examples": 2,
        "quiz_questions": 5,
        "resources": 4
    }
```

**After:**
```python
def duration_profile(minutes: int) -> Dict[str, Any]:
    # Includes new fields:
    # - depth_guidance: Specific instructions for content depth
    # - pacing: Minutes per section guideline
    # Dynamic scaling from ultra-short (15min) to comprehensive (120+min)
```

### Why It's Better

1. **Centralized Configuration**: All level-specific parameters in one place
2. **Consistency**: Every agent uses the same level definitions
3. **Maintainability**: Easy to add new levels or modify existing ones
4. **Rich Context**: Provides vocabulary, complexity, and cultural guidelines

---

## 2. Planner Agent (`app/agents/planner.py`)

### Key Changes

#### System Prompt Enhancement

**Before:**
```
"You are an expert curriculum designer. Return JSON only."
```

**After:**
```
"You are a world-class curriculum architect with expertise in educational psychology,
instructional design, and learning science. You design curricula used by educators
globally, ensuring content is culturally neutral, pedagogically sound, and
appropriate for the target audience level."
```

#### User Prompt Improvements

| Aspect | Before | After |
|--------|--------|-------|
| Level Context | Just level name | Full profile with age range, depth, vocabulary |
| Duration Handling | Basic section count | Pacing guidance, depth instructions |
| Section Structure | Generic list | Detailed structure with timing, goals, engagement hooks |
| Global Standards | Not addressed | Explicit cultural neutrality requirements |

#### New Prompt Sections

1. **Educational Context Block**
   - Target audience characteristics
   - Prior knowledge assumptions
   - Vocabulary constraints

2. **Curriculum Design Principles**
   - Progressive complexity
   - Active learning integration
   - Universal accessibility

3. **Section Structure Template**
   - Learning goal per section
   - Engagement hooks
   - Time allocation
   - Transition logic

### Why It's Better

1. **Expert-Level Output**: Prompts emulate professional curriculum designers
2. **Pedagogically Sound**: Follows learning science principles
3. **Globally Acceptable**: Explicit instructions for cultural neutrality
4. **Structured Planning**: Each section has clear purpose and timing

---

## 3. Content Agent (`app/agents/content.py`)

### Key Changes

#### Level-Aware Content Generation

**Before:**
```python
user_prompt = f"""
Topic: {topic}
Level: {level}
Section: {section_title}
...
"""
```

**After:**
```python
level_profile = get_level_profile(level)
user_prompt = f"""
TOPIC: {topic}
EDUCATION LEVEL: {level}
TARGET AUDIENCE: {level_profile['age_range']}

LEVEL-SPECIFIC REQUIREMENTS:
- Vocabulary: {level_profile['vocabulary']}
- Depth: {level_profile['depth']}
- Complexity: {level_profile['complexity']}
- Examples: {level_profile['examples']}
- Global Context: {level_profile['global_context']}
...
"""
```

#### Enhanced Resource Generation

**Before:** Generic 4-6 resources

**After:**
```
RESOURCES (exactly 8 items):
Generate a balanced mix across these categories:
- 2 theoretical/foundational resources
- 2 practical/applied resources  
- 2 video/multimedia resources
- 2 reference/documentation resources

Each resource with:
- Type categorization (video, article, course, documentation, tool, book)
- Difficulty indicator (matches level)
- Brief description of value
```

#### Global Accessibility Guidelines

New section added:
```
GLOBAL ACCESSIBILITY:
- Use metric units (km, kg, °C) as primary
- Reference international standards and organizations
- Include examples from multiple geographic regions
- Avoid culture-specific idioms or references
- Use globally recognized terminology
```

### Why It's Better

1. **Level-Appropriate Language**: Content matches audience vocabulary
2. **Richer Resources**: 8 balanced resources across categories
3. **Cultural Neutrality**: Explicit guidelines for global content
4. **Consistent Depth**: Matches level complexity requirements

---

## 4. Quiz Agent (`app/agents/quiz.py`)

### Key Changes

#### Complete Prompt Redesign

**Before:**
```
"You are an expert assessment designer creating multiple-choice questions."
```

**After:**
```
"You are an expert assessment designer with specialization in creating globally
accessible, level-appropriate evaluations. Your questions are used by educational
institutions worldwide and must be culturally neutral, pedagogically sound, and
aligned with international educational standards."
```

#### Level-Appropriate Question Design

| Level | Question Characteristics |
|-------|-------------------------|
| School | Simple scenarios, single-concept focus, clear correct answers |
| Undergraduate | Applied scenarios, multi-step reasoning, some ambiguity |
| Postgraduate | Complex scenarios, synthesis required, nuanced options |
| Professional | Real-world cases, decision-making focus, industry context |

#### New Prompt Sections

1. **Question Design Principles**
   - Progressive difficulty within quiz
   - Cover different cognitive levels
   - Real-world scenario focus
   - Clear, unambiguous wording

2. **Global Accessibility for Questions**
   ```
   - Use universally recognized scenarios
   - Avoid culturally specific references
   - Use metric units and international standards
   - Names should be culturally diverse
   - Avoid region-specific regulations
   ```

3. **Option Design Guidelines**
   - All options must be plausible
   - Correct answer shouldn't be obviously longer
   - Avoid "all of the above" patterns
   - Distractors based on common misconceptions

### Why It's Better

1. **Scenario-Based**: Questions test application, not memorization
2. **Globally Accessible**: Culturally neutral scenarios and examples
3. **Cognitively Appropriate**: Question complexity matches level
4. **Better Distractors**: Options based on real misconceptions

---

## 5. Key Takeaways Agent (`app/agents/key_takeaways.py`)

### Key Changes

#### Level Integration

**Before:** No level-specific handling

**After:**
```python
from app.agents.utils import get_level_profile
level_profile = get_level_profile(level)

# Used in prompt:
# - Vocabulary matching level
# - Complexity appropriate to audience
# - Global context requirements
```

#### Enhanced Prompt Structure

**Before:**
```
"Generate EXACTLY 5 key takeaways..."
```

**After:**
```
KEY TAKEAWAY DESIGN GUIDELINES:

1. STRUCTURE (EXACTLY 5 takeaways):
   - "title": Short header (2-5 words) - the key concept
   - "description": One complete sentence explaining the insight

2. CONTENT QUALITY:
   - Focus on "aha moments" and core insights
   - Make them memorable and quotable
   - Ensure practical applicability
   - DO NOT repeat learning objectives verbatim

3. GLOBAL ACCESSIBILITY:
   - Use universally understood concepts
   - Avoid culture-specific references
   - Include globally relevant examples
```

#### Improved Examples

**Before:**
```json
{
    "title": "Causes of Conflict",
    "description": "Economic inequality..."
}
```

**After:**
```json
[
    {
        "title": "Supply Meets Demand",
        "description": "Market prices naturally adjust to balance..."
    },
    {
        "title": "Code Reusability",
        "description": "Functions allow you to write logic once..."
    }
]
```

#### Better Fallback Content

**Before:**
```python
{"title": f"Introduction to {topic}", "description": f"{topic} is a fundamental concept..."}
```

**After:**
```python
{"title": "Core Concept", "description": f"{topic} represents a foundational idea with applications across multiple domains."}
{"title": "Global Relevance", "description": f"{topic} plays a significant role in international contexts and cross-cultural applications."}
```

### Why It's Better

1. **Insight-Focused**: Takeaways are "aha moments", not objectives
2. **Memorable**: Short titles, complete explanations
3. **Level-Appropriate**: Language matches audience
4. **Globally Relevant**: Universal applicability emphasized

---

## Comparison Summary

| Aspect | Before | After |
|--------|--------|-------|
| Level Awareness | Basic level name only | Comprehensive profiles with 9 parameters |
| Duration Handling | Fixed section counts | Dynamic scaling with depth guidance |
| **Country Localization** | Not addressed | Smart detection for law/accounting/commerce topics |
| Global Accessibility | Not addressed | Explicit in every agent's prompts |
| Vocabulary Control | None | Level-specific vocabulary guidelines |
| Question Quality | Generic MCQs | Scenario-based, cognitively appropriate |
| Resource Diversity | Random selection | Categorized, balanced distribution |
| Content Depth | One-size-fits-all | Scaled to level complexity |
| Cultural Neutrality | Not considered | Metric units, diverse names, universal examples |
| **Regulatory Context** | None | Country-specific laws, standards for relevant topics |

---

## Impact on Generated Content

### Country-Specific Topics (Law, Accounting, Commerce, etc.)

The LLM dynamically uses its knowledge to generate country-appropriate content:

For a user from **India** generating a lesson on "Contract Law":
- LLM references Indian Contract Act and relevant Indian laws
- Uses INR (₹) for monetary examples
- Cites Indian courts and legal precedents
- Uses Indian company examples

For a user from **United States** generating the same topic:
- LLM references UCC and relevant US laws
- Uses USD ($) for monetary examples
- Cites US federal and state courts
- Uses US company examples

For a user from **any other country** (e.g., Brazil, Japan, South Africa):
- LLM uses its knowledge of that country's legal/regulatory framework
- No hardcoded data required - works for any country

### Universal Topics (Science, Mathematics, Technology)
- Global accessibility with metric units
- Examples from diverse cultures and regions
- Internationally recognized standards

### School Level (13-18 years)
- Simple vocabulary, concrete examples
- Daily life scenarios
- Single-concept questions
- Foundational takeaways

### Undergraduate Level (18-24 years)
- Academic vocabulary with definitions
- Case studies and research references
- Applied reasoning questions
- Conceptual connection takeaways

### Postgraduate Level (22-30 years)
- Technical terminology expected
- Research methodology integration
- Complex analytical questions
- Advanced synthesis takeaways

### Professional Level (25+ years)
- Industry-standard terminology
- Real-world case studies
- Decision-making questions
- Practical implementation takeaways

---

## Files Modified

| File | Changes |
|------|---------|
| `app/agents/utils.py` | Added LEVEL_PROFILES, LOCALIZED_TOPIC_KEYWORDS, get_level_profile(), get_level_guidance(), get_localization_guidance(), requires_localization(), enhanced duration_profile() |
| `app/agents/orchestrator.py` | Added country parameter to generate_full_lesson(), passes to state |
| `app/agents/planner.py` | Accepts country parameter, uses localization guidance in prompts |
| `app/agents/content.py` | Level-aware content with country localization for relevant topics |
| `app/agents/quiz.py` | Country-specific scenarios for law/accounting/commerce topics |
| `app/agents/key_takeaways.py` | Context-aware takeaways based on topic category and country |
| `app/api/v1/lessons.py` | Passes user's country to orchestrator from user profile |

---

## Testing Recommendations

1. **Level Comparison Test**: Generate lessons on the same topic at all 4 levels
2. **Duration Test**: Generate lessons at 15, 30, 60, and 90 minutes
3. **Localization Test**: Generate "Contract Law" for India vs. US users
4. **Universal Topic Test**: Generate "Photosynthesis" and verify global accessibility
5. **Vocabulary Analysis**: Verify language complexity matches level
6. **Question Quality Review**: Assess scenario relevance and option quality

---

*Document updated: February 7, 2026*
*Version: 2.1 - Country-Based Localization*
