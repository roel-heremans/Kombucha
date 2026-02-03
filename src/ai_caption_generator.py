"""
AI Caption Generator Module

Generates engaging Instagram captions, hashtags, and CTAs using AI from PDF content.
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
from .utils import load_config, get_theme_config


class AICaptionGenerator:
    """Generate Instagram captions using AI."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize AI caption generator.
        
        Args:
            config: Configuration dictionary. If None, loads from file.
        """
        if config is None:
            config = load_config()
        
        self.config = config
        ai_config = config.get('ai', {})
        self.provider = ai_config.get('provider', 'openai').lower()
        self.model = ai_config.get('model', 'gpt-4')
        self.language = ai_config.get('language', 'pt')
        
        # Initialize OpenAI client if using OpenAI
        self.client = None
        if self.provider == 'openai':
            api_key = ai_config.get('api_key') or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not found. AI caption generation will not work.")
    
    def generate_caption(
        self,
        content_text: str,
        theme_name: str,
        content_type: str = 'feed',
        target_audience: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Generate Instagram caption from content text.
        
        Args:
            content_text: Text content from PDFs or other sources.
            theme_name: Name of the theme.
            content_type: Type of content ('feed' or 'reel').
            target_audience: List of target audiences.
        
        Returns:
            Dictionary with caption, hashtags, and CTA.
        """
        if not self.client:
            return self._fallback_caption(content_text, theme_name)
        
        theme_config = get_theme_config(self.config, theme_name)
        hashtags_base = theme_config.get('hashtags', {}).get('base', []) if theme_config else []
        hashtags_custom = theme_config.get('hashtags', {}).get('custom', []) if theme_config else []
        
        if target_audience is None:
            target_audience = theme_config.get('target_audience', []) if theme_config else []
        
        # Build prompt
        prompt = self._build_prompt(
            content_text,
            theme_name,
            content_type,
            target_audience,
            hashtags_base,
            hashtags_custom
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are an expert social media content creator specializing in health and wellness content for Instagram.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            return self._parse_ai_response(result_text, hashtags_base, hashtags_custom)
        
        except Exception as e:
            print(f"Error generating caption with AI: {e}")
            return self._fallback_caption(content_text, theme_name)
    
    def _build_prompt(
        self,
        content_text: str,
        theme_name: str,
        content_type: str,
        target_audience: List[str],
        hashtags_base: List[str],
        hashtags_custom: List[str]
    ) -> str:
        """Build the prompt for AI generation."""
        lang_instruction = "Portuguese" if self.language == 'pt' else "English"
        
        audience_text = " and ".join(target_audience) if target_audience else "general audience"
        
        # Truncate content if too long
        content_preview = content_text[:2000] if len(content_text) > 2000 else content_text
        
        prompt = f"""Create an engaging Instagram {'Reel' if content_type == 'reel' else 'Feed post'} caption in {lang_instruction} for a Kombucha business in Madeira.

Theme: {theme_name}
Target Audience: {audience_text}

Content Context:
{content_preview}

Requirements:
1. Write a captivating caption (2-4 sentences) that highlights key benefits or research findings
2. Make it engaging and suitable for {audience_text}
3. Include relevant hashtags (mix of base and custom hashtags)
4. Add a call-to-action appropriate for the audience

Base hashtags to consider: {', '.join(hashtags_base)}
Custom hashtags to consider: {', '.join(hashtags_custom)}

Format your response as:
CAPTION: [your caption text here]
HASHTAGS: [list of hashtags, one per line]
CTA: [call to action text]

Write in {lang_instruction} language."""
        
        return prompt
    
    def _parse_ai_response(self, response: str, hashtags_base: List[str], hashtags_custom: List[str]) -> Dict[str, str]:
        """Parse AI response into structured format."""
        result = {
            'caption': '',
            'hashtags': [],
            'cta': ''
        }
        
        # Extract caption
        caption_match = response.split('CAPTION:')
        if len(caption_match) > 1:
            caption_part = caption_match[1].split('HASHTAGS:')[0].strip()
            result['caption'] = caption_part
        
        # Extract hashtags
        hashtags_match = response.split('HASHTAGS:')
        if len(hashtags_match) > 1:
            hashtags_part = hashtags_match[1].split('CTA:')[0].strip()
            hashtags_list = [h.strip() for h in hashtags_part.split('\n') if h.strip()]
            # Combine with base hashtags
            result['hashtags'] = hashtags_base + hashtags_custom[:5] + hashtags_list[:10]
        else:
            result['hashtags'] = hashtags_base + hashtags_custom[:5]
        
        # Extract CTA
        cta_match = response.split('CTA:')
        if len(cta_match) > 1:
            result['cta'] = cta_match[1].strip()
        else:
            result['cta'] = "Experimente nosso kombucha hoje! 🍵"
        
        return result
    
    def _fallback_caption(self, content_text: str, theme_name: str) -> Dict[str, str]:
        """Generate a simple fallback caption if AI is not available."""
        # Simple extraction of first sentence
        first_sentence = content_text.split('.')[0][:200] if content_text else "Descubra os benefícios do kombucha!"
        
        return {
            'caption': f"{first_sentence} Descubra mais sobre kombucha em Madeira!",
            'hashtags': ['#kombucha', '#madeira', '#healthy', '#realhealthkombucha'],
            'cta': 'Experimente nosso kombucha hoje! 🍵'
        }
    
    def format_caption_for_instagram(self, caption_data: Dict[str, str]) -> str:
        """
        Format caption data into Instagram-ready text.
        
        Args:
            caption_data: Dictionary with caption, hashtags, and CTA.
        
        Returns:
            Formatted caption string ready for Instagram.
        """
        lines = []
        
        # Add caption
        if caption_data.get('caption'):
            lines.append(caption_data['caption'])
            lines.append('')  # Empty line
        
        # Add CTA
        if caption_data.get('cta'):
            lines.append(caption_data['cta'])
            lines.append('')  # Empty line
        
        # Add hashtags
        if caption_data.get('hashtags'):
            hashtags = ' '.join(caption_data['hashtags'])
            lines.append(hashtags)
        
        return '\n'.join(lines)


def main():
    """Test function."""
    generator = AICaptionGenerator()
    
    test_content = """
    Kombucha is a fermented tea beverage that has been consumed for thousands of years.
    It contains probiotics, antioxidants, and beneficial acids that support gut health.
    Research suggests kombucha may help improve digestion and boost immune function.
    """
    
    result = generator.generate_caption(
        test_content,
        'kombucha_benefits',
        'feed',
        ['health_conscious', 'restaurants']
    )
    
    print("Generated Caption:")
    print(generator.format_caption_for_instagram(result))


if __name__ == '__main__':
    main()
