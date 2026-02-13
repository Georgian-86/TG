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

class BrandPDF(FPDF):
    def header(self):
        # Draw border (A4 size: 210x297mm)
        # Rect(x, y, w, h, style)
        self.set_draw_color(79, 70, 229) # Indigo-600
        self.set_line_width(0.5)
        self.rect(5, 5, 200, 287) # 5mm margin box
        
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Powered by TeachGenie.ai | Page ' + str(self.page_no()), 0, 0, 'C')

def generate_pdf_logic(
    topic: str,
    sections: List[Dict[str, Any]],
    takeaways: Optional[List[str]] = None,
    quiz: Optional[Dict[str, Any]] = None
) -> str:
    """Generate PDF logic decoupled from Celery."""
    logger.info(f"Generating PDF for: {topic}")
    
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        pdf = BrandPDF()
        pdf.set_auto_page_break(True, margin=20)
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
            if isinstance(text, dict):
                text = text.get("text", text.get("content", text.get("description", str(text))))
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

        # Helper for bullets (simple split)
        def get_sentences(text):
            text = clean_text(text)
            parts = re.split(r"(?<=[.!?])\s+", text)
            return [p for p in parts if len(p) > 20]

        # Helper to extract subsections (Same as PPT)
        def extract_content_structure(content):
            results = []
            if isinstance(content, dict):
                if "text" in content or "content" in content or "description" in content:
                    text = content.get("text", content.get("content", content.get("description", "")))
                    bullets = get_sentences(text)
                    if bullets: results.append((None, bullets))
                else:
                    for key, value in content.items():
                        subtitle = key.replace("_", " ").title()
                        text = value
                        if isinstance(value, dict):
                            text = value.get("text", value.get("content", ""))
                        elif isinstance(value, list):
                            text = " ".join(str(x) for x in value)
                        bullets = get_sentences(str(text))
                        if bullets: results.append((subtitle, bullets))
            elif isinstance(content, list):
                text = " ".join(str(x) for x in content)
                bullets = get_sentences(text)
                if bullets: results.append((None, bullets))
            else:
                bullets = get_sentences(str(content))
                if bullets: results.append((None, bullets))
            return results

        # Usable width calculation (A4 is 210mm wide)
        # Margins are handled by set_l_margin/set_r_margin (default 1cm = 10mm)
        # Set margins to work within the border (5mm border + 5mm padding)
        pdf.set_left_margin(12)
        pdf.set_right_margin(12)
        usable_width = 210 - 24 # 186mm
        
        # --- TITLE PAGE ---
        mascot_path = Path("assets/TechGenieMascot.png")
        if mascot_path.exists():
            mascot_x = (210 - 50) / 2
            pdf.image(str(mascot_path), x=mascot_x, y=40, w=50)
            pdf.ln(70)
        else:
            pdf.ln(10)
        
        pdf.set_font(font_name, "B", 24)
        pdf.multi_cell(0, 10, clean_text(topic), align='C')
        pdf.ln(10)
        
        pdf.add_page()
        
        # --- SECTIONS ---
        for section in sections:
            pdf.set_font(font_name, "B", 16)
            pdf.set_text_color(79, 70, 229) # Indigo header
            pdf.set_x(pdf.l_margin)  # Reset X position
            pdf.multi_cell(0, 8, clean_text(section.get("title", "Untitled")))
            pdf.ln(2)
            
            structured = extract_content_structure(section.get("content", ""))
            
            for subtitle, bullets in structured:
                if subtitle:
                    pdf.set_font(font_name, "B", 13)
                    pdf.set_text_color(50, 50, 50)
                    pdf.set_x(pdf.l_margin)  # Reset X position
                    pdf.multi_cell(0, 7, subtitle)
                
                pdf.set_font(font_name, "", 11)
                pdf.set_text_color(0, 0, 0)
                
                for bullet in bullets:
                    # Multi_cell handles wrapping automatically
                    # Use a bullet char with proper indentation
                    left_margin = pdf.l_margin
                    pdf.set_x(left_margin + 5)  # Indent 5mm from left margin
                    # Calculate available width for multi_cell
                    available_width = pdf.w - pdf.l_margin - pdf.r_margin - 5
                    pdf.multi_cell(available_width, 6, f"- {bullet}")
                    pdf.ln(1)
            
            pdf.ln(3)
        
        # --- TAKEAWAYS ---
        if takeaways:
            pdf.add_page()
            pdf.set_font(font_name, "B", 18)
            pdf.set_text_color(79, 70, 229)
            pdf.set_x(pdf.l_margin)  # Reset X position
            pdf.multi_cell(0, 10, "Key Takeaways")
            pdf.ln(3)
            
            pdf.set_font(font_name, "", 11)
            pdf.set_text_color(0, 0, 0)
            
            for takeaway in takeaways[:8]:
                clean_item = ""
                if isinstance(takeaway, dict):
                    title = takeaway.get("title", "Key Idea")
                    desc = takeaway.get("description", "")
                    clean_item = f"{title}: {desc}"
                else:
                    clean_item = str(takeaway)
                    
                left_margin = pdf.l_margin
                pdf.set_x(left_margin + 5)  # Indent 5mm from left margin
                available_width = pdf.w - pdf.l_margin - pdf.r_margin - 5
                pdf.multi_cell(available_width, 7, f"- {clean_text(clean_item)}")
                pdf.ln(2)

        # --- QUIZ ---
        if quiz and isinstance(quiz, dict) and "questions" in quiz:
            questions = quiz.get("questions", [])
            if questions:
                pdf.add_page()
                pdf.set_font(font_name, "B", 18)
                pdf.set_text_color(79, 70, 229)
                pdf.set_x(pdf.l_margin)  # Reset X position
                pdf.multi_cell(0, 10, "Knowledge Check")
                pdf.ln(3)
                
                for idx, q in enumerate(questions):
                    # Scenario
                    pdf.set_font(font_name, "I", 11)
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_x(pdf.l_margin)  # Reset X position
                    pdf.multi_cell(0, 6, f"Scenario {idx+1}: {clean_text(q.get('scenario', ''))}")
                    pdf.ln(2)
                    
                    # Question
                    pdf.set_font(font_name, "B", 11)
                    pdf.set_x(pdf.l_margin)  # Reset X position
                    pdf.multi_cell(0, 6, f"Q: {clean_text(q.get('question', ''))}")
                    
                    # Options
                    pdf.set_font(font_name, "", 10)
                    options = q.get("options", {})
                    for opt_key in ["A", "B", "C", "D"]:
                        if opt_key in options:
                            # Use proper indentation for options
                            left_margin = pdf.l_margin
                            pdf.set_x(left_margin + 5)
                            option_text = f"{opt_key}) {clean_text(str(options[opt_key]))}"
                            available_width = pdf.w - pdf.l_margin - pdf.r_margin - 5
                            pdf.multi_cell(available_width, 6, option_text)
                            
                    pdf.ln(4)
                
                # Answer Key
                pdf.add_page()
                pdf.set_font(font_name, "B", 14)
                pdf.set_text_color(79, 70, 229)
                pdf.set_x(pdf.l_margin)  # Reset X position
                pdf.multi_cell(0, 10, "Answer Key")
                pdf.set_font(font_name, "", 10)
                pdf.set_text_color(0, 0, 0)
                
                for idx, q in enumerate(questions):
                    ans = q.get("correct_option", "?")
                    exp = clean_text(q.get("explanation", ""))
                    pdf.set_x(pdf.l_margin)  # Reset X position for each answer
                    available_width = pdf.w - pdf.l_margin - pdf.r_margin
                    pdf.multi_cell(available_width, 6, f"{idx+1}. {ans} - {exp}")

        # Save
        safe_filename = topic.replace(" ", "_").replace("/", "_")
        pdf_path = OUTPUT_DIR / f"TG-{safe_filename}.pdf"
        pdf.output(str(pdf_path))
        
        return str(pdf_path)
    
    except Exception as e:
        logger.error(f"Generate PDF Logic failed: {e}")
        raise e
