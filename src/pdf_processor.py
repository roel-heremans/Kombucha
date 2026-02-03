"""
PDF Processor Module

Extracts text content from PDFs in theme directories for use in content generation.
"""

import pdfplumber
from pathlib import Path
from typing import List, Dict, Optional
import re


class PDFProcessor:
    """Process PDF files to extract text content."""
    
    def __init__(self, assets_base_path: Optional[Path] = None):
        """
        Initialize PDF processor.
        
        Args:
            assets_base_path: Base path to assets directory. If None, uses default.
        """
        if assets_base_path is None:
            assets_base_path = Path(__file__).parent.parent / 'assets'
        self.assets_base_path = assets_base_path
    
    def find_pdfs(self, theme_name: str) -> List[Path]:
        """
        Find all PDF files in a theme directory.
        
        Args:
            theme_name: Name of the theme directory.
        
        Returns:
            List of PDF file paths.
        """
        theme_path = self.assets_base_path / theme_name / 'pdfs'
        if not theme_path.exists():
            return []
        
        pdf_files = list(theme_path.glob('*.pdf'))
        return pdf_files
    
    def extract_text(self, pdf_path: Path, max_pages: Optional[int] = None) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file.
            max_pages: Maximum number of pages to extract. If None, extracts all.
        
        Returns:
            Extracted text content.
        """
        text_content = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages_to_process = len(pdf.pages)
                if max_pages:
                    pages_to_process = min(pages_to_process, max_pages)
                
                for i in range(pages_to_process):
                    page = pdf.pages[i]
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
        
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
        
        return "\n\n".join(text_content)
    
    def extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """
        Extract key points from text using simple heuristics.
        
        Args:
            text: Text content to analyze.
            max_points: Maximum number of key points to extract.
        
        Returns:
            List of key points.
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Simple heuristic: prioritize sentences with keywords
        keywords = [
            'kombucha', 'benefit', 'health', 'probiotic', 'antioxidant',
            'research', 'study', 'scientific', 'improve', 'reduce',
            'digest', 'immune', 'gut', 'bacteria'
        ]
        
        scored_sentences = []
        for sentence in sentences:
            score = sum(1 for keyword in keywords if keyword.lower() in sentence.lower())
            if score > 0:
                scored_sentences.append((score, sentence))
        
        # Sort by score and take top sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        key_points = [sentence for _, sentence in scored_sentences[:max_points]]
        
        # If not enough key points, add more sentences
        if len(key_points) < max_points:
            remaining = [s for s in sentences if s not in key_points]
            key_points.extend(remaining[:max_points - len(key_points)])
        
        return key_points
    
    def process_theme_pdfs(self, theme_name: str, max_pages_per_pdf: Optional[int] = 10) -> Dict[str, str]:
        """
        Process all PDFs in a theme directory.
        
        Args:
            theme_name: Name of the theme directory.
            max_pages_per_pdf: Maximum pages to extract from each PDF.
        
        Returns:
            Dictionary mapping PDF filenames to extracted text.
        """
        pdf_files = self.find_pdfs(theme_name)
        results = {}
        
        for pdf_path in pdf_files:
            print(f"Processing PDF: {pdf_path.name}")
            text = self.extract_text(pdf_path, max_pages=max_pages_per_pdf)
            if text:
                results[pdf_path.name] = text
        
        return results
    
    def get_combined_text(self, theme_name: str, max_pages_per_pdf: Optional[int] = 10) -> str:
        """
        Get combined text from all PDFs in a theme.
        
        Args:
            theme_name: Name of the theme directory.
            max_pages_per_pdf: Maximum pages to extract from each PDF.
        
        Returns:
            Combined text from all PDFs.
        """
        pdf_texts = self.process_theme_pdfs(theme_name, max_pages_per_pdf)
        return "\n\n---\n\n".join(pdf_texts.values())
    
    def get_summary(self, theme_name: str, max_pages_per_pdf: Optional[int] = 10) -> Dict[str, any]:
        """
        Get a summary of PDF content for a theme.
        
        Args:
            theme_name: Name of the theme directory.
            max_pages_per_pdf: Maximum pages to extract from each PDF.
        
        Returns:
            Dictionary with summary information.
        """
        combined_text = self.get_combined_text(theme_name, max_pages_per_pdf)
        key_points = self.extract_key_points(combined_text)
        
        return {
            'full_text': combined_text,
            'key_points': key_points,
            'word_count': len(combined_text.split()),
            'character_count': len(combined_text)
        }


def main():
    """Test function."""
    processor = PDFProcessor()
    
    # Test with kombucha_benefits theme
    theme = 'kombucha_benefits'
    pdfs = processor.find_pdfs(theme)
    
    if pdfs:
        print(f"Found {len(pdfs)} PDF(s) in {theme}:")
        for pdf in pdfs:
            print(f"  - {pdf.name}")
        
        # Process first PDF
        if pdfs:
            text = processor.extract_text(pdfs[0], max_pages=2)
            print(f"\nExtracted text (first 500 chars):\n{text[:500]}...")
    else:
        print(f"No PDFs found in {theme} theme.")


if __name__ == '__main__':
    main()
