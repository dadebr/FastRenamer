"""
Content extraction module for file renaming based on file content.
Provides extractors for text files, PDFs, and image EXIF data.
"""

import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import chardet
except ImportError:
    chardet = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    Image = None
    TAGS = None


class BaseContentExtractor(ABC):
    """Base class for content extractors."""
    
    @abstractmethod
    def can_extract(self, file_path: Path) -> bool:
        """Check if this extractor can process the given file."""
        pass
    
    @abstractmethod
    def extract_content(self, file_path: Path, **kwargs) -> Optional[str]:
        """Extract content from the file for renaming purposes."""
        pass


class TextExtractor(BaseContentExtractor):
    """Extract content from text files (TXT, MD, etc.)."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.log', '.rst', '.csv'}
    
    def can_extract(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def extract_content(self, file_path: Path, **kwargs) -> Optional[str]:
        """Extract first non-empty line or use regex pattern.
        
        Args:
            file_path: Path to the text file
            regex_pattern: Optional regex pattern to extract specific content
        
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            # Detect encoding
            encoding = 'utf-8'
            if chardet:
                with open(file_path, 'rb') as f:
                    raw_data = f.read(8192)
                    result = chardet.detect(raw_data)
                    if result['encoding']:
                        encoding = result['encoding']
            
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            
            regex_pattern = kwargs.get('regex_pattern')
            if regex_pattern:
                match = re.search(regex_pattern, content, re.MULTILINE)
                if match:
                    return match.group(1) if match.groups() else match.group(0)
                return None
            
            # Return first non-empty line
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    return line
            
            return None
            
        except Exception:
            return None


class PDFExtractor(BaseContentExtractor):
    """Extract content from PDF files using pypdf."""
    
    def can_extract(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.pdf' and PdfReader is not None
    
    def extract_content(self, file_path: Path, **kwargs) -> Optional[str]:
        """Extract text from first few pages of PDF.
        
        Args:
            file_path: Path to the PDF file
            max_pages: Maximum number of pages to read (default: 3)
            regex_pattern: Optional regex pattern to extract specific content
        
        Returns:
            Extracted text content or None if extraction fails
        """
        if not PdfReader:
            return None
            
        try:
            reader = PdfReader(file_path)
            max_pages = min(kwargs.get('max_pages', 3), len(reader.pages))
            
            content = ""
            for i in range(max_pages):
                page = reader.pages[i]
                content += page.extract_text() + "\n"
            
            regex_pattern = kwargs.get('regex_pattern')
            if regex_pattern:
                match = re.search(regex_pattern, content, re.MULTILINE)
                if match:
                    return match.group(1) if match.groups() else match.group(0)
                return None
            
            # Return first non-empty line
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    return line
            
            return None
            
        except Exception:
            return None


class ImageExifExtractor(BaseContentExtractor):
    """Extract EXIF DateTimeOriginal from image files."""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.tiff', '.tif'}
    
    def can_extract(self, file_path: Path) -> bool:
        return (file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS and 
                Image is not None)
    
    def extract_content(self, file_path: Path, **kwargs) -> Optional[str]:
        """Extract DateTimeOriginal from EXIF data.
        
        Args:
            file_path: Path to the image file
            date_format: Format for date output (default: '%Y%m%d_%H%M%S')
        
        Returns:
            Formatted date string or None if no EXIF date found
        """
        if not Image or not TAGS:
            return None
            
        try:
            with Image.open(file_path) as img:
                exifdata = img.getexif()
                
                # Look for DateTimeOriginal (tag 306 or 36867)
                datetime_original = None
                for tag_id in [36867, 306]:  # DateTimeOriginal, DateTime
                    if tag_id in exifdata:
                        datetime_original = exifdata[tag_id]
                        break
                
                if not datetime_original:
                    return None
                
                # Parse datetime string (format: "YYYY:MM:DD HH:MM:SS")
                from datetime import datetime
                try:
                    dt = datetime.strptime(datetime_original, "%Y:%m:%d %H:%M:%S")
                    date_format = kwargs.get('date_format', '%Y%m%d_%H%M%S')
                    return dt.strftime(date_format)
                except ValueError:
                    return None
                    
        except Exception:
            return None


class ContentExtractorManager:
    """Manager class for handling multiple content extractors."""
    
    def __init__(self):
        self.extractors = [
            TextExtractor(),
            PDFExtractor(),
            ImageExifExtractor()
        ]
    
    def get_extractor(self, file_path: Path) -> Optional[BaseContentExtractor]:
        """Get the appropriate extractor for a file."""
        for extractor in self.extractors:
            if extractor.can_extract(file_path):
                return extractor
        return None
    
    def extract_content(self, file_path: Path, **kwargs) -> Optional[str]:
        """Extract content from file using appropriate extractor."""
        extractor = self.get_extractor(file_path)
        if extractor:
            return extractor.extract_content(file_path, **kwargs)
        return None
    
    def get_supported_extensions(self) -> set:
        """Get all supported file extensions."""
        extensions = set()
        if hasattr(TextExtractor, 'SUPPORTED_EXTENSIONS'):
            extensions.update(TextExtractor.SUPPORTED_EXTENSIONS)
        if PdfReader:
            extensions.add('.pdf')
        if Image:
            extensions.update(ImageExifExtractor.SUPPORTED_EXTENSIONS)
        return extensions
