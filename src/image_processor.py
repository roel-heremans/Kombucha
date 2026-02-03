"""
Image Processor Module

Creates Instagram feed posts with text overlays, brand colors, and optimized dimensions.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional, Tuple, Dict
import textwrap
from .utils import load_config, get_brand_colors, get_brand_fonts


class ImageProcessor:
    """Process images for Instagram feed posts."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize image processor.
        
        Args:
            config: Configuration dictionary. If None, loads from file.
        """
        if config is None:
            config = load_config()
        
        self.config = config
        self.brand_colors = get_brand_colors(config)
        self.brand_fonts = get_brand_fonts(config)
        
        # Instagram dimensions
        instagram_config = config.get('instagram', {})
        feed_dims = instagram_config.get('feed_dimensions', {})
        self.feed_width = feed_dims.get('width', 1080)
        self.feed_height = feed_dims.get('height', 1080)
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def load_font(self, font_name: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """
        Load font with fallback options.
        
        Args:
            font_name: Name of the font.
            size: Font size.
            bold: Whether to use bold weight.
        
        Returns:
            PIL Font object.
        """
        try:
            # Try to load the specified font
            if bold:
                font_paths = [
                    f"/usr/share/fonts/truetype/{font_name.lower()}-bold.ttf",
                    f"/usr/share/fonts/truetype/{font_name.lower()}-Bold.ttf",
                    f"/System/Library/Fonts/{font_name}.ttc",
                ]
            else:
                font_paths = [
                    f"/usr/share/fonts/truetype/{font_name.lower()}.ttf",
                    f"/System/Library/Fonts/{font_name}.ttc",
                ]
            
            for font_path in font_paths:
                if Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)
            
            # Fallback to default font
            return ImageFont.load_default()
        
        except Exception:
            return ImageFont.load_default()
    
    def create_text_overlay(
        self,
        image: Image.Image,
        text: str,
        position: str = 'bottom',
        max_width: Optional[int] = None,
        font_size: int = 48,
        padding: int = 40
    ) -> Image.Image:
        """
        Add text overlay to image.
        
        Args:
            image: PIL Image object.
            text: Text to overlay.
            position: Position of text ('top', 'center', 'bottom').
            max_width: Maximum width for text wrapping.
            font_size: Font size.
            padding: Padding from edges.
        
        Returns:
            Image with text overlay.
        """
        if max_width is None:
            max_width = image.width - (padding * 2)
        
        # Load font
        font = self.load_font(
            self.brand_fonts.get('heading', 'Arial'),
            font_size,
            bold=True
        )
        
        # Wrap text
        wrapped_lines = []
        for line in text.split('\n'):
            wrapped = textwrap.wrap(line, width=max_width // (font_size // 2))
            wrapped_lines.extend(wrapped)
        
        # Calculate text dimensions
        draw = ImageDraw.Draw(image)
        line_heights = []
        for line in wrapped_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])
        
        total_height = sum(line_heights) + (len(wrapped_lines) - 1) * 10
        
        # Calculate position
        if position == 'top':
            y_start = padding
        elif position == 'center':
            y_start = (image.height - total_height) // 2
        else:  # bottom
            y_start = image.height - total_height - padding
        
        # Create semi-transparent background for text
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        text_color = self.hex_to_rgb(self.brand_colors.get('text', '#000000'))
        bg_color = self.hex_to_rgb(self.brand_colors.get('background', '#ffffff'))
        
        # Draw background rectangle
        rect_y1 = max(0, y_start - padding // 2)
        rect_y2 = min(image.height, y_start + total_height + padding // 2)
        overlay_draw.rectangle(
            [(padding // 2, rect_y1), (image.width - padding // 2, rect_y2)],
            fill=(*bg_color, 200)  # Semi-transparent
        )
        
        # Draw text
        y_offset = y_start
        for i, line in enumerate(wrapped_lines):
            x = padding
            overlay_draw.text((x, y_offset), line, font=font, fill=(*text_color, 255))
            y_offset += line_heights[i] + 10
        
        # Composite overlay onto image
        image = Image.alpha_composite(image.convert('RGBA'), overlay)
        return image.convert('RGB')
    
    def process_image(
        self,
        image_path: Path,
        output_path: Path,
        text_overlay: Optional[str] = None,
        text_position: str = 'bottom'
    ) -> Path:
        """
        Process an image for Instagram feed post.
        
        Args:
            image_path: Path to source image.
            output_path: Path to save processed image.
            text_overlay: Optional text to overlay on image.
            text_position: Position of text overlay.
        
        Returns:
            Path to saved image.
        """
        # Open and resize image
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to Instagram feed dimensions (maintain aspect ratio, crop if needed)
        img.thumbnail((self.feed_width, self.feed_height), Image.Resampling.LANCZOS)
        
        # Create new image with exact dimensions
        new_img = Image.new('RGB', (self.feed_width, self.feed_height), 
                           self.hex_to_rgb(self.brand_colors.get('background', '#ffffff')))
        
        # Center the image
        x_offset = (self.feed_width - img.width) // 2
        y_offset = (self.feed_height - img.height) // 2
        new_img.paste(img, (x_offset, y_offset))
        
        # Add text overlay if provided
        if text_overlay:
            new_img = self.create_text_overlay(new_img, text_overlay, text_position)
        
        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        new_img.save(output_path, 'JPEG', quality=95)
        
        return output_path
    
    def create_quote_card(
        self,
        quote: str,
        author: Optional[str] = None,
        output_path: Path = None
    ) -> Path:
        """
        Create a quote card image.
        
        Args:
            quote: Quote text.
            author: Optional author name.
            output_path: Path to save the image.
        
        Returns:
            Path to saved image.
        """
        if output_path is None:
            output_path = Path(__file__).parent.parent / 'output' / 'feed_posts' / 'quote_card.jpg'
        
        # Create image
        img = Image.new('RGB', (self.feed_width, self.feed_height),
                       self.hex_to_rgb(self.brand_colors.get('background', '#ffffff')))
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        quote_font = self.load_font(
            self.brand_fonts.get('heading', 'Arial'),
            60,
            bold=True
        )
        author_font = self.load_font(
            self.brand_fonts.get('body', 'Arial'),
            36,
            bold=False
        )
        
        # Wrap quote text
        max_width = self.feed_width - 160
        wrapped_quote = textwrap.wrap(quote, width=max_width // 30)
        
        # Calculate positions
        quote_height = sum(draw.textbbox((0, 0), line, font=quote_font)[3] - 
                          draw.textbbox((0, 0), line, font=quote_font)[1] 
                          for line in wrapped_quote) + (len(wrapped_quote) - 1) * 20
        
        if author:
            author_bbox = draw.textbbox((0, 0), author, font=author_font)
            author_height = author_bbox[3] - author_bbox[1]
            total_height = quote_height + author_height + 40
        else:
            total_height = quote_height
        
        start_y = (self.feed_height - total_height) // 2
        
        # Draw quote
        text_color = self.hex_to_rgb(self.brand_colors.get('text', '#000000'))
        primary_color = self.hex_to_rgb(self.brand_colors.get('primary', '#1a5f3f'))
        
        y_offset = start_y
        for line in wrapped_quote:
            bbox = draw.textbbox((0, 0), line, font=quote_font)
            line_width = bbox[2] - bbox[0]
            x = (self.feed_width - line_width) // 2
            draw.text((x, y_offset), line, font=quote_font, fill=primary_color)
            y_offset += bbox[3] - bbox[1] + 20
        
        # Draw author if provided
        if author:
            author_bbox = draw.textbbox((0, 0), author, font=author_font)
            author_width = author_bbox[2] - author_bbox[0]
            author_x = (self.feed_width - author_width) // 2
            draw.text((author_x, y_offset + 20), f"— {author}", font=author_font, fill=text_color)
        
        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, 'JPEG', quality=95)
        
        return output_path


def main():
    """Test function."""
    processor = ImageProcessor()
    
    # Test quote card creation
    quote = "Kombucha is a fermented tea that supports gut health and boosts immunity."
    output = processor.create_quote_card(quote, "Research Study")
    print(f"Created quote card: {output}")


if __name__ == '__main__':
    main()
