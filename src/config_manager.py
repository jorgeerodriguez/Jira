"""
Configuration Manager for Jira Reporting System
Handles loading and validation of configuration from config.json
"""

import os
import json
from typing import Dict, Optional, List


class ConfigManager:
    """Manages configuration loading and validation"""
    
    DEFAULT_CONFIG_FILE = "config.json"
    
    REQUIRED_JIRA_KEYS = ["jira_server", "jira_email", "jira_api_token"]
    OPTIONAL_EMAIL_KEYS = ["email_address", "email_password", "smtp_server", "smtp_port"]
    OPTIONAL_SLACK_KEYS = ["slack_webhook_url", "slack_channel"]
    
    def __init__(self, config_file: str = None):
        """
        Initialize the configuration manager
        
        Args:
            config_file: Path to configuration file (defaults to config.json in current directory)
        """
        self.config_file = config_file or self.DEFAULT_CONFIG_FILE
        self.config = None
        
    def load_config(self) -> Optional[Dict]:
        """
        Load configuration from JSON file
        
        Returns:
            Dictionary containing configuration data, or None if loading fails
        """
        config_path = os.path.join(os.getcwd(), self.config_file)
        
        if not os.path.exists(config_path):
            print(f"Error: Configuration file not found at '{config_path}'")
            print("Please create the file with required configuration.")
            return None
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
            # Validate required Jira keys
            if not all(key in config_data for key in self.REQUIRED_JIRA_KEYS):
                missing = [key for key in self.REQUIRED_JIRA_KEYS if key not in config_data]
                print(f"Error: Configuration file is missing required keys: {missing}")
                return None
            
            # Check if API token is not empty
            if not config_data.get("jira_api_token"):
                print("Error: 'jira_api_token' is empty in configuration file.")
                return None
            
            print(f"Successfully loaded configuration from '{config_path}'")
            self.config = config_data
            return config_data
            
        except json.JSONDecodeError as e:
            print(f"Error: Could not parse JSON in configuration file '{config_path}'.")
            print(f"Details: {e}")
            return None
        except Exception as e:
            print(f"Error: An unexpected error occurred while reading '{config_path}'.")
            print(f"Details: {e}")
            return None
    
    def get(self, key: str, default=None):
        """
        Get a configuration value
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if self.config is None:
            self.load_config()
        return self.config.get(key, default) if self.config else default
    
    def get_jira_config(self) -> Dict:
        """Get Jira-specific configuration"""
        if self.config is None:
            self.load_config()
        
        return {
            "server": self.get("jira_server"),
            "email": self.get("jira_email"),
            "api_token": self.get("jira_api_token")
        }
    
    def get_email_config(self) -> Dict:
        """Get email-specific configuration"""
        if self.config is None:
            self.load_config()
        
        return {
            "address": self.get("email_address"),
            "password": self.get("email_password"),
            "smtp_server": self.get("smtp_server", "smtp.gmail.com"),
            "smtp_port": self.get("smtp_port", 587)
        }
    
    def get_slack_config(self) -> Dict:
        """Get Slack-specific configuration"""
        if self.config is None:
            self.load_config()
        
        return {
            "webhook_url": self.get("slack_webhook_url"),
            "channel": self.get("slack_channel", "#general")
        }
    
    def has_email_config(self) -> bool:
        """Check if email configuration is available"""
        email_cfg = self.get_email_config()
        return bool(email_cfg.get("address") and email_cfg.get("password"))
    
    def has_slack_config(self) -> bool:
        """Check if Slack configuration is available"""
        slack_cfg = self.get_slack_config()
        return bool(slack_cfg.get("webhook_url"))
