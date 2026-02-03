#!/usr/bin/env python3
"""
Instagram Content Generator CLI

Main entry point for generating Instagram content.
"""

import click
from pathlib import Path
from src.content_generator import ContentGenerator
from src.brand_extractor import BrandExtractor
from src.utils import load_config
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)


@click.group()
def cli():
    """Instagram Content Generator for Real Health Kombucha."""
    pass


@cli.command()
@click.option('--theme', '-t', required=True, help='Theme name (e.g., kombucha_benefits)')
@click.option('--type', '-T', type=click.Choice(['feed', 'reel'], case_sensitive=False),
              required=True, help='Content type: feed or reel')
@click.option('--image', '-i', type=click.Path(exists=True), help='Specific image file to use (for feed posts)')
@click.option('--videos', '-v', multiple=True, type=click.Path(exists=True),
              help='Specific video files to use (for reels, can specify multiple)')
@click.option('--music', '-m', type=click.Path(exists=True), help='Background music file for reels')
@click.option('--no-pdf', is_flag=True, help='Skip PDF content extraction')
def generate(theme, type, image, videos, music, no_pdf):
    """Generate Instagram content (feed post or reel)."""
    try:
        generator = ContentGenerator()
        
        click.echo(f"{Fore.CYAN}Generating {type} content for theme: {theme}{Style.RESET_ALL}")
        
        if type.lower() == 'feed':
            # Generate feed post
            image_path = Path(image) if image else None
            result = generator.generate_feed_post(
                theme,
                image_path=image_path,
                use_pdf_content=not no_pdf
            )
            
            click.echo(f"{Fore.GREEN}✓ Feed post generated successfully!{Style.RESET_ALL}")
            click.echo(f"  Image: {result['image']}")
            click.echo(f"  Caption: {result['caption']}")
            click.echo(f"  Metadata: {result['metadata']}")
        
        elif type.lower() == 'reel':
            # Generate reel
            video_paths = [Path(v) for v in videos] if videos else None
            music_path = Path(music) if music else None
            
            result = generator.generate_reel(
                theme,
                video_paths=video_paths,
                use_pdf_content=not no_pdf,
                music_path=music_path
            )
            
            click.echo(f"{Fore.GREEN}✓ Reel generated successfully!{Style.RESET_ALL}")
            click.echo(f"  Video: {result['video']}")
            click.echo(f"  Caption: {result['caption']}")
            click.echo(f"  Metadata: {result['metadata']}")
    
    except ValueError as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}", err=True)
        exit(1)


@cli.command()
def themes():
    """List available themes."""
    generator = ContentGenerator()
    themes_list = generator.list_themes()
    
    if not themes_list:
        click.echo(f"{Fore.YELLOW}No themes found. Create theme directories in assets/{Style.RESET_ALL}")
        return
    
    click.echo(f"{Fore.CYAN}Available themes:{Style.RESET_ALL}")
    for theme in themes_list:
        stats = generator.get_theme_stats(theme)
        click.echo(f"  {Fore.GREEN}{theme}{Style.RESET_ALL}")
        click.echo(f"    Images: {stats['images']}, Videos: {stats['videos']}, PDFs: {stats['pdfs']}")


@cli.command()
@click.option('--theme', '-t', help='Show stats for specific theme')
def stats(theme):
    """Show statistics about themes and assets."""
    generator = ContentGenerator()
    
    if theme:
        if theme not in generator.list_themes():
            click.echo(f"{Fore.RED}Theme '{theme}' not found{Style.RESET_ALL}", err=True)
            exit(1)
        
        stats = generator.get_theme_stats(theme)
        click.echo(f"{Fore.CYAN}Stats for '{theme}':{Style.RESET_ALL}")
        click.echo(f"  Images: {stats['images']}")
        click.echo(f"  Videos: {stats['videos']}")
        click.echo(f"  PDFs: {stats['pdfs']}")
    else:
        themes_list = generator.list_themes()
        click.echo(f"{Fore.CYAN}Overall Statistics:{Style.RESET_ALL}")
        
        total_images = 0
        total_videos = 0
        total_pdfs = 0
        
        for theme in themes_list:
            stats = generator.get_theme_stats(theme)
            total_images += stats['images']
            total_videos += stats['videos']
            total_pdfs += stats['pdfs']
        
        click.echo(f"  Themes: {len(themes_list)}")
        click.echo(f"  Total Images: {total_images}")
        click.echo(f"  Total Videos: {total_videos}")
        click.echo(f"  Total PDFs: {total_pdfs}")


@cli.command()
def extract_brand():
    """Extract brand colors and fonts from website."""
    click.echo(f"{Fore.CYAN}Extracting brand information from realhealthkombucha.com...{Style.RESET_ALL}")
    
    extractor = BrandExtractor()
    brand_info = extractor.extract_brand_info()
    
    click.echo(f"{Fore.GREEN}✓ Brand extraction complete!{Style.RESET_ALL}")
    click.echo(f"\n{Fore.CYAN}Extracted Information:{Style.RESET_ALL}")
    click.echo(f"  Name: {brand_info['name']}")
    click.echo(f"  Colors:")
    for key, value in brand_info['colors'].items():
        click.echo(f"    {key}: {value}")
    click.echo(f"  Fonts:")
    click.echo(f"    Heading: {brand_info['fonts']['heading']}")
    click.echo(f"    Body: {brand_info['fonts']['body']}")
    
    # Save to config
    config_path = Path(__file__).parent / 'config' / 'settings.yaml'
    extractor.save_to_config(config_path, brand_info)
    
    click.echo(f"\n{Fore.GREEN}Brand information saved to config/settings.yaml{Style.RESET_ALL}")


@cli.command()
def config():
    """Show current configuration."""
    config_data = load_config()
    
    click.echo(f"{Fore.CYAN}Current Configuration:{Style.RESET_ALL}")
    click.echo(f"\n{Fore.YELLOW}Brand:{Style.RESET_ALL}")
    brand = config_data.get('brand', {})
    click.echo(f"  Name: {brand.get('name', 'N/A')}")
    click.echo(f"  Website: {brand.get('website', 'N/A')}")
    
    click.echo(f"\n{Fore.YELLOW}Colors:{Style.RESET_ALL}")
    colors = brand.get('colors', {})
    for key, value in colors.items():
        click.echo(f"  {key}: {value}")
    
    click.echo(f"\n{Fore.YELLOW}Fonts:{Style.RESET_ALL}")
    fonts = brand.get('fonts', {})
    click.echo(f"  Heading: {fonts.get('heading', 'N/A')}")
    click.echo(f"  Body: {fonts.get('body', 'N/A')}")
    
    click.echo(f"\n{Fore.YELLOW}AI Settings:{Style.RESET_ALL}")
    ai = config_data.get('ai', {})
    click.echo(f"  Provider: {ai.get('provider', 'N/A')}")
    click.echo(f"  Model: {ai.get('model', 'N/A')}")
    click.echo(f"  Language: {ai.get('language', 'N/A')}")
    
    click.echo(f"\n{Fore.YELLOW}Themes:{Style.RESET_ALL}")
    themes = config_data.get('themes', [])
    for theme in themes:
        click.echo(f"  - {theme.get('name', 'N/A')}")


if __name__ == '__main__':
    cli()
