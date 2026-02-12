"""
Resources Agent
Decides pedagogically appropriate learning resources and generates safe links.
"""
import urllib.parse
import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


# --------------------------------------------------
# SAFE LINK GENERATOR (UTILITY, NOT AGENT)
# --------------------------------------------------
def generate_safe_link(platform: str, search_query: str) -> str:
    """Generate a safe search URL for a given platform"""
    query = urllib.parse.quote_plus(search_query)

    platforms = {
        "YouTube": f"https://www.youtube.com/results?search_query={query}",
        "Google Scholar": f"https://scholar.google.com/scholar?q={query}",
        "Wikipedia": f"https://en.wikipedia.org/wiki/{query.replace('+', '_')}",
        "Medium": f"https://medium.com/search?q={query}",
        "Coursera": f"https://www.coursera.org/search?query={query}",
        "edX": f"https://www.edx.org/search?q={query}",
        "NPTEL": f"https://nptel.ac.in/courses?searchText={query}",
    }

    return platforms.get(platform, f"https://www.google.com/search?q={query}")


class ResourcesAgent(BaseAgent):
    """Resources Agent Class for LLM interaction"""
    pass


# --------------------------------------------------
# RESOURCES AGENT (REASONING AGENT)
# --------------------------------------------------
async def resources_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent role:
    Decide pedagogically appropriate learning resources
    based on topic and learner level.
    """
    agent = ResourcesAgent()
    topic = state.get("topic")
    level = state.get("level")

    if not topic:
        state["resources"] = {}
        return state

    system_prompt = """
You are an educational resources curator agent.

Your task:
- Recommend learning resources for a lesson topic
- Adapt choices to learner level
- Do NOT generate URLs
- Output ONLY valid JSON
- Categorize resources into:
  web_pages, videos, research_articles, blogs, others

Each resource must have:
- title
- platform (e.g., YouTube, Wikipedia, Google Scholar, Medium, Coursera, edX, NPTEL)
- search_query (what the learner should search)
"""

    user_prompt = f"""
Lesson Topic: {topic}
Learner Level: {level}

Generate 1–2 high-quality resources per category.
If a category is not suitable, return an empty list.
"""

    try:
        # Use BaseAgent for consistent API handling
        resources = await agent.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
    except Exception as e:
        logger.error(f"Resources Agent LLM call failed: {e}")
        resources = {}

    # Safety: enforce structure
    structured_resources = {
        "web_pages": resources.get("web_pages", []),
        "videos": resources.get("videos", []),
        "research_articles": resources.get("research_articles", []),
        "blogs": resources.get("blogs", []),
        "others": resources.get("others", [])
    }
    
    # Post-process to add URLs using safe link generator
    # (Optional enhancement to match the intent of 'generate_safe_link' usage)
    for category in structured_resources:
        for item in structured_resources[category]:
            if "url" not in item:
                item["url"] = generate_safe_link(item.get("platform", ""), item.get("search_query", item.get("title", "")))

    state["resources"] = structured_resources

    return state
