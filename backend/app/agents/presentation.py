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
    
    def _summarize_to_bullets(self, text: str, max_bullets: int = 6) -> List[str]:
        """Convert text to bullet points (max 6 by default)"""
        sentences = self._split_into_sentences(text)
        return sentences[:max_bullets]
    
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
        
        # Add mascot if available
        if self.mascot_path.exists():
            slide.shapes.add_picture(
                str(self.mascot_path),
                left=Inches(3.8),
                top=Inches(0.6),
                height=Inches(2.8)
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
        p2 = tf.add_paragraph()
        p2.text = f"Level: {level}  |  Duration: {duration} minutes"
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
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = section.get("title", "Untitled Section")
            
            body = slide.shapes.placeholders[1].text_frame
            body.clear()
            
            content = section.get("content", "")
            bullets = self._summarize_to_bullets(content, 6)
            
            for i, bullet in enumerate(bullets):
                p = body.paragraphs[0] if i == 0 else body.add_paragraph()
                p.text = bullet
                p.font.size = Pt(22)
                p.level = 0
                p.space_after = Pt(12)
            
            # Footer
            footer = slide.shapes.add_textbox(
                Inches(6.2), Inches(6.9), Inches(3.3), Inches(0.4)
            )
            ft = footer.text_frame
            fp = ft.paragraphs[0]
            fp.text = "🧞 Built by passionate agents of TeachGenie.ai"
            fp.font.size = Pt(16)
            fp.alignment = PP_ALIGN.RIGHT
        
        # ---------- KEY TAKEAWAYS SLIDE ----------
        if takeaways:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = "Key Takeaways"
            
            body = slide.shapes.placeholders[1].text_frame
            body.clear()
            
            for i, takeaway in enumerate(takeaways[:6]):
                p = body.paragraphs[0] if i == 0 else body.add_paragraph()
                p.text = takeaway
                p.font.size = Pt(22)
                p.space_after = Pt(12)
        
        # Save PPT
        safe_filename = topic.replace(" ", "_").replace("/", "_")
        ppt_path = self.output_dir / f"{safe_filename}.pptx"
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
            
            # Run PDF generation in executor to avoid blocking
            pdf_path = await asyncio.to_thread(
                self._generate_pdf_sync,
                topic, sections, takeaways
            )
            
            logger.info(f"PDF generated successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def _generate_pdf_sync(
        self,
        topic: str,
        sections: List[Dict[str, Any]],
        takeaways: Optional[List[str]]
    ) -> Path:
        """Synchronous PDF generation (called in thread executor)"""
        pdf = FPDF()
        pdf.set_auto_page_break(True, 15)
        pdf.add_page()
        
        # Add Unicode-safe fonts if available, otherwise use built-in
        font_available = False
        if self.font_regular.exists() and self.font_bold.exists():
            try:
                pdf.add_font("DejaVu", "", str(self.font_regular), uni=True)
                pdf.add_font("DejaVu", "B", str(self.font_bold), uni=True)
                font_name = "DejaVu"
                font_available = True
                logger.info("Using DejaVu font for PDF")
            except Exception as e:
                logger.warning(f"Failed to load DejaVu font: {e}. Using default font.")
                font_name = "Arial"
        else:
            logger.info("DejaVu fonts not found, using Arial")
            font_name = "Arial"
        
        usable_width = pdf.w - pdf.l_margin - pdf.r_margin
        
        # Title
        pdf.set_font(font_name, "B", 18)
        pdf.multi_cell(usable_width, 10, topic)
        pdf.ln(4)
        
        # Content sections
        for section in sections:
            pdf.set_font(font_name, "B", 14)
            pdf.multi_cell(usable_width, 8, section.get("title", "Untitled"))
            pdf.ln(1)
            
            pdf.set_font(font_name, "", 12)
            content = section.get("content", "")
            bullets = self._summarize_to_bullets(content, 6)
            
            for bullet in bullets:
                wrapped = textwrap.wrap(bullet, 95)
                for line in wrapped:
                    pdf.multi_cell(usable_width, 7, f"- {line}")
                pdf.ln(1)
        
        # Key takeaways
        if takeaways:
            pdf.add_page()
            pdf.set_font(font_name, "B", 16)
            pdf.multi_cell(usable_width, 10, "Key Takeaways")
            pdf.ln(2)
            
            pdf.set_font(font_name, "", 12)
            for takeaway in takeaways[:6]:
                pdf.multi_cell(usable_width, 7, f"- {takeaway}")
                pdf.ln(1)
        
        # Save PDF
        safe_filename = topic.replace(" ", "_").replace("/", "_")
        pdf_path = self.output_dir / f"{safe_filename}.pdf"
        pdf.output(str(pdf_path))
        
        return pdf_path
    
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
