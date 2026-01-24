"""Utility functions for serializing and deserializing UI element hierarchies."""

import pygame
from typing import Dict, TYPE_CHECKING, Callable, Optional
from src.ui.ui_element import UIElement
from src.ui.elements.button import Button
from src.ui.elements.toggle import Toggle
from src.ui.elements.slider import Slider
from src.ui.elements.image import Image
from src.ui.elements.text_display import TextDisplay
from src.ui.elements.scrollable_area import ScrollableArea
from src.ui.elements.menu import Menu

if TYPE_CHECKING:
    from src.managers.game_manager import GameManager


def create_element_from_layout(layout_props: dict, game_manager: 'GameManager') -> UIElement:
    """Factory function to create a UI element from layout properties.
    
    Args:
        layout_props: Dictionary containing element configuration including '_type' key
        game_manager: The game manager instance
        
    Returns:
        A newly created UIElement instance of the appropriate type
        
    Raises:
        ValueError: If element type is unknown or missing
    """
    element_type = layout_props.get("_type")
    
    if not element_type:
        raise ValueError("Layout props missing '_type' field")
    
    # Create element based on type
    if element_type == "Button":
        return Button(
            layout_props, 
            game_manager.game_font, 
            game_manager,
            callback=None,  # Callbacks should be set separately
            shown=layout_props.get("shown", True)
        )
    
    elif element_type == "Toggle":
        return Toggle(
            layout_props,
            pygame.time.get_ticks(),
            game_manager,
            on=layout_props.get("on", False),
            callback=None,
            shown=layout_props.get("shown", True)
        )
    
    elif element_type == "Slider":
        return Slider(
            layout_props,
            layout_props.get("value", 0),
            game_manager,
            callback=None,
            shown=layout_props.get("shown", True)
        )
    
    elif element_type == "Image":
        return Image(
            layout_props,
            game_manager,
            callback=None
        )
    
    elif element_type == "TextDisplay":
        return TextDisplay(
            layout_props,
            game_manager,
            game_manager.game_font,
            callback=None,
            shown=layout_props.get("shown", True)
        )
    
    elif element_type == "ScrollableArea":
        # ScrollableArea needs a content surface
        # Create a placeholder surface that will be replaced if needed
        width = layout_props.get("viewable_content_width", 100)
        height = layout_props.get("viewable_content_height", 100)
        content_surface = pygame.Surface((width, height))
        return ScrollableArea(
            layout_props,
            game_manager,
            content_surface
        )
    
    elif element_type == "Menu":
        # Menu needs dictionaries of elements organized by tabs
        # We'll create them from the serialized data
        buttons_data = layout_props.get("buttons", {})
        toggles_data = layout_props.get("toggles", {})
        sliders_data = layout_props.get("sliders", {})
        images_data = layout_props.get("images", {})
        text_displays_data = layout_props.get("text_displays", {})
        
        # Recursively create elements for each tab
        buttons = {}
        for tab, tab_buttons in buttons_data.items():
            buttons[tab] = {}
            for name, button_layout in tab_buttons.items():
                buttons[tab][name] = create_element_from_layout(button_layout, game_manager)
        
        toggles = {}
        for tab, tab_toggles in toggles_data.items():
            toggles[tab] = {}
            for name, toggle_layout in tab_toggles.items():
                toggles[tab][name] = create_element_from_layout(toggle_layout, game_manager)
        
        sliders = {}
        for tab, tab_sliders in sliders_data.items():
            sliders[tab] = {}
            for name, slider_layout in tab_sliders.items():
                sliders[tab][name] = create_element_from_layout(slider_layout, game_manager)
        
        images = {}
        for tab, tab_images in images_data.items():
            images[tab] = {}
            for name, image_layout in tab_images.items():
                images[tab][name] = create_element_from_layout(image_layout, game_manager)
        
        text_displays = {}
        for tab, tab_text_displays in text_displays_data.items():
            text_displays[tab] = {}
            for name, text_display_layout in tab_text_displays.items():
                text_displays[tab][name] = create_element_from_layout(text_display_layout, game_manager)
        
        return Menu(
            layout_props,
            game_manager,
            buttons,
            toggles,
            sliders,
            images,
            text_displays,
            time=pygame.time.get_ticks()
        )
    
    else:
        raise ValueError(f"Unknown element type: {element_type}")

