import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import textwrap
import re

from app.worker import celery_app
from fpdf import FPDF
from app.config import settings

logger = logging.getLogger(__name__)

# Constants duplicated from presentation.py to be standalone
OUTPUT_DIR = Path("outputs")
FONT_REGULAR = Path("assets/fonts/DejaVuSans.ttf")
FONT_BOLD = Path("assets/fonts/DejaVuSans-Bold.ttf")

@celery_app.task(name="generate_pdf_task")
def generate_pdf_task(topic: str, sections: List[Dict[str, Any]], takeaways: Optional[List[str]] = None) -> str:
    """
    Celery task to generate PDF.
    Delegates to decoupled utility logic.
    """
    logger.info(f"Worker generating PDF for: {topic}")
    from app.utils.pdf_generator import generate_pdf_logic
    
    try:
        return generate_pdf_logic(topic, sections, takeaways)
    except Exception as e:
        logger.error(f"Generate PDF Task failed: {e}")
        raise e
