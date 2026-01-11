from dataclasses import dataclass
import flet as ft

@dataclass
class ThemeColors:
    window_bg: str
    body_bg: str
    text_primary: str
    text_secondary: str
    border: str
    
    # Title Bar
    title_bar_gradient_start: str
    title_bar_gradient_end: str
    title_bar_border: str
    title_bar_text: str
    
    # Sidebar
    sidebar_bg: str
    sidebar_border: str
    sidebar_item_hover: str
    sidebar_item_active: str
    sidebar_text: str
    sidebar_text_active: str
    
    # Components
    panel_bg: str
    panel_border: str
    button_gradient_start: str
    button_gradient_end: str
    button_border: str
    button_text: str
    
    # Utilities
    error: str
    primary: str

class Theme:
    """Base class for themes"""
    colors: ThemeColors
    font_family: str = "Segoe UI, Tahoma, Geneva, Verdana, sans-serif"

class Theme2010s(Theme):
    """
    Frutiger theme
    Characterized by:
    - Blue gradients
    - Subtle shadows and borders
    - Skeuomorphic elements
    """
    colors = ThemeColors(
        window_bg="#ecf0f1",
        body_bg="#ecf0f1",
        text_primary="#2c3e50",
        text_secondary="#7f8c8d",
        border="#7f8c8d",
        
        # Shiny Blue Title Bar
        title_bar_gradient_start="#4a90e2",
        title_bar_gradient_end="#357abd",
        title_bar_border="#2c5aa0",
        title_bar_text="#ffffff",
        
        # Sidebar with soft gray
        sidebar_bg="#d5dbdb",
        sidebar_border="#95a5a6",
        sidebar_item_hover="#c5d1d2",
        sidebar_item_active="#3498db",
        sidebar_text="#2c3e50",
        sidebar_text_active="#ffffff",
        
        # Content Panels
        panel_bg="#f8f9fa",
        panel_border="#bdc3c7",
        
        # Glossy Buttons
        button_gradient_start="#52a8ec",
        button_gradient_end="#3498db",
        button_border="#2980b9",
        button_text="#ffffff",
        
        # Utilities
        error="#e74c3c",
        primary="#3498db"
    )

# Global current theme instance
current_theme = Theme2010s()
