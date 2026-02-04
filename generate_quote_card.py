#!/usr/bin/env python3
"""
Quick script to generate a quote card from the kombucha quotes collection.
"""

import sys
from pathlib import Path
from src.quote_generator import QuoteGenerator
from src.image_processor import ImageProcessor
from datetime import datetime

def main():
    """Generate a quote card."""
    if len(sys.argv) > 1:
        # Use provided quote
        quote_text = " ".join(sys.argv[1:])
        author = "Real Health Kombucha"
    else:
        # Use random quote
        generator = QuoteGenerator()
        
        # Show available categories
        print("Available categories:")
        categories = generator.get_all_categories()
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        
        # Get random quote
        quote_text = generator.get_random_quote()
        author = "Real Health Kombucha"
        
        print(f"\nSelected quote: {quote_text}")
    
    # Generate quote card
    processor = ImageProcessor()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(__file__).parent / 'output' / 'feed_posts' / f'quote_{timestamp}.jpg'
    
    print(f"\nGenerating quote card...")
    result_path = processor.create_quote_card(
        quote=quote_text,
        author=author,
        output_path=output_path
    )
    
    print(f"✓ Quote card created: {result_path}")
    print(f"\nReady to post on Instagram!")

if __name__ == '__main__':
    main()
