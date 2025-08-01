"""
CONFIGO Settings Menu
=====================

A modern settings interface for CONFIGO that allows users to:
- Change UI themes
- Configure UI preferences
- Manage memory settings
- Set debug/logging options
- Configure AI/LLM settings
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ui.modern_terminal_ui import ModernTerminalUI, UIConfig, Theme
from rich import box

logger = logging.getLogger(__name__)

class SettingType(Enum):
    """Types of settings."""
    THEME = "theme"
    ANIMATION = "animation"
    EMOJI = "emoji"
    DEBUG = "debug"
    LOGGING = "logging"
    MEMORY = "memory"
    AI = "ai"

@dataclass
class Setting:
    """A single setting configuration."""
    name: str
    description: str
    type: SettingType
    current_value: Any
    options: Optional[list] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

class SettingsMenu:
    """Modern settings menu for CONFIGO."""
    
    def __init__(self, ui: ModernTerminalUI):
        self.ui = ui
        self.settings = self._initialize_settings()
    
    def _initialize_settings(self) -> Dict[str, Setting]:
        """Initialize all available settings."""
        return {
            "theme": Setting(
                name="UI Theme",
                description="Choose the visual theme for CONFIGO",
                type=SettingType.THEME,
                current_value=Theme.DEFAULT,
                options=[
                    ("Default", Theme.DEFAULT, "Modern cyan theme with animations"),
                    ("Minimal", Theme.MINIMAL, "Clean white theme for low-resource terminals"),
                    ("Developer", Theme.DEVELOPER, "Bright blue theme for development focus"),
                    ("Verbose", Theme.VERBOSE, "Green theme with detailed output"),
                    ("Dark", Theme.DARK, "High contrast dark theme"),
                    ("Light", Theme.LIGHT, "Light theme for bright environments")
                ]
            ),
            "animation": Setting(
                name="Animations",
                description="Enable/disable UI animations",
                type=SettingType.ANIMATION,
                current_value=True,
                options=[
                    ("Enabled", True, "Show smooth animations and transitions"),
                    ("Disabled", False, "Minimal animations for performance")
                ]
            ),
            "emoji": Setting(
                name="Emoji Support",
                description="Show emojis and icons in the interface",
                type=SettingType.EMOJI,
                current_value=True,
                options=[
                    ("Enabled", True, "Show emojis and visual icons"),
                    ("Disabled", False, "Text-only interface")
                ]
            ),
            "debug": Setting(
                name="Debug Mode",
                description="Show detailed debug information",
                type=SettingType.DEBUG,
                current_value=False,
                options=[
                    ("Enabled", True, "Show debug logs and technical details"),
                    ("Disabled", False, "User-friendly output only")
                ]
            ),
            "logging": Setting(
                name="Log Level",
                description="Set the logging verbosity level",
                type=SettingType.LOGGING,
                current_value="INFO",
                options=[
                    ("DEBUG", "DEBUG", "Most verbose logging"),
                    ("INFO", "INFO", "Standard information logging"),
                    ("WARNING", "WARNING", "Warnings and errors only"),
                    ("ERROR", "ERROR", "Errors only")
                ]
            )
        }
    
    def show_settings_menu(self) -> None:
        """Display the main settings menu."""
        while True:
            self.ui.clear_screen()
            self.ui.show_banner()
            self.ui.show_mode_header("Settings", "Configure CONFIGO preferences")
            
            # Show current settings summary
            self._show_settings_summary()
            
            # Show menu options
            options = [
                ("🎨 Change Theme", "Modify the UI visual theme"),
                ("⚡ Animation Settings", "Configure UI animations"),
                ("🔧 Debug Settings", "Configure debug and logging options"),
                ("💾 Memory Settings", "Configure memory and storage"),
                ("🤖 AI Settings", "Configure AI and LLM options"),
                ("📊 Reset to Defaults", "Reset all settings to default values"),
                ("🔙 Back to Main Menu", "Return to the main menu")
            ]
            
            from rich.table import Table
            table = Table(
                title="⚙️ Settings Menu",
                box=box.ROUNDED if self.ui.config.rounded_corners else box.SIMPLE,
                border_style=self.ui.config.colors['panel_border'],
                title_style=f"bold {self.ui.config.colors['info']}"
            )
            
            table.add_column("Option", style="bold")
            table.add_column("Description", style=self.ui.config.colors['text'])
            table.add_column("Key", style=self.ui.config.colors['primary'])
            
            for i, (name, desc) in enumerate(options, 1):
                table.add_row(name, desc, str(i))
            
            self.ui.console.print(table)
            self.ui.console.print()
            
            choice = self.ui.get_user_input("Select option (1-7): ")
            
            if choice == "1":
                self._change_theme()
            elif choice == "2":
                self._animation_settings()
            elif choice == "3":
                self._debug_settings()
            elif choice == "4":
                self._memory_settings()
            elif choice == "5":
                self._ai_settings()
            elif choice == "6":
                self._reset_to_defaults()
            elif choice == "7":
                break
            else:
                self.ui.show_error_message("Invalid option selected")
    
    def _show_settings_summary(self) -> None:
        """Show a summary of current settings."""
        summary_text = []
        for key, setting in self.settings.items():
            if setting.type == SettingType.THEME:
                value = f"{setting.current_value.value.title()}"
            elif setting.type == SettingType.ANIMATION:
                value = "Enabled" if setting.current_value else "Disabled"
            elif setting.type == SettingType.EMOJI:
                value = "Enabled" if setting.current_value else "Disabled"
            elif setting.type == SettingType.DEBUG:
                value = "Enabled" if setting.current_value else "Disabled"
            elif setting.type == SettingType.LOGGING:
                value = setting.current_value
            else:
                value = str(setting.current_value)
            
            summary_text.append(f"• {setting.name}: {value}")
        
        from rich.panel import Panel
        summary_panel = Panel(
            "\n".join(summary_text),
            title="Current Settings",
            border_style=self.ui.config.colors['info'],
            box=box.ROUNDED if self.ui.config.rounded_corners else box.SIMPLE,
            padding=self.ui.config.panel_padding
        )
        
        self.ui.console.print(summary_panel)
        self.ui.console.print()
    
    def _change_theme(self) -> None:
        """Change the UI theme."""
        self.ui.clear_screen()
        self.ui.show_banner()
        self.ui.show_mode_header("Theme Selection", "Choose your preferred UI theme")
        
        theme_setting = self.settings["theme"]
        
        table = Table(
            title="🎨 Available Themes",
            box=box.ROUNDED if self.ui.config.rounded_corners else box.SIMPLE,
            border_style=self.ui.config.colors['panel_border'],
            title_style=f"bold {self.ui.config.colors['info']}"
        )
        
        table.add_column("Theme", style="bold")
        table.add_column("Description", style=self.ui.config.colors['text'])
        table.add_column("Current", style=self.ui.config.colors['success'])
        table.add_column("Key", style=self.ui.config.colors['primary'])
        
        for i, (name, theme, desc) in enumerate(theme_setting.options, 1):
            current = "✓" if theme == theme_setting.current_value else ""
            table.add_row(name, desc, current, str(i))
        
        self.ui.console.print(table)
        self.ui.console.print()
        
        choice = self.ui.get_user_input(f"Select theme (1-{len(theme_setting.options)}): ")
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(theme_setting.options):
                new_theme = theme_setting.options[choice_idx][1]
                self.settings["theme"].current_value = new_theme
                
                # Update UI config
                self.ui.config.theme = new_theme
                self.ui.config._setup_theme()
                
                self.ui.show_success_message(f"Theme changed to {new_theme.value.title()}!")
            else:
                self.ui.show_error_message("Invalid theme selection")
        except ValueError:
            self.ui.show_error_message("Invalid input")
    
    def _animation_settings(self) -> None:
        """Configure animation settings."""
        self.ui.clear_screen()
        self.ui.show_banner()
        self.ui.show_mode_header("Animation Settings", "Configure UI animations and effects")
        
        anim_setting = self.settings["animation"]
        emoji_setting = self.settings["emoji"]
        
        # Animation toggle
        anim_enabled = self.ui.confirm_action(
            f"Enable animations? (Currently: {'Enabled' if anim_setting.current_value else 'Disabled'})"
        )
        self.settings["animation"].current_value = anim_enabled
        
        # Emoji toggle
        emoji_enabled = self.ui.confirm_action(
            f"Enable emojis? (Currently: {'Enabled' if emoji_setting.current_value else 'Disabled'})"
        )
        self.settings["emoji"].current_value = emoji_enabled
        
        self.ui.show_success_message("Animation settings updated!")
    
    def _debug_settings(self) -> None:
        """Configure debug and logging settings."""
        self.ui.clear_screen()
        self.ui.show_banner()
        self.ui.show_mode_header("Debug Settings", "Configure debug and logging options")
        
        debug_setting = self.settings["debug"]
        logging_setting = self.settings["logging"]
        
        # Debug mode toggle
        debug_enabled = self.ui.confirm_action(
            f"Enable debug mode? (Currently: {'Enabled' if debug_setting.current_value else 'Disabled'})"
        )
        self.settings["debug"].current_value = debug_enabled
        
        # Log level selection
        self.ui.show_info_message("Current log level: " + logging_setting.current_value)
        
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        table = Table(
            title="📊 Log Levels",
            box=box.ROUNDED if self.ui.config.rounded_corners else box.SIMPLE,
            border_style=self.ui.config.colors['panel_border']
        )
        
        table.add_column("Level", style="bold")
        table.add_column("Description", style=self.ui.config.colors['text'])
        table.add_column("Key", style=self.ui.config.colors['primary'])
        
        for i, level in enumerate(log_levels, 1):
            desc = {
                "DEBUG": "Most verbose logging",
                "INFO": "Standard information logging",
                "WARNING": "Warnings and errors only",
                "ERROR": "Errors only"
            }[level]
            current = "✓" if level == logging_setting.current_value else ""
            table.add_row(level, desc, str(i))
        
        self.ui.console.print(table)
        self.ui.console.print()
        
        choice = self.ui.get_user_input("Select log level (1-4): ")
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(log_levels):
                new_level = log_levels[choice_idx]
                self.settings["logging"].current_value = new_level
                self.ui.show_success_message(f"Log level changed to {new_level}!")
            else:
                self.ui.show_error_message("Invalid log level selection")
        except ValueError:
            self.ui.show_error_message("Invalid input")
    
    def _memory_settings(self) -> None:
        """Configure memory settings."""
        self.ui.clear_screen()
        self.ui.show_banner()
        self.ui.show_mode_header("Memory Settings", "Configure memory and storage options")
        
        # TODO: Implement memory settings
        self.ui.show_info_message("Memory settings will be implemented in the future.")
    
    def _ai_settings(self) -> None:
        """Configure AI and LLM settings."""
        self.ui.clear_screen()
        self.ui.show_banner()
        self.ui.show_mode_header("AI Settings", "Configure AI and LLM options")
        
        # TODO: Implement AI settings
        self.ui.show_info_message("AI settings will be implemented in the future.")
    
    def _reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        if self.ui.confirm_action("Are you sure you want to reset all settings to defaults?"):
            self.settings = self._initialize_settings()
            self.ui.show_success_message("All settings reset to defaults!")
        else:
            self.ui.show_info_message("Settings reset cancelled.")
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings as a dictionary."""
        return {key: setting.current_value for key, setting in self.settings.items()}
    
    def apply_settings(self, ui: ModernTerminalUI) -> None:
        """Apply current settings to the UI."""
        # Apply theme
        if "theme" in self.settings:
            ui.config.theme = self.settings["theme"].current_value
            ui.config._setup_theme()
        
        # Apply animation settings
        if "animation" in self.settings:
            ui.config.use_animations = self.settings["animation"].current_value
        
        # Apply emoji settings
        if "emoji" in self.settings:
            ui.config.use_emoji = self.settings["emoji"].current_value 