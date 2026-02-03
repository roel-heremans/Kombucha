"""
Content Generator Module

Main orchestrator that coordinates all processors to generate Instagram content.
"""

import random
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .pdf_processor import PDFProcessor
from .ai_caption_generator import AICaptionGenerator
from .image_processor import ImageProcessor
from .video_processor import VideoProcessor
from .utils import load_config, get_theme_config, ensure_output_dirs


class ContentGenerator:
    """Main content generator orchestrator."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize content generator.
        
        Args:
            config: Configuration dictionary. If None, loads from file.
        """
        if config is None:
            config = load_config()
        
        self.config = config
        self.assets_base_path = Path(__file__).parent.parent / 'assets'
        self.output_base_path = Path(__file__).parent.parent / 'output'
        
        # Initialize processors
        self.pdf_processor = PDFProcessor(self.assets_base_path)
        self.ai_generator = AICaptionGenerator(config)
        self.image_processor = ImageProcessor(config)
        self.video_processor = VideoProcessor(config)
        
        ensure_output_dirs()
    
    def find_assets(self, theme_name: str, asset_type: str) -> List[Path]:
        """
        Find assets of a specific type in a theme directory.
        
        Args:
            theme_name: Name of the theme.
            asset_type: Type of asset ('images', 'videos', 'pdfs').
        
        Returns:
            List of asset paths.
        """
        theme_path = self.assets_base_path / theme_name / asset_type
        if not theme_path.exists():
            return []
        
        if asset_type == 'images':
            extensions = ['.jpg', '.jpeg', '.png', '.webp']
        elif asset_type == 'videos':
            extensions = ['.mp4', '.mov', '.avi', '.mkv']
        elif asset_type == 'pdfs':
            extensions = ['.pdf']
        else:
            return []
        
        assets = []
        for ext in extensions:
            assets.extend(theme_path.glob(f'*{ext}'))
            assets.extend(theme_path.glob(f'*{ext.upper()}'))
        
        return sorted(assets)
    
    def generate_feed_post(
        self,
        theme_name: str,
        image_path: Optional[Path] = None,
        text_overlay: Optional[str] = None,
        use_pdf_content: bool = True
    ) -> Dict[str, Path]:
        """
        Generate an Instagram feed post.
        
        Args:
            theme_name: Name of the theme.
            image_path: Optional specific image to use. If None, selects randomly.
            text_overlay: Optional text to overlay. If None, generates from PDFs.
            use_pdf_content: Whether to use PDF content for caption generation.
        
        Returns:
            Dictionary with paths to generated content and caption file.
        """
        # Find images
        images = self.find_assets(theme_name, 'images')
        if not images:
            raise ValueError(f"No images found in theme '{theme_name}'")
        
        # Select image
        if image_path is None:
            image_path = random.choice(images)
        elif image_path not in images:
            raise ValueError(f"Image {image_path} not found in theme '{theme_name}'")
        
        # Get PDF content for caption if needed
        pdf_text = ""
        if use_pdf_content:
            pdf_text = self.pdf_processor.get_combined_text(theme_name, max_pages_per_pdf=5)
        
        # Generate caption
        caption_data = self.ai_generator.generate_caption(
            pdf_text or "Kombucha benefits and health information.",
            theme_name,
            'feed'
        )
        
        # Use text overlay from PDF if not provided
        if text_overlay is None and pdf_text:
            key_points = self.pdf_processor.extract_key_points(pdf_text, max_points=1)
            if key_points:
                text_overlay = key_points[0][:100]  # Limit to 100 chars
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{theme_name}_{timestamp}.jpg"
        output_path = self.output_base_path / 'feed_posts' / output_filename
        
        # Process image
        processed_image_path = self.image_processor.process_image(
            image_path,
            output_path,
            text_overlay=text_overlay,
            text_position='bottom'
        )
        
        # Save caption
        caption_filename = f"{theme_name}_{timestamp}_caption.txt"
        caption_path = self.output_base_path / 'feed_posts' / caption_filename
        
        formatted_caption = self.ai_generator.format_caption_for_instagram(caption_data)
        with open(caption_path, 'w', encoding='utf-8') as f:
            f.write(formatted_caption)
        
        # Save metadata
        metadata_filename = f"{theme_name}_{timestamp}_metadata.json"
        metadata_path = self.output_base_path / 'feed_posts' / metadata_filename
        
        metadata = {
            'theme': theme_name,
            'type': 'feed',
            'image_source': str(image_path),
            'generated_at': datetime.now().isoformat(),
            'caption_data': caption_data,
            'output_image': str(processed_image_path),
            'caption_file': str(caption_path)
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return {
            'image': processed_image_path,
            'caption': caption_path,
            'metadata': metadata_path
        }
    
    def generate_reel(
        self,
        theme_name: str,
        video_paths: Optional[List[Path]] = None,
        num_clips: int = 3,
        use_pdf_content: bool = True,
        music_path: Optional[Path] = None
    ) -> Dict[str, Path]:
        """
        Generate an Instagram Reel.
        
        Args:
            theme_name: Name of the theme.
            video_paths: Optional specific videos to use. If None, selects randomly.
            num_clips: Number of video clips to use.
            use_pdf_content: Whether to use PDF content for caption/subtitle generation.
            music_path: Optional path to background music file.
        
        Returns:
            Dictionary with paths to generated content and caption file.
        """
        # Find videos
        videos = self.find_assets(theme_name, 'videos')
        if not videos:
            raise ValueError(f"No videos found in theme '{theme_name}'")
        
        # Select videos
        if video_paths is None:
            if len(videos) < num_clips:
                # Repeat videos if not enough
                selected_videos = (videos * ((num_clips // len(videos)) + 1))[:num_clips]
            else:
                selected_videos = random.sample(videos, num_clips)
        else:
            selected_videos = video_paths
        
        # Get PDF content for captions/subtitles
        pdf_text = ""
        if use_pdf_content:
            pdf_text = self.pdf_processor.get_combined_text(theme_name, max_pages_per_pdf=5)
        
        # Generate caption for post
        caption_data = self.ai_generator.generate_caption(
            pdf_text or "Kombucha benefits and health information.",
            theme_name,
            'reel'
        )
        
        # Create text overlays for video (subtitles)
        text_overlays = []
        if pdf_text:
            key_points = self.pdf_processor.extract_key_points(pdf_text, max_points=num_clips)
            clip_duration = min(90 / num_clips, 10)  # Distribute time
            
            for i, point in enumerate(key_points[:num_clips]):
                text_overlays.append({
                    'text': point[:80],  # Limit text length
                    'start_time': i * clip_duration,
                    'duration': min(clip_duration - 1, 5),
                    'position': 'bottom',
                    'font_size': 50
                })
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{theme_name}_{timestamp}.mp4"
        output_path = self.output_base_path / 'reels' / output_filename
        
        # Create reel
        processed_video_path = self.video_processor.create_reel(
            selected_videos,
            output_path,
            text_overlays=text_overlays if text_overlays else None,
            music_path=music_path
        )
        
        # Save caption
        caption_filename = f"{theme_name}_{timestamp}_caption.txt"
        caption_path = self.output_base_path / 'reels' / caption_filename
        
        formatted_caption = self.ai_generator.format_caption_for_instagram(caption_data)
        with open(caption_path, 'w', encoding='utf-8') as f:
            f.write(formatted_caption)
        
        # Save metadata
        metadata_filename = f"{theme_name}_{timestamp}_metadata.json"
        metadata_path = self.output_base_path / 'reels' / metadata_filename
        
        metadata = {
            'theme': theme_name,
            'type': 'reel',
            'video_sources': [str(v) for v in selected_videos],
            'generated_at': datetime.now().isoformat(),
            'caption_data': caption_data,
            'output_video': str(processed_video_path),
            'caption_file': str(caption_path),
            'text_overlays': text_overlays
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return {
            'video': processed_video_path,
            'caption': caption_path,
            'metadata': metadata_path
        }
    
    def list_themes(self) -> List[str]:
        """List available themes."""
        if not self.assets_base_path.exists():
            return []
        
        themes = []
        for item in self.assets_base_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                themes.append(item.name)
        
        return sorted(themes)
    
    def get_theme_stats(self, theme_name: str) -> Dict:
        """Get statistics about assets in a theme."""
        return {
            'images': len(self.find_assets(theme_name, 'images')),
            'videos': len(self.find_assets(theme_name, 'videos')),
            'pdfs': len(self.find_assets(theme_name, 'pdfs'))
        }


def main():
    """Test function."""
    generator = ContentGenerator()
    
    themes = generator.list_themes()
    print(f"Available themes: {themes}")
    
    if themes:
        theme = themes[0]
        stats = generator.get_theme_stats(theme)
        print(f"\nStats for '{theme}':")
        print(f"  Images: {stats['images']}")
        print(f"  Videos: {stats['videos']}")
        print(f"  PDFs: {stats['pdfs']}")


if __name__ == '__main__':
    main()
