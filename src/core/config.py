"""
Configuration management for the Facebook Comment Analyzer.

This module handles loading, validation, and management of application configuration
from environment variables, files, and default values.
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import asdict
from dotenv import load_dotenv

from .models import FacebookConfig, AnalysisConfig, ExportConfig
from .exceptions import ConfigurationError


class ConfigManager:
    """
    Manages application configuration from multiple sources.
    
    Configuration is loaded in the following order of precedence:
    1. Environment variables
    2. Configuration files (YAML)
    3. Default values
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to YAML configuration file (optional)
        """
        self.config_file = config_file
        self._load_environment()
        self._config_data = self._load_config_file() if config_file else {}
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        load_dotenv(override=True)
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_file):
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file: {e}")
    
    def get_facebook_config(self) -> FacebookConfig:
        """
        Load Facebook API configuration.
        
        Returns:
            FacebookConfig: Facebook API configuration
            
        Raises:
            ConfigurationError: If required configuration is missing
        """
        facebook_config = self._config_data.get('facebook', {})
        
        try:
            return FacebookConfig(
                app_id=self._get_config_value('FACEBOOK_APP_ID', facebook_config.get('app_id', '')),
                app_secret=self._get_config_value('FACEBOOK_APP_SECRET', facebook_config.get('app_secret', '')),
                access_token=self._get_config_value('FACEBOOK_ACCESS_TOKEN', facebook_config.get('access_token', '')),
                api_version=self._get_config_value('FACEBOOK_API_VERSION', facebook_config.get('api_version', 'v18.0')),
                timeout=int(self._get_config_value('FACEBOOK_TIMEOUT', facebook_config.get('timeout', 30)))
            )
        except ValueError as e:
            raise ConfigurationError(f"Invalid Facebook configuration: {e}")
    
    def get_analysis_config(self) -> AnalysisConfig:
        """
        Load analysis configuration.
        
        Returns:
            AnalysisConfig: Analysis configuration
        """
        analysis_config = self._config_data.get('analysis', {})
        
        return AnalysisConfig(
            positive_threshold=float(self._get_config_value('POSITIVE_THRESHOLD', analysis_config.get('positive_threshold', 0.05))),
            negative_threshold=float(self._get_config_value('NEGATIVE_THRESHOLD', analysis_config.get('negative_threshold', -0.05))),
            max_comments_per_request=int(self._get_config_value('MAX_COMMENTS_PER_REQUEST', analysis_config.get('max_comments_per_request', 100))),
            rate_limit_delay=float(self._get_config_value('RATE_LIMIT_DELAY', analysis_config.get('rate_limit_delay', 1.0))),
            include_replies=self._get_config_value('INCLUDE_REPLIES', analysis_config.get('include_replies', False), bool),
            min_comment_length=int(self._get_config_value('MIN_COMMENT_LENGTH', analysis_config.get('min_comment_length', 1))),
            enable_emoji_analysis=self._get_config_value('ENABLE_EMOJI_ANALYSIS', analysis_config.get('enable_emoji_analysis', True), bool)
        )
    
    def get_export_config(self) -> ExportConfig:
        """
        Load export configuration.
        
        Returns:
            ExportConfig: Export configuration
        """
        export_config = self._config_data.get('export', {})
        
        return ExportConfig(
            format=self._get_config_value('EXPORT_FORMAT', export_config.get('format', 'csv')),
            include_raw_data=self._get_config_value('INCLUDE_RAW_DATA', export_config.get('include_raw_data', True), bool),
            include_metadata=self._get_config_value('INCLUDE_METADATA', export_config.get('include_metadata', True), bool),
            output_directory=self._get_config_value('OUTPUT_DIRECTORY', export_config.get('output_directory', '.')),
            filename_prefix=self._get_config_value('FILENAME_PREFIX', export_config.get('filename_prefix', 'facebook_analysis'))
        )
    
    def _get_config_value(self, env_key: str, default_value: Any, value_type: type = str) -> Any:
        """
        Get configuration value from environment variable or default.
        
        Args:
            env_key: Environment variable key
            default_value: Default value if not found
            value_type: Type to convert the value to
            
        Returns:
            Configuration value
        """
        env_value = os.getenv(env_key)
        
        if env_value is not None:
            if value_type is bool:
                return env_value.lower() in ('true', '1', 'yes', 'on')
            return value_type(env_value)
        
        return default_value
    
    def save_config(self, config_file: str = None) -> None:
        """
        Save current configuration to YAML file.
        
        Args:
            config_file: Path to save configuration file
        """
        output_file = config_file or self.config_file or 'config.yaml'
        
        config_data = {
            'facebook': asdict(self.get_facebook_config()),
            'analysis': asdict(self.get_analysis_config()),
            'export': asdict(self.get_export_config())
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                yaml.dump(config_data, file, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def validate_config(self) -> bool:
        """
        Validate all configuration settings.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            facebook_config = self.get_facebook_config()
            analysis_config = self.get_analysis_config()
            export_config = self.get_export_config()
            
            # Validate Facebook config
            if not facebook_config.access_token:
                raise ConfigurationError("Facebook access token is required")
            
            # Validate analysis config
            if analysis_config.positive_threshold <= analysis_config.negative_threshold:
                raise ConfigurationError("Positive threshold must be greater than negative threshold")
            
            if analysis_config.max_comments_per_request <= 0:
                raise ConfigurationError("Max comments per request must be positive")
            
            # Validate export config
            valid_formats = ['csv', 'json', 'excel']
            if export_config.format not in valid_formats:
                raise ConfigurationError(f"Export format must be one of: {valid_formats}")
            
            return True
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Configuration validation failed: {e}")


def load_config(config_file: str = None) -> ConfigManager:
    """
    Load configuration with default settings.
    
    Args:
        config_file: Path to configuration file (optional)
        
    Returns:
        ConfigManager: Configured manager instance
    """
    return ConfigManager(config_file)
