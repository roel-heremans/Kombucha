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
try:
    from .video_processor import VideoProcessor
except ImportError:
    VideoProcessor = None  # Video processing optional if moviepy not available
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
        try:
            if VideoProcessor:
                self.video_processor = VideoProcessor(config)
            else:
                self.video_processor = None
        except Exception as e:
            print(f"Warning: Video processor not available: {e}")
            self.video_processor = None
        
        ensure_output_dirs()
    
    def _validate_path(self, path: Path, path_type: str = "file") -> Path:
        """
        Validate that a path exists and convert relative paths to absolute.
        
        Args:
            path: Path to validate (can be string or Path).
            path_type: Type of path ('file' or 'directory').
        
        Returns:
            Absolute Path object.
        
        Raises:
            ValueError: If path doesn't exist or is wrong type.
        """
        if isinstance(path, str):
            path = Path(path)
        
        # Convert to absolute path if relative
        if not path.is_absolute():
            path = Path(__file__).parent.parent / path
        
        if not path.exists():
            raise ValueError(f"{path_type.capitalize()} {path} not found")
        
        if path_type == 'file' and not path.is_file():
            raise ValueError(f"Path {path} is not a file")
        elif path_type == 'directory' and not path.is_dir():
            raise ValueError(f"Path {path} is not a directory")
        
        return path
    
    def find_assets(self, theme_name: str, asset_type: str) -> List[Path]:
        """
        Find assets of a specific type.
        
        New structure:
        - Images: assets/01_images/
        - Videos: assets/02_videos/
        - Quotes: assets/03_kombucha_quotes/
        - PDFs: assets/04_immune_system/, assets/05_kombucha_benefits/, etc.
        
        Args:
            theme_name: Name of the theme (used for PDFs only, e.g., '04_immune_system').
            asset_type: Type of asset ('images', 'videos', 'pdfs', 'quotes').
        
        Returns:
            List of asset paths.
        """
        if asset_type == 'images':
            # Images are in assets/01_images/
            assets_path = self.assets_base_path / '01_images'
            extensions = ['.jpg', '.jpeg', '.png', '.webp']
        elif asset_type == 'videos':
            # Videos are in assets/02_videos/
            assets_path = self.assets_base_path / '02_videos'
            extensions = ['.mp4', '.mov', '.avi', '.mkv']
        elif asset_type == 'quotes':
            # Quotes are in assets/03_kombucha_quotes/
            assets_path = self.assets_base_path / '03_kombucha_quotes'
            extensions = ['.txt']
        elif asset_type == 'pdfs':
            # PDFs are in numbered theme folders/pdfs subfolder (e.g., assets/04_immune_system/pdfs/)
            assets_path = self.assets_base_path / theme_name / 'pdfs'
            extensions = ['.pdf']
        else:
            return []
        
        if not assets_path.exists():
            return []
        
        assets = []
        for ext in extensions:
            assets.extend(assets_path.glob(f'*{ext}'))
            assets.extend(assets_path.glob(f'*{ext.upper()}'))
        
        return sorted(assets)
    
    def generate_feed_post(
        self,
        theme_name: str,
        image_path: Optional[Path] = None,
        text_overlay: Optional[str] = None,
        use_pdf_content: bool = True,
        use_quote: bool = False
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
        # Get quote for text overlay (always try to get a quote)
        quote_text = None
        try:
            from .quote_generator import QuoteGenerator
            quote_gen = QuoteGenerator()
            quote_text = quote_gen.get_random_quote()
        except Exception as e:
            print(f"Warning: Could not load quote: {e}")
        
        # Get PDF content for caption only if not using quotes or if explicitly requested
        pdf_text = ""
        if use_pdf_content and not quote_text:
            # Only process PDFs if we don't have a quote to use for caption
            # Try JSON first, then fallback to PDF processing
            pdf_text = self.pdf_processor.get_combined_text_from_json(theme_name)
            if not pdf_text:
                pdf_text = self.pdf_processor.get_combined_text(theme_name, max_pages_per_pdf=5)
        
        # Generate caption - use quote if available, otherwise use PDF content
        caption_source = quote_text if quote_text else (pdf_text or "Kombucha benefits and health information.")
        caption_data = self.ai_generator.generate_caption(
            caption_source,
            theme_name,
            'feed'
        )
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{theme_name}_{timestamp}.jpg"
        output_path = self.output_base_path / 'feed_posts' / output_filename
        
        # Find images
        images = self.find_assets(theme_name, 'images')
        
        # If use_quote is True and we have a quote, create quote card
        if use_quote and quote_text:
            processed_image_path = self.image_processor.create_quote_card(
                quote=quote_text,
                author="Real Health Kombucha",
                output_path=output_path
            )
            image_source = "quote_card_from_collection"
        # If no images available, create a quote card from PDF content
        elif not images:
            # Extract a good quote from PDF content
            if pdf_text:
                # Try to get key points from JSON first
                key_points = self.pdf_processor.get_key_points_from_json(theme_name)
                if not key_points:
                    key_points = self.pdf_processor.extract_key_points(pdf_text, max_points=3)
                else:
                    key_points = key_points[:3]  # Limit to 3
                if key_points:
                    # Use the first key point as quote (limit to 200 chars)
                    quote = key_points[0][:200]
                    if len(key_points[0]) > 200:
                        quote = key_points[0][:197] + "..."
                else:
                    # Fallback: use first sentence from PDF
                    quote = pdf_text.split('.')[0][:200] if pdf_text else "Descubra os benefícios do kombucha!"
            else:
                quote = "Descubra os benefícios do kombucha para sua saúde!"
            
            # Create quote card
            processed_image_path = self.image_processor.create_quote_card(
                quote=quote,
                author="Real Health Kombucha",
                output_path=output_path
            )
            image_source = "quote_card_generated"
        else:
            # Select image
            if image_path is None:
                if not images:
                    raise ValueError(f"No images found for theme '{theme_name}'. Place images in assets/01_images/")
                image_path = random.choice(images)
            else:
                # User provided a specific image path - validate it exists
                image_path = self._validate_path(image_path, 'file')
            
            # Always use quote from collection for text overlay (not PDFs)
            if text_overlay is None:
                if quote_text:
                    text_overlay = quote_text  # Use full quote as overlay
                else:
                    # This shouldn't happen since we load quote_text earlier, but keep as fallback
                    text_overlay = "Descubra os benefícios do kombucha para sua saúde!"
            
            # Process image with font size for readability
            processed_image_path = self.image_processor.process_image(
                image_path,
                output_path,
                text_overlay=text_overlay,
                text_position='bottom',  # Keep at bottom
                font_size=20  # Font size for text overlay
            )
            image_source = str(image_path)
        
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
            'image_source': image_source,
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
    
    def generate_combined_reel(
        self,
        theme_name: str,
        video_paths: Optional[List[Path]] = None,
        image_paths: Optional[List[Path]] = None,
        use_quote: bool = True,
        use_pdf_content: bool = True,
        use_llm_refinement: bool = False,
        music_path: Optional[Path] = None,
        video_duration: float = 5.0,
        image_duration: float = 3.0
    ) -> Dict[str, Path]:
        """
        Generate a combined reel with video, images, quotes, and health benefits.
        
        Args:
            theme_name: Name of the theme.
            video_paths: Optional specific videos to use.
            image_paths: Optional specific images to use.
            use_quote: Whether to include a quote overlay.
            use_pdf_content: Whether to use PDF content for health benefits.
            use_llm_refinement: Whether to use LLM to refine health benefit text.
            music_path: Optional background music.
            video_duration: Duration for video segments.
            image_duration: Duration for image segments.
        
        Returns:
            Dictionary with paths to generated content.
        """
        if not self.video_processor:
            raise ValueError("Video processor not available. Please install moviepy.")
        
        # Get videos
        videos = self.find_assets(theme_name, 'videos')
        if not videos and not video_paths:
            raise ValueError(f"No videos found in assets/02_videos/")
        
        # Get images
        images = self.find_assets(theme_name, 'images')
        if not images and not image_paths:
            raise ValueError(f"No images found in assets/01_images/")
        
        # Select videos
        if video_paths is None:
            selected_videos = [random.choice(videos)] if videos else []
        else:
            # Validate provided video paths
            selected_videos = [self._validate_path(vp, 'file') for vp in video_paths]
        
        # Select images
        if image_paths is None:
            selected_images = [random.choice(images)] if images else []
        else:
            # Validate provided image paths
            selected_images = [self._validate_path(ip, 'file') for ip in image_paths]
        
        # Get PDF content for health benefits
        pdf_text = ""
        health_benefit_text = None
        if use_pdf_content:
            # Prioritize refined key points from JSON (already human-friendly and accessible)
            json_content = self.pdf_processor.load_processed_content(theme_name)
            using_json = json_content is not None and 'summary' in json_content
            
            if using_json:
                # Use a random key point from JSON for variety (all are already refined)
                benefit_text = self.pdf_processor.get_random_key_point_from_json(theme_name)
                if benefit_text:
                    # Get all key points for caption generation context
                    all_key_points = self.pdf_processor.get_key_points_from_json(theme_name, max_points=5)
                    pdf_text = ". ".join(all_key_points[:3]) + "." if all_key_points else ""
                else:
                    benefit_text = None
            else:
                # Fallback: get combined text and extract key points (raw extraction)
                pdf_text = self.pdf_processor.get_combined_text(theme_name, max_pages_per_pdf=5)
                if pdf_text:
                    key_points = self.pdf_processor.extract_key_points(pdf_text, max_points=1)
                    benefit_text = key_points[0] if key_points else None
                else:
                    benefit_text = None
            
            if benefit_text:
                # Use the refined key point from JSON (already optimized for readability)
                # or the extracted one from PDFs
                
                # JSON key points are already refined to be short and accessible
                # But we still need to ensure they fit on screen (max 200 chars for video)
                if len(benefit_text) > 200:
                    # Smart truncation: find last sentence boundary
                    truncated = benefit_text[:200]
                    last_period = truncated.rfind('.')
                    last_exclamation = truncated.rfind('!')
                    last_question = truncated.rfind('?')
                    last_sentence_end = max(last_period, last_exclamation, last_question)
                    
                    if last_sentence_end > 50:  # Found a reasonable sentence end
                        health_benefit_text = benefit_text[:last_sentence_end + 1].strip()
                    else:
                        # No sentence end found, truncate at word boundary
                        last_space = truncated.rfind(' ')
                        if last_space > 150:
                            health_benefit_text = benefit_text[:last_space].strip() + "..."
                        else:
                            health_benefit_text = truncated.strip() + "..."
                else:
                    health_benefit_text = benefit_text.strip()
                
                # Only apply additional LLM refinement if explicitly requested AND not using JSON
                # (JSON points are already refined, so double refinement is usually unnecessary)
                if use_llm_refinement and not using_json and health_benefit_text:
                    try:
                        refined = self.ai_generator.refine_health_benefit(
                            health_benefit_text,
                            theme_name,
                            max_length=200
                        )
                        # Use the language version matching config
                        config_language = self.config.get('ai', {}).get('language', 'en')
                        if config_language in refined:
                            health_benefit_text = refined[config_language]
                        elif 'en' in refined:
                            health_benefit_text = refined['en']
                        elif 'pt' in refined:
                            health_benefit_text = refined['pt']
                    except Exception as e:
                        print(f"Warning: LLM refinement failed, using original text: {e}")
                elif using_json:
                    # JSON key points are already refined, so we can use them directly
                    print(f"Using refined key points from JSON (already optimized for accessibility)")
        
        # Get quote
        quote_text = None
        if use_quote:
            try:
                from .quote_generator import QuoteGenerator
                quote_gen = QuoteGenerator()
                quote_text = quote_gen.get_random_quote()
            except Exception as e:
                print(f"Warning: Could not load quote: {e}")
        
        # Generate caption
        caption_data = self.ai_generator.generate_caption(
            pdf_text or "Kombucha health benefits and wellness information.",
            theme_name,
            'reel'
        )
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{theme_name}_combined_{timestamp}.mp4"
        output_path = self.output_base_path / 'reels' / output_filename
        
        # Create combined reel
        processed_video_path = self.video_processor.create_combined_reel(
            selected_videos,
            image_paths=selected_images,
            quote_text=quote_text,
            health_benefit_text=health_benefit_text,
            output_path=output_path,
            video_duration=video_duration,
            image_duration=image_duration,
            music_path=music_path
        )
        
        # Save caption
        caption_filename = f"{theme_name}_combined_{timestamp}_caption.txt"
        caption_path = self.output_base_path / 'reels' / caption_filename
        
        formatted_caption = self.ai_generator.format_caption_for_instagram(caption_data)
        with open(caption_path, 'w', encoding='utf-8') as f:
            f.write(formatted_caption)
        
        # Save metadata
        metadata_filename = f"{theme_name}_combined_{timestamp}_metadata.json"
        metadata_path = self.output_base_path / 'reels' / metadata_filename
        
        metadata = {
            'theme': theme_name,
            'type': 'reel_combined',
            'video_sources': [str(v) for v in selected_videos],
            'image_sources': [str(i) for i in selected_images],
            'quote': quote_text,
            'health_benefit': health_benefit_text.replace('\n', ' ') if health_benefit_text else None,
            'generated_at': datetime.now().isoformat(),
            'caption_data': caption_data,
            'output_video': str(processed_video_path),
            'caption_file': str(caption_path)
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return {
            'video': processed_video_path,
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
            # Validate provided video paths
            selected_videos = [self._validate_path(vp, 'file') for vp in video_paths]
        
        # Get PDF content for captions/subtitles
        pdf_text = ""
        if use_pdf_content:
            # Try JSON first, then fallback to PDF processing
            pdf_text = self.pdf_processor.get_combined_text_from_json(theme_name)
            if not pdf_text:
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
        """List available themes (numbered folders 04-07)."""
        if not self.assets_base_path.exists():
            return []
        
        themes = []
        for item in self.assets_base_path.iterdir():
            if item.is_dir() and item.name.startswith(('04_', '05_', '06_', '07_')):
                themes.append(item.name)
        
        return sorted(themes)
    
    def get_theme_stats(self, theme_name: str) -> Dict:
        """Get statistics about assets in a theme."""
        return {
            'images': len(self.find_assets(theme_name, 'images')),
            'videos': len(self.find_assets(theme_name, 'videos')),
            'pdfs': len(self.find_assets(theme_name, 'pdfs')),
            'quotes': len(self.find_assets(theme_name, 'quotes'))
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
