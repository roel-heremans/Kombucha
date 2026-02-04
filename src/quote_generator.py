"""
Quote Generator Module

Utilities for working with kombucha quotes from the quotes collection.
"""

import random
from pathlib import Path
from typing import List, Dict, Optional


class QuoteGenerator:
    """Generate and manage kombucha quotes."""
    
    def __init__(self, quotes_file: Optional[Path] = None):
        """
        Initialize quote generator.
        
        Args:
            quotes_file: Path to quotes.txt file. If None, uses default.
        """
        if quotes_file is None:
            quotes_file = Path(__file__).parent.parent / 'assets' / '03_kombucha_quotes' / 'quotes.txt'
        self.quotes_file = quotes_file
        self.quotes = self._load_quotes()
    
    def _load_quotes(self) -> Dict[str, List[str]]:
        """Load quotes from file."""
        quotes = {}
        current_category = None
        
        if not self.quotes_file.exists():
            return quotes
        
        with open(self.quotes_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Check if it's a category header (## Category Name)
                if line.startswith('##') and not line.startswith('###'):
                    current_category = line.replace('##', '').strip()
                    if current_category not in quotes:
                        quotes[current_category] = []
                # Skip comment lines and category headers
                elif line.startswith('#') or line.startswith('---'):
                    continue
                # Add quote to current category
                elif current_category and line:
                    # Remove surrounding quotes if present
                    quote = line.strip('"').strip("'")
                    if quote and len(quote) > 10:  # Minimum quote length
                        quotes[current_category].append(quote)
        
        return quotes
    
    def get_random_quote(self, category: Optional[str] = None) -> str:
        """
        Get a random quote.
        
        Args:
            category: Optional category to filter by.
        
        Returns:
            Random quote string.
        """
        if category and category in self.quotes:
            quotes_list = self.quotes[category]
        else:
            # Get all quotes
            quotes_list = []
            for cat_quotes in self.quotes.values():
                quotes_list.extend(cat_quotes)
        
        if not quotes_list:
            return "Kombucha: Nature's probiotic powerhouse."
        
        return random.choice(quotes_list)
    
    def get_quotes_by_category(self, category: str) -> List[str]:
        """
        Get all quotes from a specific category.
        
        Args:
            category: Category name.
        
        Returns:
            List of quotes in that category.
        """
        return self.quotes.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get list of all available categories."""
        return list(self.quotes.keys())
    
    def search_quotes(self, keyword: str) -> List[str]:
        """
        Search quotes by keyword.
        
        Args:
            keyword: Keyword to search for.
        
        Returns:
            List of matching quotes.
        """
        keyword_lower = keyword.lower()
        matching_quotes = []
        
        for quotes_list in self.quotes.values():
            for quote in quotes_list:
                if keyword_lower in quote.lower():
                    matching_quotes.append(quote)
        
        return matching_quotes


def main():
    """Test function."""
    generator = QuoteGenerator()
    
    print("Available categories:")
    for category in generator.get_all_categories():
        count = len(generator.get_quotes_by_category(category))
        print(f"  - {category}: {count} quotes")
    
    print("\nRandom quote:")
    print(f"  {generator.get_random_quote()}")
    
    print("\nRandom quote from 'Yoga & Wellness':")
    print(f"  {generator.get_random_quote('Yoga & Wellness Quotes')}")
    
    print("\nSearch for 'probiotic':")
    results = generator.search_quotes('probiotic')
    for quote in results[:3]:
        print(f"  - {quote}")


if __name__ == '__main__':
    main()
