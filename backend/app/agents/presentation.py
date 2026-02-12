"""
Presentation Agent
Generates PowerPoint and PDF files from lesson content
Async class-based implementation with BaseAgent inheritance
"""
from typing import Dict, Any, List, Optional
import asyncio
import os
import re
import textwrap
from pathlib import Path
import logging

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from fpdf import FPDF

from app.agents.base import BaseAgent
from app.config import settings

logger = logging.getLogger(__name__)

# =========================================================
# CONFIGURATION
# =========================================================

OUTPUT_DIR = Path("outputs")
MASCOT_PATH = Path("assets/TechGenieMascot.png")
FONT_REGULAR = Path("assets/fonts/DejaVuSans.ttf")
FONT_BOLD = Path("assets/fonts/DejaVuSans-Bold.ttf")


class PresentationAgent(BaseAgent):
    """Generates PowerPoint and PDF presentation files from lesson content"""
    
    def __init__(self):
        super().__init__()
        self.output_dir = OUTPUT_DIR
        self.mascot_path = MASCOT_PATH
        self.font_regular = FONT_REGULAR
        self.font_bold = FONT_BOLD
        
    def _ensure_dirs(self):
        """Create output directory if it doesn't exist"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _clean_text(self, text: str) -> str:
        """Normalize text safely for PPT/PDF (handles smart quotes)"""
        if not text:
            return ""
        
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
            
        # Replace smart quotes and other common unicode characters
        replacements = {
            '\u2018': "'", '\u2019': "'",  # Smart single quotes
            '\u201c': '"', '\u201d': '"',  # Smart double quotes
            '\u2013': '-', '\u2014': '-',  # En/Em dashes
            '\u2026': '...',               # Ellipsis
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
            
        # If fonts aren't available, force ASCII to prevent crashes
        if not self.font_regular.exists():
            text = text.encode('ascii', 'ignore').decode('ascii')
            
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for bullet points"""
        text = self._clean_text(text)
        parts = re.split(r"(?<=[.!?])\s+", text)
        return [p for p in parts if len(p) > 25]
    
    def _summarize_to_bullets(self, content, max_bullets: int = 6) -> List[str]:
        """Convert text or dict to bullet points (max 6 by default)"""
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
        
        sentences = self._split_into_sentences(text)
        return sentences[:max_bullets]
    
    def _extract_all_content_bullets(self, content) -> List[str]:
        """Extract ALL content from nested subsections as bullet points (no limit)"""
        bullets = []
        
        if isinstance(content, dict):
            # Handle nested subsections structure
            if "text" in content or "content" in content or "description" in content:
                # Standard dict with known keys
                text = content.get("text", content.get("content", content.get("description", "")))
                bullets.extend(self._split_into_sentences(text))
            else:
                # It's a subsections dict - extract each subsection
                for subsection_name, subsection_content in content.items():
                    if isinstance(subsection_content, str) and len(subsection_content) > 20:
                        # Split each subsection into sentences
                        sentences = self._split_into_sentences(subsection_content)
                        bullets.extend(sentences)
                    elif isinstance(subsection_content, dict):
                        # Handle nested dicts
                        nested_text = subsection_content.get("text", subsection_content.get("content", subsection_content.get("description", "")))
                        if nested_text:
                            bullets.extend(self._split_into_sentences(nested_text))
        elif isinstance(content, list):
            # Handle list of items
            for item in content:
                if isinstance(item, str):
                    bullets.extend(self._split_into_sentences(item))
                elif isinstance(item, dict):
                    text = item.get("text", item.get("content", item.get("description", "")))
                    if text:
                        bullets.extend(self._split_into_sentences(text))
        else:
            # Plain string
            text = str(content) if content else ""
            bullets.extend(self._split_into_sentences(text))
        
        # Filter out very short bullets (dynamic pagination handles length)
        return [b for b in bullets if len(b) > 25]
    
    async def _build_ppt(
        self,
        topic: str,
        level: str,
        duration: int,
        sections: List[Dict[str, Any]],
        takeaways: Optional[List[str]] = None
    ) -> Path:
        """
        Build PowerPoint presentation
        
        Args:
            topic: Lesson topic
            level: Educational level
            duration: Lesson duration in minutes
            sections: List of lesson sections with title and content
            takeaways: Optional list of key takeaways
            
        Returns:
            Path to generated PPT file
        """
        logger.info(f"Building PPT for: {topic}")
        
        try:
            self._ensure_dirs()
            
            # Run PPT generation in executor to avoid blocking
            ppt_path = await asyncio.to_thread(
                self._generate_ppt_sync,
                topic, level, duration, sections, takeaways
            )
            
            logger.info(f"PPT generated successfully: {ppt_path}")
            return ppt_path
            
        except Exception as e:
            logger.error(f"PPT generation failed: {e}")
            raise
    
    def _generate_ppt_sync(
        self,
        topic: str,
        level: str,
        duration: int,
        sections: List[Dict[str, Any]],
        takeaways: Optional[List[str]]
    ) -> Path:
        """Synchronous PPT generation (called in thread executor)"""
        prs = Presentation()
        
        # ---------- TITLE SLIDE ----------
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Add mascot at center if available
        if self.mascot_path.exists():
            slide.shapes.add_picture(
                str(self.mascot_path),
                left=Inches(3.5),  # Centered horizontally (10" slide - ~3" mascot width / 2)
                top=Inches(1.2),   # Centered vertically with more top spacing
                height=Inches(2.5)
            )
        
        # Title text box
        title_box = slide.shapes.add_textbox(
            Inches(1), Inches(3.4), Inches(8), Inches(2)
        )
        tf = title_box.text_frame
        tf.clear()
        
        # Main title
        p = tf.paragraphs[0]
        p.text = topic
        p.font.size = Pt(36)
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER
        
        # Subtitle (level and duration)
        # Extract clean level value (remove enum prefix like "LessonLevel.")
        clean_level = str(level).replace("LessonLevel.", "").replace("_", " ").title()
        p2 = tf.add_paragraph()
        p2.text = f"Level: {clean_level}  |  Duration: {duration} minutes"
        p2.font.size = Pt(22)
        p2.alignment = PP_ALIGN.CENTER
        
        # Credits
        p3 = tf.add_paragraph()
        p3.text = "Powered by TeachGenie.ai"
        p3.font.size = Pt(24)
        p3.font.bold = True
        p3.alignment = PP_ALIGN.CENTER
        
        # ---------- CONTENT SLIDES ----------
        for section in sections:
            section_title = section.get("title", "Untitled Section")
            content = section.get("content", "")
            
            # Extract ALL content
            bullets = self._extract_all_content_bullets(content)
            
            if not bullets:
                continue
            
            # DYNAMIC PAGINATION: Calculate height per bullet and create slides as needed
            # Slide dimensions and limits (CONSERVATIVE VALUES to prevent overflow)
            SLIDE_HEIGHT_INCHES = 7.5  # Standard slide height
            USABLE_HEIGHT_INCHES = 4.8  # More conservative after title and footer (was 5.5)
            FONT_SIZE_PT = 16
            LINE_HEIGHT_INCHES = 0.28  # More realistic height per line (was 0.25)
            CHARS_PER_LINE = 85  # More conservative wrapping estimate (was 100)
            
            def estimate_bullet_height(bullet_text):
                """Estimate the height in inches a bullet will take"""
                # Calculate number of lines based on text length
                num_lines = max(1, (len(bullet_text) + CHARS_PER_LINE - 1) // CHARS_PER_LINE)
                # Add space for bullet marker and spacing (more generous)
                return num_lines * LINE_HEIGHT_INCHES + 0.2  # Increased from 0.15
            
            # Group bullets into slides dynamically
            slide_groups = []
            current_slide_bullets = []
            current_height = 0
            
            for bullet in bullets:
                bullet_height = estimate_bullet_height(bullet)
                
                # Check if adding this bullet exceeds slide capacity
                if current_height + bullet_height > USABLE_HEIGHT_INCHES and current_slide_bullets:
                    # Save current slide and start new one
                    slide_groups.append(current_slide_bullets)
                    current_slide_bullets = [bullet]
                    current_height = bullet_height
                else:
                    # Add to current slide
                    current_slide_bullets.append(bullet)
                    current_height += bullet_height
            
            # Add last group if not empty
            if current_slide_bullets:
                slide_groups.append(current_slide_bullets)
            
            # Create slides for each group
            for page_num, slide_bullets in enumerate(slide_groups):
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                
                # Add page indicator if content spans multiple slides
                if len(slide_groups) > 1:
                    page_indicator = f" ({page_num + 1}/{len(slide_groups)})"
                    slide.shapes.title.text = section_title + page_indicator
                else:
                    slide.shapes.title.text = section_title
                
                body = slide.shapes.placeholders[1].text_frame
                body.clear()
                
                # Add bullets for this slide
                for i, bullet in enumerate(slide_bullets):
                    p = body.paragraphs[0] if i == 0 else body.add_paragraph()
                    p.text = bullet
                    p.font.size = Pt(16)
                    p.level = 0
                    p.space_after = Pt(8)
                
                # Footer
                footer = slide.shapes.add_textbox(
                    Inches(6.2), Inches(6.9), Inches(3.3), Inches(0.4)
                )
                ft = footer.text_frame
                fp = ft.paragraphs[0]
                fp.text = "🧞 Built by passionate agents of TeachGenie.ai"
                fp.font.size = Pt(14)
                fp.alignment = PP_ALIGN.RIGHT
        
        # ---------- KEY TAKEAWAYS SLIDE ----------
        if takeaways:
            # Ensure takeaways is a list to prevent "unhashable type: slice" error
            if not isinstance(takeaways, list):
                takeaways = []
                
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = "Key Takeaways"
            
            body = slide.shapes.placeholders[1].text_frame
            body.clear()
            
            for i, takeaway in enumerate(takeaways[:6]):
                p = body.paragraphs[0] if i == 0 else body.add_paragraph()
                
                # Handle structured dicts (new format) or legacy strings
                if isinstance(takeaway, dict):
                    title = takeaway.get("title", "Key Idea")
                    desc = takeaway.get("description", "")
                    p.text = f"{title}: {desc}"
                    # Make title bold manually if needed, or just let it be single line
                    # For simplicity in PPT, just concat
                else:
                    p.text = str(takeaway)
                    
                p.font.size = Pt(16)  # Match content slides (was 22)
                p.space_after = Pt(8)  # Match content slides (was 12)
            
            # Add footer watermark (matching content slides)
            footer = slide.shapes.add_textbox(
                Inches(6.2), Inches(6.9), Inches(3.3), Inches(0.4)
            )
            ft = footer.text_frame
            fp = ft.paragraphs[0]
            fp.text = "🧞 Built by passionate agents of TeachGenie.ai"
            fp.font.size = Pt(14)
            fp.alignment = PP_ALIGN.RIGHT
        
        # Save PPT with TG- prefix
        safe_filename = topic.replace(" ", "_").replace("/", "_")
        ppt_path = self.output_dir / f"TG-{safe_filename}.pptx"
        prs.save(str(ppt_path))
        
        return ppt_path
    
    async def _build_pdf(
        self,
        topic: str,
        sections: List[Dict[str, Any]],
        takeaways: Optional[List[str]] = None
    ) -> Path:
        """
        Build PDF document
        
        Args:
            topic: Lesson topic
            sections: List of lesson sections
            takeaways: Optional list of key takeaways
            
        Returns:
            Path to generated PDF file
        """
        logger.info(f"Building PDF for: {topic}")
        
        try:
            self._ensure_dirs()
            from app.utils.pdf_generator import generate_pdf_logic
            
            # Using synchronous execution via thread pool (bypass Celery broker)
            # This allows PDF generation to work even if Redis is not running
            logger.info("Generating PDF locally via thread pool (Celery bypassed)...")
            pdf_path_str = await asyncio.to_thread(
                generate_pdf_logic, 
                topic, sections, takeaways
            )
            
            pdf_path = Path(pdf_path_str)
            logger.info(f"PDF generated successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    # _generate_pdf_sync removed (moved to Celery task)
    
    async def run(
        self,
        topic: str,
        level: str,
        duration: int,
        sections: List[Dict[str, Any]],
        takeaways: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate both PPT and PDF presentations
        
        Args:
            topic: Lesson topic
            level: Educational level
            duration: Lesson duration in minutes
            sections: Lesson sections with content
            takeaways: Optional key takeaways
            
        Returns:
            Dictionary with ppt_path and pdf_path
        """
        logger.info(f"Generating presentations for: {topic}")
        
        try:
            # Generate PPT and PDF in parallel for speed
            ppt_path, pdf_path = await asyncio.gather(
                self._build_ppt(topic, level, duration, sections, takeaways),
                self._build_pdf(topic, sections, takeaways)
            )
            
            return {
                "ppt_path": str(ppt_path),
                "pdf_path": str(pdf_path)
            }
            
        except Exception as e:
            logger.error(f"Presentation generation failed: {e}")
            raise