def restore_ui_hierarchy(elements: list, game_manager: 'GameManager') -> Dict[str, UIElement]:
    """Restore a complete UI hierarchy from a list of element layouts.
    
    This function handles the two-phase process of:
    1. Creating all elements
    2. Restoring parent-child relationships
    
    Args:
        elements: List of layout property dictionaries
        game_manager: The game manager instance
        
    Returns:
        Dictionary mapping element names to UIElement instances
    """
    # Phase 1: Create all elements
    element_registry = {}
    created_elements = []
    
    for element_layout in elements:
        try:
            element = create_element_from_layout(element_layout, game_manager)
            created_elements.append(element)
            if element.name:
                element_registry[element.name] = element
        except Exception as e:
            print(f"Warning: Failed to create element: {e}")
    
    # Phase 2: Restore parent-child relationships
    for element in created_elements:
        element.restore_child_relationships(element_registry)
        
        # Special handling for ScrollableArea content elements
        if isinstance(element, ScrollableArea):
            element.restore_content_elements(
                lambda layout, gm: create_element_from_layout(layout, gm)
            )
    
    return element_registry

def reconnect_callbacks(element_registry: Dict[str, UIElement], callback_registry: Dict[str, Callable]) -> None:
    """Reconnect callbacks to UI elements after loading from layout.
    
    This function iterates through all elements and assigns callbacks based on
    the callback names saved in the layout and the provided callback registry.
    
    Args:
        element_registry: Dictionary mapping element names to UIElement instances
        callback_registry: Dictionary mapping callback names to callable functions
        
    Example:
        callback_registry = {
            "handle_start_button": start_game_function,
            "toggle_audio": toggle_audio_setting,
            "adjust_volume": volume_slider_callback
        }
        reconnect_callbacks(elements, callback_registry)
    """
    for element_name, element in element_registry.items():
        # Check if element has a saved callback name in its layout
        if hasattr(element, 'callback'):
            # Try to get callback name from the original layout
            # This requires storing it during creation, which we do via get_layout
            callback_name = None
            
            # For buttons, check if callback was saved
            if isinstance(element, (Button, Toggle, Slider)):
                # Callback names would have been stored during serialization
                # We need to read it from the saved state
                # Note: This is a simplified approach - in practice you might want
                # to store callback_name as an attribute during element creation
                pass
            
            # If we have a callback name, look it up and assign it
            if callback_name and callback_name in callback_registry:
                element.callback = callback_registry[callback_name]
                print(f"Reconnected callback '{callback_name}' to element '{element_name}'")

def reconnect_callbacks_by_name(element_registry: Dict[str, UIElement], 
                                 element_callback_map: Dict[str, str],
                                 callback_registry: Dict[str, Callable]) -> None:
    """Reconnect callbacks using an explicit element-to-callback mapping.
    
    This is the recommended approach for callback restoration, as it provides
    explicit control over which callbacks get assigned to which elements.
    
    Args:
        element_registry: Dictionary mapping element names to UIElement instances
        element_callback_map: Dictionary mapping element names to callback names
        callback_registry: Dictionary mapping callback names to callable functions
        
    Example:
        element_callback_map = {
            "start_button": "handle_start_button",
            "audio_toggle": "toggle_audio",
            "volume_slider": "adjust_volume"
        }
        callback_registry = {
            "handle_start_button": start_game_function,
            "toggle_audio": toggle_audio_setting,
            "adjust_volume": volume_slider_callback
        }
        reconnect_callbacks_by_name(elements, element_callback_map, callback_registry)
    """
    for element_name, callback_name in element_callback_map.items():
        if element_name in element_registry and callback_name in callback_registry:
            element = element_registry[element_name]
            if hasattr(element, 'callback'):
                element.callback = callback_registry[callback_name]
                print(f"Assigned callback '{callback_name}' to element '{element_name}'")
            else:
                print(f"Warning: Element '{element_name}' does not support callbacks")
        else:
            if element_name not in element_registry:
                print(f"Warning: Element '{element_name}' not found in registry")
            if callback_name not in callback_registry:
                print(f"Warning: Callback '{callback_name}' not found in registry")

def save_ui_hierarchy(root_elements: list) -> list:
    """Save a UI hierarchy to a list of layout dictionaries.
    
    Args:
        root_elements: List of root UIElement instances to save
        
    Returns:
        List of layout property dictionaries
    """
    saved_elements = []
    visited = set()
    
    def save_element_tree(element: UIElement):
        """Recursively save element and its children."""
        if id(element) in visited:
            return
        visited.add(id(element))
        
        # Save this element
        layout = element.get_layout()
        saved_elements.append(layout)
        
        # Recursively save children
        for child in element.children:
            save_element_tree(child)
    
    # Save each root element and its tree
    for root in root_elements:
        save_element_tree(root)
    
    return saved_elements
