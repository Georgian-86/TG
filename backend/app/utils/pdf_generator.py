import logging
import re
import textwrap
from pathlib import Path
from typing import List, Dict, Any, Optional
from fpdf import FPDF

logger = logging.getLogger(__name__)

# Constants
OUTPUT_DIR = Path("outputs")
FONT_REGULAR = Path("assets/fonts/DejaVuSans.ttf")
FONT_BOLD = Path("assets/fonts/DejaVuSans-Bold.ttf")

def generate_pdf_logic(topic: str, sections: List[Dict[str, Any]], takeaways: Optional[List[str]] = None) -> str:
    """
    Generate PDF logic decoupled from Celery.
    Returns the string path of the generated file.
    """
    logger.info(f"Generating PDF for: {topic}")
    
    try:
        # Ensure output dir exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        pdf = FPDF()
        pdf.set_auto_page_break(True, 15)
        pdf.add_page()
        
        # Font setup
        font_name = "Arial"
        if FONT_REGULAR.exists() and FONT_BOLD.exists():
            try:
                pdf.add_font("DejaVu", "", str(FONT_REGULAR), uni=True)
                pdf.add_font("DejaVu", "B", str(FONT_BOLD), uni=True)
                font_name = "DejaVu"
            except Exception:
                pass

        # Helper to clean text
        def clean_text(text):
            if not text: return ""
            
            # Handle dict content (new structure)
            if isinstance(text, dict):
                # Try to extract text from dict
                if "text" in text:
                    text = text["text"]
                elif "content" in text:
                    text = text["content"]
                elif "description" in text:
                    text = text["description"]
                else:
                    # Convert dict to string representation
                    text = str(text)
            
            # Convert to string if not already
            text = str(text)
            
            replacements = {
                '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
                '\u2013': '-', '\u2014': '-', '\u2026': '...'
            }
            for k, v in replacements.items():
                text = text.replace(k, v)
            if not FONT_REGULAR.exists():
                 text = text.encode('ascii', 'ignore').decode('ascii')
            return re.sub(r"\s+", " ", text).strip()

        # Helper for bullets
        def get_bullets(content):
            # Handle different content structures
            if isinstance(content, dict):
                # NEW: Handle nested subsections structure from Content Agent
                # Example: {"basic_syntax": "text...", "data_types": "text...", ...}
                
                # First check if it's a standard key-value structure
                if "text" in content:
                    text = content["text"]
                elif "content" in content:
                    text = content["content"]
                elif "description" in content:
                    text = content["description"]
                else:
                    # It's a subsections dict - extract all subsection texts
                    subsection_texts = []
                    for key, value in content.items():
                        if isinstance(value, str) and len(value) > 20:  # Extract meaningful text content
                            subsection_texts.append(value)
                        elif isinstance(value, dict):
                            # Handle nested dicts recursively
                            subsection_texts.append(str(value.get("text", value.get("content", value.get("description", "")))))
                    
                    # Join all subsection texts
                    text = " ".join(subsection_texts)
            elif isinstance(content, list):
                # Join list items
                text = " ".join(str(item) for item in content)
            else:
                text = str(content) if content else ""
            
            text = clean_text(text)
            parts = re.split(r"(?<=[.!?])\s+", text)
            sentences = [p for p in parts if len(p) > 25]
            # REMOVED LIMIT: return ALL sentences, not just 6
            return sentences

        usable_width = pdf.w - pdf.l_margin - pdf.r_margin
        
        # Add mascot at center of title page if available
        mascot_path = Path("assets/TechGenieMascot.png")  # Match PPT path
        if mascot_path.exists():
            # Center the mascot horizontally
            # PDF page width is typically ~210mm, mascot width ~50mm
            mascot_x = (pdf.w - 50) / 2  # Center horizontally
            mascot_y = 40  # Position from top
            pdf.image(str(mascot_path), x=mascot_x, y=mascot_y, w=50)
            pdf.ln(70)  # Space after mascot
        else:
            pdf.ln(10)
        
        # Title (centered below mascot)
        pdf.set_font(font_name, "B", 20)
        pdf.cell(0, 10, clean_text(topic), align='C', ln=True)
        pdf.ln(5)
        
        # Add "Powered by TeachGenie.ai" centered
        pdf.set_font(font_name, "I", 12)
        pdf.cell(0, 10, "Powered by TeachGenie.ai", align='C', ln=True)
        pdf.ln(10)
        
        # Start new page for content
        pdf.add_page()
        
        # Content - iterate through all sections
        for section in sections:
            # Use auto page break for overflow handling
            pdf.set_font(font_name, "B", 14)
            pdf.multi_cell(usable_width, 8, clean_text(section.get("title", "Untitled")))
            pdf.ln(1)
            
            pdf.set_font(font_name, "", 12)
            bullets = get_bullets(section.get("content", ""))
            
            for bullet in bullets:
                wrapped = textwrap.wrap(bullet, 95)
                for line in wrapped:
                    pdf.multi_cell(usable_width, 7, f"- {line}")
                pdf.ln(1)
        
        # Takeaways
        if takeaways:
            pdf.add_page()
            pdf.set_font(font_name, "B", 16)
            pdf.multi_cell(usable_width, 10, "Key Takeaways")
            pdf.ln(2)
            pdf.set_font(font_name, "", 12)
            for takeaway in takeaways[:6]:
                if isinstance(takeaway, dict):
                    title = takeaway.get("title", "Key Idea")
                    desc = takeaway.get("description", "")
                    clean_item = f"{title}: {desc}"
                else:
                    clean_item = str(takeaway)
                    
                pdf.multi_cell(usable_width, 7, f"- {clean_text(clean_item)}")
                pdf.ln(1)

        # Save with TG- prefix
        safe_filename = topic.replace(" ", "_").replace("/", "_")
        pdf_path = OUTPUT_DIR / f"TG-{safe_filename}.pdf"
        pdf.output(str(pdf_path))
        
        return str(pdf_path)

    except Exception as e:
        logger.error(f"Generate PDF Logic failed: {e}")
        raise e
