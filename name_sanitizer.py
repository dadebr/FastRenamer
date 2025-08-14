"""
Filename sanitization and conflict resolution utilities.
Provides functions to sanitize filenames and resolve naming conflicts.
"""

import os
import re
import unicodedata
from pathlib import Path
from typing import List, Tuple, Optional


def sanitize_filename(filename: str, 
                     normalize_unicode: bool = True, 
                     replace_spaces: bool = False, 
                     max_length: int = 255) -> str:
    """Sanitize a filename by removing or replacing invalid characters.
    
    Args:
        filename: The original filename to sanitize
        normalize_unicode: Whether to normalize unicode characters
        replace_spaces: Whether to replace spaces with underscores
        max_length: Maximum filename length (default 255)
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    if not filename:
        return "unnamed"
    
    # Normalize unicode if requested
    if normalize_unicode:
        filename = unicodedata.normalize('NFKD', filename)
        # Remove combining characters
        filename = ''.join(c for c in filename if not unicodedata.combining(c))
    
    # Replace or remove invalid characters
    # Windows invalid chars: < > : " | ? * \
    # Plus control characters (0-31) and DEL (127)
    invalid_chars = r'[<>:"|?*\\\x00-\x1f\x7f]'
    filename = re.sub(invalid_chars, '_', filename)
    
    # Handle reserved Windows names
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_without_ext = Path(filename).stem.upper()
    if name_without_ext in reserved_names:
        filename = f"_{filename}"
    
    # Replace spaces if requested
    if replace_spaces:
        filename = filename.replace(' ', '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure it's not empty after sanitization
    if not filename:
        filename = "unnamed"
    
    # Truncate if too long, preserving extension
    if len(filename) > max_length:
        path = Path(filename)
        ext = path.suffix
        stem = path.stem
        
        # Calculate available length for stem
        available_length = max_length - len(ext)
        if available_length > 0:
            filename = stem[:available_length] + ext
        else:
            filename = filename[:max_length]
    
    return filename


def resolve_filename_conflicts(base_filename: str, 
                               directory: Path, 
                               suffix_format: str = "({})"  ,
                               max_attempts: int = 1000) -> str:
    """Resolve filename conflicts by adding numeric suffixes.
    
    Args:
        base_filename: The desired filename
        directory: Directory where the file will be placed
        suffix_format: Format string for the suffix (default: "({})")
        max_attempts: Maximum number of attempts to find unique name
        
    Returns:
        Unique filename that doesn't exist in the directory
    """
    if not directory.exists():
        return base_filename
    
    original_path = directory / base_filename
    
    # If no conflict, return original filename
    if not original_path.exists():
        return base_filename
    
    # Split filename into parts
    path = Path(base_filename)
    stem = path.stem
    suffix = path.suffix
    
    # Try numbered variants
    for i in range(1, max_attempts + 1):
        numbered_suffix = suffix_format.format(i)
        new_filename = f"{stem}{numbered_suffix}{suffix}"
        new_path = directory / new_filename
        
        if not new_path.exists():
            return new_filename
    
    # If we couldn't find a unique name, add timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{stem}_{timestamp}{suffix}"


def truncate_filename(filename: str, 
                     max_length: int, 
                     preserve_extension: bool = True) -> str:
    """Truncate a filename to a maximum length.
    
    Args:
        filename: The filename to truncate
        max_length: Maximum allowed length
        preserve_extension: Whether to preserve the file extension
        
    Returns:
        Truncated filename
    """
    if len(filename) <= max_length:
        return filename
    
    if not preserve_extension:
        return filename[:max_length]
    
    path = Path(filename)
    ext = path.suffix
    stem = path.stem
    
    # If extension is too long, truncate the whole filename
    if len(ext) >= max_length:
        return filename[:max_length]
    
    # Calculate available length for stem
    available_length = max_length - len(ext)
    if available_length > 0:
        return stem[:available_length] + ext
    else:
        return ext[:max_length]


def add_prefix_suffix(filename: str, 
                     prefix: str = "", 
                     suffix: str = "") -> str:
    """Add prefix and/or suffix to a filename while preserving the extension.
    
    Args:
        filename: The original filename
        prefix: Prefix to add before the filename
        suffix: Suffix to add before the extension
        
    Returns:
        Modified filename with prefix/suffix
    """
    if not filename:
        return filename
    
    path = Path(filename)
    stem = path.stem
    ext = path.suffix
    
    new_stem = f"{prefix}{stem}{suffix}"
    return new_stem + ext


def normalize_filename_case(filename: str, case_style: str = "lower") -> str:
    """Normalize filename case.
    
    Args:
        filename: The filename to normalize
        case_style: Case style - 'lower', 'upper', 'title', or 'sentence'
        
    Returns:
        Filename with normalized case
    """
    if not filename:
        return filename
    
    path = Path(filename)
    stem = path.stem
    ext = path.suffix.lower()  # Extensions are typically lowercase
    
    if case_style == "lower":
        stem = stem.lower()
    elif case_style == "upper":
        stem = stem.upper()
    elif case_style == "title":
        stem = stem.title()
    elif case_style == "sentence":
        stem = stem.capitalize()
    
    return stem + ext


class FilenameSanitizer:
    """Class for comprehensive filename sanitization with configurable options."""
    
    def __init__(self, 
                 normalize_unicode: bool = True,
                 replace_spaces: bool = False,
                 max_length: int = 255,
                 case_style: Optional[str] = None,
                 conflict_resolution: bool = True,
                 conflict_suffix_format: str = "({})"):
        """Initialize the sanitizer with configuration options.
        
        Args:
            normalize_unicode: Whether to normalize unicode characters
            replace_spaces: Whether to replace spaces with underscores
            max_length: Maximum filename length
            case_style: Case normalization style ('lower', 'upper', 'title', 'sentence')
            conflict_resolution: Whether to resolve naming conflicts automatically
            conflict_suffix_format: Format for conflict resolution suffixes
        """
        self.normalize_unicode = normalize_unicode
        self.replace_spaces = replace_spaces
        self.max_length = max_length
        self.case_style = case_style
        self.conflict_resolution = conflict_resolution
        self.conflict_suffix_format = conflict_suffix_format
    
    def sanitize(self, 
                filename: str, 
                directory: Optional[Path] = None, 
                prefix: str = "", 
                suffix: str = "") -> str:
        """Perform comprehensive filename sanitization.
        
        Args:
            filename: Original filename
            directory: Target directory (for conflict resolution)
            prefix: Prefix to add
            suffix: Suffix to add
            
        Returns:
            Fully sanitized and conflict-free filename
        """
        if not filename:
            return "unnamed"
        
        # Start with basic sanitization
        result = sanitize_filename(
            filename,
            normalize_unicode=self.normalize_unicode,
            replace_spaces=self.replace_spaces,
            max_length=self.max_length
        )
        
        # Add prefix/suffix
        if prefix or suffix:
            result = add_prefix_suffix(result, prefix, suffix)
            # Re-truncate if necessary after adding prefix/suffix
            result = truncate_filename(result, self.max_length)
        
        # Normalize case
        if self.case_style:
            result = normalize_filename_case(result, self.case_style)
        
        # Resolve conflicts if requested and directory provided
        if self.conflict_resolution and directory:
            result = resolve_filename_conflicts(
                result, 
                directory, 
                suffix_format=self.conflict_suffix_format
            )
        
        return result
    
    def batch_sanitize(self, 
                      filenames: List[str], 
                      directory: Optional[Path] = None,
                      prefix: str = "", 
                      suffix: str = "") -> List[Tuple[str, str]]:
        """Sanitize multiple filenames at once.
        
        Args:
            filenames: List of original filenames
            directory: Target directory (for conflict resolution)
            prefix: Prefix to add to all files
            suffix: Suffix to add to all files
            
        Returns:
            List of tuples (original_filename, sanitized_filename)
        """
        results = []
        used_names = set()
        
        for original in filenames:
            sanitized = self.sanitize(original, directory, prefix, suffix)
            
            # Additional conflict resolution within the batch
            if sanitized in used_names:
                counter = 1
                base_path = Path(sanitized)
                stem = base_path.stem
                ext = base_path.suffix
                
                while sanitized in used_names and counter <= 1000:
                    numbered_suffix = self.conflict_suffix_format.format(counter)
                    sanitized = f"{stem}{numbered_suffix}{ext}"
                    counter += 1
            
            used_names.add(sanitized)
            results.append((original, sanitized))
        
        return results
