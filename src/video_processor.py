"""
Video Processor Module

Creates Instagram Reels with clips, music, text overlays, and transitions.
"""

from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip, concatenate_videoclips
from moviepy.video.fx import resize
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import textwrap
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
            clip = clip.subclip(start_time, min(end_time, clip.duration))
        
        # Resize to fit Reel dimensions (maintain aspect ratio, crop if needed)
        clip = clip.resize(height=self.reel_height)
        
        # Center crop if width exceeds
        if clip.w > self.reel_width:
            x_center = clip.w / 2
            clip = clip.crop(x_center=x_center, width=self.reel_width)
        
        return clip
    
    def create_text_clip(
        self,
        text: str,
        duration: float,
        position: str = 'bottom',
        font_size: int = 60,
        start_time: float = 0
    ) -> TextClip:
        """
        Create a text overlay clip.
        
        Args:
            text: Text to display.
            duration: Duration of text clip.
            position: Position ('top', 'center', 'bottom').
            font_size: Font size.
            start_time: Start time in seconds.
        
        Returns:
            TextClip object.
        """
        # Wrap text
        max_chars_per_line = 30
        wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
        display_text = '\n'.join(wrapped_lines)
        
        # Calculate position
        if position == 'top':
            y_pos = 100
        elif position == 'center':
            y_pos = 'center'
        else:  # bottom
            y_pos = self.reel_height - 300
        
        # Get colors
        text_color = self.brand_colors.get('text', '#000000')
        bg_color = self.brand_colors.get('background', '#ffffff')
        
        # Create text clip
        txt_clip = TextClip(
            display_text,
            fontsize=font_size,
            color=text_color,
            font=self.brand_fonts.get('heading', 'Arial'),
            stroke_color=bg_color,
            stroke_width=2,
            method='caption',
            size=(self.reel_width - 100, None),
            align='center'
        ).set_position(('center', y_pos)).set_duration(duration).set_start(start_time)
        
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
                from moviepy.editor import AudioFileClip, concatenate_audioclips
                audio = AudioFileClip(str(music_path))
                # Loop audio if needed
                if audio.duration < final_clip.duration:
                    loops = int(final_clip.duration / audio.duration) + 1
                    audio = concatenate_audioclips([audio] * loops)
                    audio = audio.subclip(0, final_clip.duration)
                else:
                    audio = audio.subclip(0, final_clip.duration)
                
                # Lower volume to 30% for background
                audio = audio.volumex(0.3)
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
            clip = clip.resize(height=self.reel_height)
            if clip.w > self.reel_width:
                x_center = clip.w / 2
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


def main():
    """Test function."""
    processor = VideoProcessor()
    print("Video processor initialized.")
    print(f"Reel dimensions: {processor.reel_width}x{processor.reel_height}")
    print(f"Duration range: {processor.min_duration}-{processor.max_duration} seconds")


if __name__ == '__main__':
    main()
