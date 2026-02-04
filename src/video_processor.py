"""
Video Processor Module

Creates Instagram Reels with clips, music, text overlays, and transitions.
"""

try:
    from moviepy import VideoFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, ImageClip, AudioFileClip, concatenate_audioclips
except ImportError:
    # Fallback for older moviepy versions
    try:
        from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, ImageClip, AudioFileClip, concatenate_audioclips
    except ImportError:
        raise ImportError("moviepy is not installed. Please install it with: pip install moviepy")
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import textwrap
import tempfile
from PIL import Image, ImageOps
from .utils import load_config, get_brand_colors, get_brand_fonts


class VideoProcessor:
    """Process videos for Instagram Reels."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize video processor.
        
        Args:
            config: Configuration dictionary. If None, loads from file.
        """
        if config is None:
            config = load_config()
        
        self.config = config
        self.brand_colors = get_brand_colors(config)
        self.brand_fonts = get_brand_fonts(config)
        
        # Instagram Reel dimensions
        instagram_config = config.get('instagram', {})
        reel_dims = instagram_config.get('reel_dimensions', {})
        self.reel_width = reel_dims.get('width', 1080)
        self.reel_height = reel_dims.get('height', 1920)
        
        reel_duration = instagram_config.get('reel_duration', {})
        self.min_duration = reel_duration.get('min', 15)
        self.max_duration = reel_duration.get('max', 90)
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def prepare_clip(
        self,
        video_path: Path,
        duration: Optional[float] = None,
        start_time: float = 0
    ) -> VideoFileClip:
        """
        Load and prepare a video clip.
        
        Args:
            video_path: Path to video file.
            duration: Duration to extract. If None, uses full clip.
            start_time: Start time in seconds.
        
        Returns:
            Prepared VideoFileClip.
        """
        clip = VideoFileClip(str(video_path))
        
        # Extract segment if needed
        if start_time > 0 or duration:
            end_time = start_time + duration if duration else clip.duration
            # Use subclipped for moviepy 2.x, fallback to subclip for older versions
            if hasattr(clip, 'subclipped'):
                clip = clip.subclipped(start_time, min(end_time, clip.duration))
            elif hasattr(clip, 'subclip'):
                clip = clip.subclip(start_time, min(end_time, clip.duration))
            # If neither method exists, just use the full clip
        
        # Resize to fit Reel dimensions (maintain aspect ratio, crop if needed)
        # Use resized for moviepy 2.x, fallback to resize for older versions
        if hasattr(clip, 'resized'):
            clip = clip.resized(height=self.reel_height)
        elif hasattr(clip, 'resize'):
            clip = clip.resize(height=self.reel_height)
        
        # Center crop if width exceeds
        if clip.w > self.reel_width:
            x_center = clip.w / 2
            if hasattr(clip, 'cropped'):
                clip = clip.cropped(x_center=x_center, width=self.reel_width)
            elif hasattr(clip, 'crop'):
                clip = clip.crop(x_center=x_center, width=self.reel_width)
        
        return clip
    
    def calculate_text_duration(self, text: str, min_duration: float = 3.0, max_duration: float = 10.0) -> float:
        """
        Calculate appropriate duration for text based on reading speed.
        
        Args:
            text: Text to display.
            min_duration: Minimum duration in seconds.
            max_duration: Maximum duration in seconds.
        
        Returns:
            Calculated duration in seconds.
        """
        # Count words and characters
        words = len(text.split())
        chars = len(text)
        
        # Reading speed: approximately 2-3 words per second for comfortable reading
        # Also account for character count (longer words need more time)
        # Base calculation: 2.5 words per second + 0.1 seconds per 10 characters
        word_based_duration = words / 2.5
        char_based_duration = chars / 100.0  # 100 chars per second
        
        # Use the longer of the two calculations to ensure readability
        calculated_duration = max(word_based_duration, char_based_duration)
        
        # Add extra time for multi-line text (more lines = more reading time)
        num_lines = len(textwrap.wrap(text, width=30))
        if num_lines > 1:
            calculated_duration += (num_lines - 1) * 0.5
        
        # Ensure duration is within bounds
        duration = max(min_duration, min(calculated_duration, max_duration))
        
        return duration
    
    def create_text_clip(
        self,
        text: str,
        duration: Optional[float] = None,
        position: str = 'bottom',
        font_size: int = 60,
        start_time: float = 0,
        auto_duration: bool = True
    ) -> TextClip:
        """
        Create a text overlay clip.
        
        Args:
            text: Text to display.
            duration: Duration of text clip. If None and auto_duration=True, calculates based on text length.
            position: Position ('top', 'center', 'bottom').
            font_size: Font size.
            start_time: Start time in seconds.
            auto_duration: If True and duration is None, automatically calculate duration based on text length.
        
        Returns:
            TextClip object.
        """
        # Calculate duration if not provided and auto_duration is enabled
        if duration is None and auto_duration:
            duration = self.calculate_text_duration(text, min_duration=3.0, max_duration=10.0)
        elif duration is None:
            duration = 5.0  # Default fallback
        # Wrap text
        max_chars_per_line = 30
        wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
        display_text = '\n'.join(wrapped_lines)
        
        # Calculate position - ensure text fits fully on screen
        # Estimate text height based on number of lines and font size
        num_lines = len(wrapped_lines)
        estimated_text_height = num_lines * (font_size * 1.5)  # Approximate line height
        
        if position == 'top':
            y_pos = 150  # More space from top to ensure text isn't cut off
        elif position == 'center':
            # Center vertically accounting for text height
            y_pos = (self.reel_height - estimated_text_height) // 2
            # Ensure it doesn't go off screen
            y_pos = max(100, min(y_pos, self.reel_height - estimated_text_height - 100))
        else:  # bottom
            # Leave more space from bottom to ensure text isn't cut off
            y_pos = self.reel_height - estimated_text_height - 200
            # Ensure it doesn't go off screen
            y_pos = max(100, y_pos)
        
        # Get colors
        text_color = self.brand_colors.get('text', '#000000')
        bg_color = self.brand_colors.get('background', '#ffffff')
        
        # Get font with fallback
        font_name = self.brand_fonts.get('heading', 'Arial')
        # Validate font name - use Arial if font contains invalid characters or is too long
        if (not font_name or 
            len(font_name) > 50 or 
            '{' in font_name or 
            '}' in font_name or 
            font_name.startswith('rgb') or
            'placeholder' in font_name.lower() or
            'var(' in font_name.lower()):
            font_name = 'Arial'
        
        # Create text clip - moviepy 2.x uses font_size instead of fontsize
        # Use larger size parameter to ensure text fits properly
        # Try with the font, but fallback to Arial if font doesn't exist
        try:
            # Try moviepy 2.x style first
            txt_clip = TextClip(
                text=display_text,
                font_size=font_size,
                color=text_color,
                font=font_name,
                stroke_color=bg_color,
                stroke_width=2,
                size=(self.reel_width - 120, None),  # More padding
                margin=(20, 20)  # Add margin to prevent clipping
            )
        except (TypeError, OSError, Exception) as e:
            # If font doesn't exist or other error, try with Arial
            if 'font' in str(e).lower() or 'cannot open resource' in str(e).lower():
                font_name = 'Arial'
            try:
                # Try moviepy 2.x style with Arial fallback
                txt_clip = TextClip(
                    text=display_text,
                    font_size=font_size,
                    color=text_color,
                    font=font_name,
                    stroke_color=bg_color,
                    stroke_width=2,
                    size=(self.reel_width - 120, None),
                    margin=(20, 20)
                )
            except TypeError:
                try:
                    # Try without font parameter
                    txt_clip = TextClip(
                        text=display_text,
                        font_size=font_size,
                        color=text_color,
                        size=(self.reel_width - 120, None),
                        margin=(20, 20)
                    )
                except TypeError:
                    # Fallback to moviepy 1.x style
                    txt_clip = TextClip(
                        display_text,
                        fontsize=font_size,
                        color=text_color,
                        font=font_name,
                        stroke_color=bg_color,
                        stroke_width=2,
                        method='caption',
                        size=(self.reel_width - 120, None),
                        align='center'
                    )
        # Set position, duration, and start time
        if hasattr(txt_clip, 'with_position'):
            txt_clip = txt_clip.with_position(('center', y_pos))
        else:
            txt_clip = txt_clip.set_position(('center', y_pos))
        
        if hasattr(txt_clip, 'with_duration'):
            txt_clip = txt_clip.with_duration(duration)
        else:
            txt_clip = txt_clip.set_duration(duration)
        
        if hasattr(txt_clip, 'with_start'):
            txt_clip = txt_clip.with_start(start_time)
        else:
            txt_clip = txt_clip.set_start(start_time)
        
        return txt_clip
        
        return txt_clip
    
    def create_reel(
        self,
        video_paths: List[Path],
        output_path: Path,
        text_overlays: Optional[List[Dict]] = None,
        music_path: Optional[Path] = None,
        transition_duration: float = 0.5
    ) -> Path:
        """
        Create an Instagram Reel from multiple video clips.
        
        Args:
            video_paths: List of paths to video files.
            output_path: Path to save the Reel.
            text_overlays: List of text overlay dicts with 'text', 'start_time', 'duration', 'position'.
            music_path: Optional path to background music file.
            transition_duration: Duration of transitions between clips.
        
        Returns:
            Path to saved Reel.
        """
        if not video_paths:
            raise ValueError("At least one video path is required")
        
        # Load and prepare clips
        clips = []
        current_time = 0
        
        for i, video_path in enumerate(video_paths):
            # Calculate clip duration to fit within max duration
            remaining_time = self.max_duration - current_time
            if remaining_time <= 0:
                break
            
            # Distribute time evenly among remaining clips
            clip_duration = min(remaining_time / (len(video_paths) - i), 10)  # Max 10 seconds per clip
            
            clip = self.prepare_clip(video_path, duration=clip_duration)
            # In moviepy 2.x, timing is handled differently - clips are positioned during composition
            # Store start time for later use in composition
            # Position clip at the right time
            if hasattr(clip, 'with_start'):
                clip = clip.with_start(current_time)
            elif hasattr(clip, 'set_start'):
                clip = clip.set_start(current_time)
            clips.append(clip)
            
            current_time += clip_duration - transition_duration
        
        # Concatenate clips
        if len(clips) > 1:
            final_clip = concatenate_videoclips(clips, method="compose")
        else:
            final_clip = clips[0]
        
        # Ensure minimum duration
        if final_clip.duration < self.min_duration:
            # Loop the clip if too short
            loops_needed = int(self.min_duration / final_clip.duration) + 1
            looped_clips = [final_clip] * loops_needed
            final_clip = concatenate_videoclips(looped_clips, method="compose")
            if hasattr(final_clip, 'subclipped'):
                final_clip = final_clip.subclipped(0, self.min_duration)
            else:
                final_clip = final_clip.subclip(0, self.min_duration)
        
        # Ensure maximum duration
        if final_clip.duration > self.max_duration:
            final_clip = final_clip.subclip(0, self.max_duration)
        
        # Add text overlays
        if text_overlays:
            text_clips = []
            for overlay in text_overlays:
                txt_clip = self.create_text_clip(
                    overlay.get('text', ''),
                    overlay.get('duration', 3),
                    overlay.get('position', 'bottom'),
                    overlay.get('font_size', 60),
                    overlay.get('start_time', 0)
                )
                text_clips.append(txt_clip)
            
            final_clip = CompositeVideoClip([final_clip] + text_clips)
        
        # Add background music if provided
        if music_path and music_path.exists():
            try:
                audio = AudioFileClip(str(music_path))
                # Loop audio if needed
                if audio.duration < final_clip.duration:
                    loops = int(final_clip.duration / audio.duration) + 1
                    audio = concatenate_audioclips([audio] * loops)
                    if hasattr(audio, 'subclipped'):
                        audio = audio.subclipped(0, final_clip.duration)
                    else:
                        audio = audio.subclip(0, final_clip.duration)
                else:
                    if hasattr(audio, 'subclipped'):
                        audio = audio.subclipped(0, final_clip.duration)
                    else:
                        audio = audio.subclip(0, final_clip.duration)
                
                # Lower volume to 30% for background
                # moviepy 2.x uses with_volume_scaled instead of volumex
                if hasattr(audio, 'with_volume_scaled'):
                    audio = audio.with_volume_scaled(0.3)
                elif hasattr(audio, 'volumex'):
                    audio = audio.volumex(0.3)
                else:
                    # Fallback: try to use fx module
                    try:
                        from moviepy.audio.fx import volumex
                        audio = audio.fx(volumex, 0.3)
                    except:
                        pass  # Continue without volume adjustment
                # Handle moviepy 2.x API changes
                if hasattr(final_clip, 'with_audio'):
                    final_clip = final_clip.with_audio(audio)
                else:
                    final_clip = final_clip.set_audio(audio)
            except Exception as e:
                print(f"Warning: Could not add music: {e}")
        
        # Write video file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_clip.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            bitrate='8000k'
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        return output_path
    
    def add_subtitles(
        self,
        video_path: Path,
        output_path: Path,
        subtitles: List[Dict],
        font_size: int = 50
    ) -> Path:
        """
        Add subtitles to a video.
        
        Args:
            video_path: Path to source video.
            output_path: Path to save video with subtitles.
            subtitles: List of subtitle dicts with 'text', 'start_time', 'duration'.
            font_size: Font size for subtitles.
        
        Returns:
            Path to saved video.
        """
        clip = VideoFileClip(str(video_path))
        
        # Resize if needed
        if clip.h != self.reel_height or clip.w != self.reel_width:
            if hasattr(clip, 'resized'):
                clip = clip.resized(height=self.reel_height)
            elif hasattr(clip, 'resize'):
                clip = clip.resize(height=self.reel_height)
            if clip.w > self.reel_width:
                x_center = clip.w / 2
                if hasattr(clip, 'cropped'):
                    clip = clip.cropped(x_center=x_center, width=self.reel_width)
                elif hasattr(clip, 'crop'):
                    clip = clip.crop(x_center=x_center, width=self.reel_width)
        
        # Create subtitle clips
        subtitle_clips = []
        for subtitle in subtitles:
            txt_clip = self.create_text_clip(
                subtitle.get('text', ''),
                subtitle.get('duration', 3),
                'bottom',
                font_size,
                subtitle.get('start_time', 0)
            )
            subtitle_clips.append(txt_clip)
        
        # Composite
        final_clip = CompositeVideoClip([clip] + subtitle_clips)
        
        # Write
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_clip.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            bitrate='8000k'
        )
        
        # Clean up
        final_clip.close()
        clip.close()
        
        return output_path
    
    def image_to_clip(
        self,
        image_path: Path,
        duration: float = 3.0
    ) -> ImageClip:
        """
        Convert an image to a video clip, handling EXIF orientation.
        
        Args:
            image_path: Path to image file.
            duration: Duration of the clip in seconds.
        
        Returns:
            ImageClip object.
        """
        # Load image with PIL to handle EXIF orientation
        img = Image.open(image_path)
        
        # Apply EXIF orientation correction
        # This ensures images display correctly regardless of how they were taken
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            # If EXIF data is missing or invalid, continue with original image
            pass
        
        # Convert to RGB if necessary (required for moviepy)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save to temporary file with correct orientation
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            img.save(tmp_path, 'JPEG', quality=95)
        
        # Create ImageClip from the corrected image
        clip = ImageClip(tmp_path)
        
        # Resize to fit Reel dimensions
        if hasattr(clip, 'resized'):
            clip = clip.resized(height=self.reel_height)
        elif hasattr(clip, 'resize'):
            clip = clip.resize(height=self.reel_height)
        
        # Center crop if width exceeds reel width
        if clip.w > self.reel_width:
            x_center = clip.w / 2
            if hasattr(clip, 'cropped'):
                clip = clip.cropped(x_center=x_center, width=self.reel_width)
            elif hasattr(clip, 'crop'):
                clip = clip.crop(x_center=x_center, width=self.reel_width)
        
        # Set duration
        if hasattr(clip, 'with_duration'):
            clip = clip.with_duration(duration)
        elif hasattr(clip, 'set_duration'):
            clip = clip.set_duration(duration)
        
        # Store temp file path for cleanup (will be cleaned up when clip is closed)
        clip.tmp_path = tmp_path
        
        return clip
    
    def create_combined_reel(
        self,
        video_paths: List[Path],
        image_paths: Optional[List[Path]] = None,
        quote_text: Optional[str] = None,
        health_benefit_text: Optional[str] = None,
        output_path: Path = None,
        video_duration: float = 5.0,
        image_duration: float = 3.0,
        music_path: Optional[Path] = None
    ) -> Path:
        """
        Create a reel combining videos, images, quotes, and health benefits.
        
        Args:
            video_paths: List of video files to use.
            image_paths: Optional list of image files to include.
            quote_text: Optional quote text to overlay.
            health_benefit_text: Optional health benefit text to overlay.
            output_path: Path to save the reel.
            video_duration: Duration for each video clip segment.
            image_duration: Duration for each image segment.
            music_path: Optional background music.
        
        Returns:
            Path to saved reel.
        """
        clips = []
        current_time = 0
        temp_files = []  # Track temp files for cleanup
        
        # Process videos
        for video_path in video_paths:
            clip = self.prepare_clip(video_path, duration=video_duration)
            # In moviepy 2.x, timing is handled differently - clips are positioned during composition
            # Store start time for later use in composition
            # Position clip at the right time
            if hasattr(clip, 'with_start'):
                clip = clip.with_start(current_time)
            elif hasattr(clip, 'set_start'):
                clip = clip.set_start(current_time)
            clips.append(clip)
            current_time += video_duration
        
        # Process images
        if image_paths:
            for image_path in image_paths:
                img_clip = self.image_to_clip(image_path, duration=image_duration)
                # Store temp file path for cleanup if it exists
                if hasattr(img_clip, 'tmp_path'):
                    temp_files.append(img_clip.tmp_path)
                # Position image clip at the right time
                if hasattr(img_clip, 'with_start'):
                    img_clip = img_clip.with_start(current_time)
                elif hasattr(img_clip, 'set_start'):
                    img_clip = img_clip.set_start(current_time)
                clips.append(img_clip)
                current_time += image_duration
        
        # Concatenate all clips
        if len(clips) > 1:
            final_clip = concatenate_videoclips(clips, method="compose")
        else:
            final_clip = clips[0]
        
        # Ensure minimum duration
        if final_clip.duration < self.min_duration:
            loops_needed = int(self.min_duration / final_clip.duration) + 1
            looped_clips = [final_clip] * loops_needed
            final_clip = concatenate_videoclips(looped_clips, method="compose")
            if hasattr(final_clip, 'subclipped'):
                final_clip = final_clip.subclipped(0, self.min_duration)
            else:
                final_clip = final_clip.subclip(0, self.min_duration)
        
        # Ensure maximum duration
        if final_clip.duration > self.max_duration:
            final_clip = final_clip.subclip(0, self.max_duration)
        
        # Add text overlays
        text_clips = []
        
        # Add quote overlay (appears early in the video)
        if quote_text:
            # Calculate duration based on text length, but ensure it doesn't exceed video duration
            quote_duration = self.calculate_text_duration(quote_text, min_duration=3.0, max_duration=min(10.0, final_clip.duration * 0.4))
            quote_start_time = final_clip.duration * 0.1
            # Ensure quote doesn't extend beyond video end
            if quote_start_time + quote_duration > final_clip.duration:
                quote_duration = max(3.0, final_clip.duration - quote_start_time - 0.5)
            
            quote_clip = self.create_text_clip(
                quote_text,
                duration=quote_duration,
                position='center',
                font_size=65,  # Slightly smaller to ensure it fits
                start_time=quote_start_time,
                auto_duration=False  # Already calculated above
            )
            text_clips.append(quote_clip)
        
        # Add health benefit overlay (appears later)
        if health_benefit_text:
            # Clean up the health benefit text - remove newlines and ensure it's readable
            clean_benefit = health_benefit_text.replace('\n', ' ').strip()
            # Calculate duration based on text length
            benefit_duration = self.calculate_text_duration(clean_benefit, min_duration=3.0, max_duration=min(12.0, final_clip.duration * 0.5))
            benefit_start_time = final_clip.duration * 0.5
            # Ensure benefit text doesn't extend beyond video end
            if benefit_start_time + benefit_duration > final_clip.duration:
                benefit_duration = max(3.0, final_clip.duration - benefit_start_time - 0.5)
            
            benefit_clip = self.create_text_clip(
                clean_benefit,
                duration=benefit_duration,
                position='bottom',
                font_size=55,  # Slightly smaller for bottom text
                start_time=benefit_start_time,
                auto_duration=False  # Already calculated above
            )
            text_clips.append(benefit_clip)
        
        if text_clips:
            final_clip = CompositeVideoClip([final_clip] + text_clips)
        
        # Add background music if provided
        if music_path and music_path.exists():
            try:
                audio = AudioFileClip(str(music_path))
                if audio.duration < final_clip.duration:
                    loops = int(final_clip.duration / audio.duration) + 1
                    audio = concatenate_audioclips([audio] * loops)
                    if hasattr(audio, 'subclipped'):
                        audio = audio.subclipped(0, final_clip.duration)
                    else:
                        audio = audio.subclip(0, final_clip.duration)
                else:
                    if hasattr(audio, 'subclipped'):
                        audio = audio.subclipped(0, final_clip.duration)
                    else:
                        audio = audio.subclip(0, final_clip.duration)
                # Lower volume to 30% for background
                # moviepy 2.x uses with_volume_scaled instead of volumex
                if hasattr(audio, 'with_volume_scaled'):
                    audio = audio.with_volume_scaled(0.3)
                elif hasattr(audio, 'volumex'):
                    audio = audio.volumex(0.3)
                else:
                    # Fallback: try to use fx module
                    try:
                        from moviepy.audio.fx import volumex
                        audio = audio.fx(volumex, 0.3)
                    except:
                        pass  # Continue without volume adjustment
                # Handle moviepy 2.x API changes
                if hasattr(final_clip, 'with_audio'):
                    final_clip = final_clip.with_audio(audio)
                else:
                    final_clip = final_clip.set_audio(audio)
            except Exception as e:
                print(f"Warning: Could not add music: {e}")
        
        # Write video file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_clip.write_videofile(
            str(output_path),
            fps=30,
            codec='libx264',
            audio_codec='aac',
            preset='medium',
            bitrate='8000k'
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        # Clean up temporary image files
        import os
        for tmp_file in temp_files:
            try:
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)
            except Exception:
                pass  # Ignore cleanup errors
        
        return output_path


def main():
    """Test function."""
    processor = VideoProcessor()
    print("Video processor initialized.")
    print(f"Reel dimensions: {processor.reel_width}x{processor.reel_height}")
    print(f"Duration range: {processor.min_duration}-{processor.max_duration} seconds")


if __name__ == '__main__':
    main()
