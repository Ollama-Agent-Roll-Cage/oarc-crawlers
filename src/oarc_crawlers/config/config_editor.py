"""
Interactive configuration editor for OARC Crawlers.

This module provides a command-line interface for editing configuration settings
using PyInquirer for an interactive experience.
"""

import configparser
from pathlib import Path
from typing import Any, Dict

from click import clear, echo, style
from PyInquirer import Separator, prompt

from oarc_crawlers.config.config import Config
from oarc_crawlers.config.config_manager import ConfigManager
from oarc_crawlers.config.config_validators import NumberValidator, PathValidator
from oarc_crawlers.decorators.singleton import singleton
from oarc_crawlers.utils.const import CONFIG_SECTION, DEFAULT_CONFIG_FILENAME
from oarc_crawlers.utils.paths import Paths


@singleton
class ConfigEditor:
    """Interactive UI for editing OARC Crawlers configuration."""
    
    def __init__(self):
        """Initialize the configuration editor."""
        # Initialize with ConfigManager class directly using singleton instantiation
        self.manager = ConfigManager()
        self.current_config = self.manager.get_current_config()
        self.config_details = self.manager.get_config_details()
    
    def is_config_changed(self) -> bool:
        """Check if the current config differs from saved/default config."""
        orig_config = Config()
        for key, value in self.current_config.items():
            orig_value = orig_config.get(key)
            if str(value) != str(orig_value):
                return True
        return False
    
    def main_menu(self) -> None:
        """Display the main configuration menu."""
        echo(style("\nOARC Crawlers Configuration Editor", fg='green', bold=True))
        
        # Create menu options
        questions = [
            {
                'type': 'list',
                'name': 'action',
                'message': 'Select an action:',
                'choices': [
                    {'name': 'Edit configuration settings', 'value': 'edit'},
                    {'name': 'Save current configuration', 'value': 'save'},
                    {'name': 'Reset to defaults', 'value': 'reset'},
                    {'name': 'Show current configuration', 'value': 'show'},
                    Separator(),
                    {'name': 'Exit', 'value': 'exit'}
                ]
            }
        ]
        
        answers = prompt(questions)
        if not answers or 'action' not in answers:
            return
            
        action = answers['action']
        
        # Using match-case instead of if-elif
        match action:
            case 'edit':
                self.edit_settings()
            case 'save':
                self.save_changes(self.current_config)
            case 'reset':
                if self.confirm_reset():
                    self.reset_to_defaults()
                    echo(style("All settings reset to defaults.", fg='green'))
                    self.main_menu()
            case 'show':
                self.manager.display_config_info()
                self.main_menu()
            case 'exit':
                if self.is_config_changed():
                    questions = [
                        {
                            'type': 'confirm',
                            'name': 'save',
                            'message': 'You have unsaved changes. Save before exiting?',
                            'default': True
                        }
                    ]
                    answers = prompt(questions)
                    if answers.get('save', False):
                        self.save_changes(self.current_config)
                return
    
    def edit_settings(self) -> None:
        """Present a menu to select which setting to edit."""
        choices = []
        for key in self.current_config.keys():
            description = self.config_details.get(key, {}).get("description", "")
            choices.append({
                'name': f"{key}: {self.current_config[key]} - {description}",
                'value': key
            })
        
        choices.append(Separator())
        choices.append({'name': 'Back to main menu', 'value': 'back'})
        
        questions = [
            {
                'type': 'list',
                'name': 'setting',
                'message': 'Select a setting to edit:',
                'choices': choices
            }
        ]
        
        answers = prompt(questions)
        if not answers or 'setting' not in answers:
            return
            
        key = answers['setting']
        if key == 'back':
            self.main_menu()
            return
            
        self.edit_setting(key)
        self.edit_settings()  # Return to settings list
    
    def edit_setting(self, key: str) -> None:
        """Edit a specific setting using appropriate input type."""
        setting_type = self.config_details.get(key, {}).get("type", "string")
        description = self.config_details.get(key, {}).get("description", "")
        help_text = self.config_details.get(key, {}).get("help", "")
        
        # Construct a message with description and help
        message = f"Enter {key} ({description})"
        if help_text:
            message += f"\n{help_text}"
            
        if setting_type == "select":
            options = self.config_details.get(key, {}).get("options", [])
            questions = [
                {
                    'type': 'list',
                    'name': 'value',
                    'message': message,
                    'choices': options,
                    'default': self.current_config[key]
                }
            ]
        elif setting_type == "int":
            value_range = self.config_details.get(key, {}).get("range", (0, 100))
            questions = [
                {
                    'type': 'input',
                    'name': 'value',
                    'message': message,
                    'default': str(self.current_config[key]),
                    'validate': lambda document: NumberValidator().validate(
                        document, min_val=value_range[0], max_val=value_range[1]
                    )
                }
            ]
        elif setting_type == "path":
            questions = [
                {
                    'type': 'input',
                    'name': 'value',
                    'message': message,
                    'default': str(self.current_config[key]),
                    'validate': PathValidator()
                }
            ]
        else:  # string or other
            questions = [
                {
                    'type': 'input',
                    'name': 'value',
                    'message': message,
                    'default': str(self.current_config[key])
                }
            ]
            
        answers = prompt(questions)
        if not answers or 'value' not in answers:
            return
            
        value = answers['value']
        
        # Type conversion if needed
        if setting_type == "int":
            value = int(value)
        elif setting_type == "path":
            path = Path(value).expanduser().resolve()
            if not path.exists():
                questions = [
                    {
                        'type': 'confirm',
                        'name': 'create',
                        'message': f"Directory {path} doesn't exist. Create it?",
                        'default': True
                    }
                ]
                create_answer = prompt(questions)
                if create_answer.get('create', False):
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                        echo(style(f"Created directory: {path}", fg='green'))
                    except Exception as e:
                        echo(style(f"Error creating directory: {e}", fg='red'))
            value = str(path)
            
        self.current_config[key] = value
    
    def confirm_reset(self) -> bool:
        """Confirm if user wants to reset to defaults."""
        questions = [
            {
                'type': 'confirm',
                'name': 'reset',
                'message': 'Reset all settings to defaults?',
                'default': False
            }
        ]
        answers = prompt(questions)
        return answers.get('reset', False)
    
    def reset_to_defaults(self) -> None:
        """Reset all values to their defaults."""
        config = Config()
        for key, value in config.DEFAULTS.items():
            if hasattr(value, "__str__"):
                self.current_config[key] = str(value)
            else:
                self.current_config[key] = value
    
    def save_changes(self, edited_values: Dict[str, Any]) -> bool:
        """Save changes to configuration file."""
        # Find or create config file
        config_file = self.manager.find_config_file()
        if not config_file:
            config_file = Paths.ensure_config_dir() / DEFAULT_CONFIG_FILENAME
        
        # Create/update config file
        parser = configparser.ConfigParser()
        if config_file.exists():
            parser.read(config_file)
        
        if CONFIG_SECTION not in parser:
            parser[CONFIG_SECTION] = {}
        
        # Update with edited values 
        for key, value in edited_values.items():
            parser[CONFIG_SECTION][key] = str(value)
            
        # Write to file
        try:
            with open(config_file, 'w') as f:
                parser.write(f)
            
            echo(style("\nConfiguration saved successfully!", fg='green'))
            
            # Ask if user wants to update environment variables
            questions = [
                {
                    'type': 'confirm',
                    'name': 'set_env',
                    'message': 'Do you want to also set these as persistent environment variables?',
                    'default': False
                }
            ]
            answers = prompt(questions)
            
            if answers.get('set_env', False):
                self.manager.update_env_vars(edited_values)
            
            return True
        except Exception as e:
            echo(style(f"Error saving config: {e}", fg='red'))
            return False
    
    def run(self) -> None:
        """Run the interactive configuration editor."""
        try:
            clear()
            self.main_menu()
        except KeyboardInterrupt:
            echo(style("\nOperation cancelled by user.", fg='yellow'))
        finally:
            echo(style("\nExiting configuration editor.", fg='blue'))
