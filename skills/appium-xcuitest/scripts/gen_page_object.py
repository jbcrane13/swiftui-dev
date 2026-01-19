#!/usr/bin/env python3
"""
Generate Appium Page Object from a SwiftUI view file.

Scans a SwiftUI file for accessibility identifiers and generates
a Python Page Object class for Appium testing.

Usage:
    python3 gen_page_object.py <swift_file> [--output <dir>] [--class-name <name>]

Options:
    --output      Output directory (default: ./page_objects)
    --class-name  Page object class name (default: derived from file)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UIElement:
    identifier: str
    element_type: str
    property_name: str


# Map SwiftUI element types to Appium element types
ELEMENT_TYPE_MAP = {
    'button': 'XCUIElementTypeButton',
    'textfield': 'XCUIElementTypeTextField',
    'securefield': 'XCUIElementTypeSecureTextField',
    'toggle': 'XCUIElementTypeSwitch',
    'picker': 'XCUIElementTypePicker',
    'slider': 'XCUIElementTypeSlider',
    'stepper': 'XCUIElementTypeStepper',
    'link': 'XCUIElementTypeLink',
    'text': 'XCUIElementTypeStaticText',
    'image': 'XCUIElementTypeImage',
    'cell': 'XCUIElementTypeCell',
    'row': 'XCUIElementTypeCell',
}


def extract_accessibility_ids(swift_content: str) -> List[UIElement]:
    """Extract accessibility identifiers from Swift content."""
    elements = []

    # Pattern to match .accessibilityIdentifier("...")
    pattern = r'\.accessibilityIdentifier\s*\(\s*"([^"]+)"\s*\)'

    for match in re.finditer(pattern, swift_content):
        identifier = match.group(1)

        # Parse the identifier to determine element type
        parts = identifier.split('_')
        if len(parts) >= 2:
            element_hint = parts[1].lower()
        else:
            element_hint = 'button'

        # Determine element type from identifier naming convention
        element_type = ELEMENT_TYPE_MAP.get(element_hint, 'XCUIElementTypeOther')

        # Generate property name from identifier
        property_name = identifier.replace('-', '_')

        elements.append(UIElement(
            identifier=identifier,
            element_type=element_type,
            property_name=property_name
        ))

    return elements


def generate_page_object(class_name: str, elements: List[UIElement]) -> str:
    """Generate Python Page Object class."""
    # Header
    code = f'''"""
Page Object for {class_name}

Auto-generated from SwiftUI accessibility identifiers.
"""

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class {class_name}:
    """Page Object representing the {class_name.replace('Page', '')} screen."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

'''

    # Element locators
    code += '    # Element Locators\n'
    for element in elements:
        code += f'    {element.property_name.upper()}_LOCATOR = (AppiumBy.ACCESSIBILITY_ID, "{element.identifier}")\n'

    code += '\n'

    # Element properties
    code += '    # Element Properties\n'
    for element in elements:
        prop_name = element.property_name
        locator_name = element.property_name.upper() + '_LOCATOR'
        code += f'''    @property
    def {prop_name}(self):
        """Get the {element.identifier} element."""
        return self.wait.until(
            EC.presence_of_element_located(self.{locator_name})
        )

'''

    # Common actions based on element types
    code += '    # Actions\n'
    for element in elements:
        if 'button' in element.element_type.lower() or 'link' in element.element_type.lower():
            code += f'''    def tap_{element.property_name}(self):
        """Tap the {element.identifier} button."""
        self.{element.property_name}.click()

'''
        elif 'textfield' in element.element_type.lower():
            code += f'''    def enter_{element.property_name}(self, text: str):
        """Enter text into {element.identifier}."""
        element = self.{element.property_name}
        element.clear()
        element.send_keys(text)

'''
        elif 'switch' in element.element_type.lower():
            code += f'''    def toggle_{element.property_name}(self):
        """Toggle the {element.identifier} switch."""
        self.{element.property_name}.click()

    def is_{element.property_name}_enabled(self) -> bool:
        """Check if {element.identifier} is enabled."""
        return self.{element.property_name}.get_attribute('value') == '1'

'''

    # Verification method
    code += '''    def is_displayed(self) -> bool:
        """Check if the page is displayed."""
        try:
            return len(self.driver.find_elements(*self.'''

    if elements:
        code += f'{elements[0].property_name.upper()}_LOCATOR)) > 0\n'
    else:
        code += 'LOCATOR)) > 0\n'

    code += '''        except:
            return False
'''

    return code


def derive_class_name(file_path: Path) -> str:
    """Derive page object class name from file path."""
    name = file_path.stem
    # Add 'Page' suffix if not present
    if not name.endswith('Page'):
        name = name.replace('View', 'Page').replace('Screen', 'Page')
        if not name.endswith('Page'):
            name += 'Page'
    return name


def main():
    parser = argparse.ArgumentParser(description='Generate Appium Page Object from SwiftUI')
    parser.add_argument('swift_file', help='SwiftUI file to process')
    parser.add_argument('--output', default='./page_objects', help='Output directory')
    parser.add_argument('--class-name', help='Page object class name')
    args = parser.parse_args()

    file_path = Path(args.swift_file)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not file_path.suffix == '.swift':
        print(f"Warning: File does not have .swift extension", file=sys.stderr)

    # Read Swift file
    content = file_path.read_text()

    # Extract accessibility identifiers
    elements = extract_accessibility_ids(content)

    if not elements:
        print(f"No accessibility identifiers found in {file_path}")
        print("Ensure your SwiftUI views use .accessibilityIdentifier(\"...\")")
        sys.exit(0)

    print(f"Found {len(elements)} accessibility identifiers")

    # Determine class name
    class_name = args.class_name or derive_class_name(file_path)

    # Generate page object
    page_object_code = generate_page_object(class_name, elements)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write page object file
    output_file = output_dir / f'{class_name.lower()}.py'
    output_file.write_text(page_object_code)

    print(f"✅ Generated: {output_file}")
    print(f"\nElements included:")
    for element in elements:
        print(f"  - {element.property_name} ({element.element_type})")


if __name__ == '__main__':
    main()
