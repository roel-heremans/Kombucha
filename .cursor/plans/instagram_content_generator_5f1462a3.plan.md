---
name: Instagram Content Generator
overview: Build a Python-based Instagram content generation engine that organizes local assets (photos, videos, PDFs) by themes, uses AI to generate captions and hashtags, creates image posts with text overlays, and produces video Reels with editing - all ready for manual posting.
todos:
  - id: setup_project
    content: Create project structure with directories (assets/, output/, src/, config/) and base files (requirements.txt, main.py, README.md)
    status: completed
  - id: pdf_processor
    content: Build PDF processor to extract text from PDFs in theme directories using pdfplumber
    status: completed
    dependencies:
      - setup_project
  - id: ai_caption_generator
    content: Create AI caption generator module using OpenAI API (or Ollama) to generate captions, hashtags, and CTAs from PDF content
    status: completed
    dependencies:
      - setup_project
  - id: image_processor
    content: Build image processor using Pillow to create feed posts with text overlays, brand colors from config, and Instagram-optimized dimensions
    status: completed
    dependencies:
      - setup_project
      - config_system
  - id: video_processor
    content: Create video processor using moviepy to generate Reels with clips, music, text overlays using brand fonts/colors, and transitions
    status: completed
    dependencies:
      - setup_project
      - config_system
  - id: content_generator
    content: Build main content generator orchestrator that selects assets, coordinates processors, and generates final content
    status: completed
    dependencies:
      - pdf_processor
      - ai_caption_generator
      - image_processor
      - video_processor
  - id: cli_interface
    content: Create CLI interface (main.py) with commands for generating content by theme and type (reel/feed)
    status: completed
    dependencies:
      - content_generator
  - id: brand_extractor
    content: Create brand extractor module to scrape realhealthkombucha.com and extract colors, fonts, and branding elements
    status: completed
    dependencies:
      - setup_project
  - id: config_system
    content: Implement YAML configuration system with extracted brand values, themes, AI provider, and API keys
    status: completed
    dependencies:
      - setup_project
      - brand_extractor
---

