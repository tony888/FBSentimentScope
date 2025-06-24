"""Data utility functions for Facebook Comment Analyzer."""

import json
import csv
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataUtils:
    """Utility class for data manipulation and processing."""
    
    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary with loaded data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            raise
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Union[str, Path], pretty: bool = True) -> None:
        """Save data to a JSON file.
        
        Args:
            data: Data to save
            file_path: Path to save the JSON file
            pretty: Whether to format JSON nicely
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)
            logger.info(f"Data saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON to {file_path}: {e}")
            raise
    
    @staticmethod
    def load_csv(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Load data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of dictionaries with CSV data
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
            return data
        except Exception as e:
            logger.error(f"Failed to load CSV from {file_path}: {e}")
            raise
    
    @staticmethod
    def save_csv(data: List[Dict[str, Any]], file_path: Union[str, Path]) -> None:
        """Save data to a CSV file.
        
        Args:
            data: List of dictionaries to save
            file_path: Path to save the CSV file
            
        Raises:
            ValueError: If data is empty or doesn't have consistent keys
        """
        if not data:
            raise ValueError("Cannot save empty data to CSV")
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            fieldnames = data[0].keys()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Data saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save CSV to {file_path}: {e}")
            raise
    
    @staticmethod
    def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten a nested dictionary.
        
        Args:
            data: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(DataUtils.flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        items.extend(DataUtils.flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                    else:
                        items.append((f"{new_key}{sep}{i}", item))
            else:
                items.append((new_key, value))
        
        return dict(items)
    
    @staticmethod
    def normalize_text_encoding(text: str) -> str:
        """Normalize text encoding for consistent processing.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not isinstance(text, str):
            return str(text)
        
        # Remove or replace problematic characters
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def validate_data_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that data contains required fields.
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            True if all required fields are present
            
        Raises:
            ValueError: If required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        return True
    
    @staticmethod
    def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
        """Split a list into chunks of specified size.
        
        Args:
            data: List to chunk
            chunk_size: Size of each chunk
            
        Returns:
            List of chunks
        """
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    @staticmethod
    def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple dictionaries, with later ones taking precedence.
        
        Args:
            *dicts: Dictionaries to merge
            
        Returns:
            Merged dictionary
        """
        result = {}
        for d in dicts:
            if d:
                result.update(d)
        return result
    
    @staticmethod
    def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Safely get a value from a dictionary with nested key support.
        
        Args:
            data: Dictionary to search
            key: Key to look for (supports dot notation for nested keys)
            default: Default value if key is not found
            
        Returns:
            Value from dictionary or default
        """
        try:
            if '.' in key:
                keys = key.split('.')
                value = data
                for k in keys:
                    value = value[k]
                return value
            else:
                return data.get(key, default)
        except (KeyError, TypeError):
            return default
    
    @staticmethod
    def generate_timestamp() -> str:
        """Generate a timestamp string for file naming.
        
        Returns:
            Timestamp string in format YYYYMMDD_HHMMSS
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
