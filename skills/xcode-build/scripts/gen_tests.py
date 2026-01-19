#!/usr/bin/env python3
"""
gen_tests.py - Generate unit or UI test files.

Usage:
    python gen_tests.py TaskTests --for Task --path ./MyAppTests
    python gen_tests.py LoginViewUITests --ui --path ./MyAppUITests
    python gen_tests.py TaskStateTests --for TaskState --path ./MyAppTests
"""

import argparse
import sys
from pathlib import Path
from xcode_utils import to_pascal_case, to_camel_case, to_snake_case


def create_unit_test(name: str, target_type: str = None) -> str:
    """Generate unit test file using Swift Testing framework."""
    
    if target_type:
        target_var = to_camel_case(target_type)
        test_content = f'''
    @Test
    @MainActor
    func testInitialization() {{
        let {target_var} = {target_type}()
        
        // TODO: Add assertions
        #expect({target_var} != nil)
    }}
    
    @Test
    @MainActor
    func testExample() async {{
        let {target_var} = {target_type}()
        
        // TODO: Test behavior
    }}'''
    else:
        test_content = '''
    @Test
    func testExample() {
        // TODO: Add test
        #expect(true)
    }'''
    
    return f'''import Testing
@testable import MyApp  // TODO: Update module name

@Suite("{name}")
struct {name} {{{test_content}
}}
'''


def create_swiftdata_test(name: str, model_type: str) -> str:
    """Generate SwiftData model test file."""
    
    model_var = to_camel_case(model_type)
    
    return f'''import Testing
import SwiftData
@testable import MyApp  // TODO: Update module name

@Suite("{name}")
struct {name} {{
    
    @Test
    @MainActor
    func testCreate{model_type}() throws {{
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        let container = try ModelContainer(for: {model_type}.self, configurations: config)
        let context = container.mainContext
        
        let {model_var} = {model_type}()  // TODO: Add init params
        context.insert({model_var})
        
        let descriptor = FetchDescriptor<{model_type}>()
        let items = try context.fetch(descriptor)
        
        #expect(items.count == 1)
    }}
    
    @Test
    @MainActor
    func testDelete{model_type}() throws {{
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        let container = try ModelContainer(for: {model_type}.self, configurations: config)
        let context = container.mainContext
        
        let {model_var} = {model_type}()  // TODO: Add init params
        context.insert({model_var})
        context.delete({model_var})
        
        let descriptor = FetchDescriptor<{model_type}>()
        let items = try context.fetch(descriptor)
        
        #expect(items.isEmpty)
    }}
}}
'''


def create_ui_test(name: str) -> str:
    """Generate XCUITest file."""
    
    screen_name = name.replace("UITests", "").replace("Tests", "")
    screen_id = to_snake_case(screen_name)
    
    return f'''import XCTest

final class {name}: XCTestCase {{
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {{
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }}
    
    override func tearDownWithError() throws {{
        app = nil
    }}
    
    func testScreenExists() throws {{
        let screen = app.otherElements["screen_{screen_id}"]
        XCTAssertTrue(screen.waitForExistence(timeout: 5))
    }}
    
    func testExample() throws {{
        // TODO: Add UI test
        // Example:
        // let button = app.buttons["{screen_id}_button_action"]
        // XCTAssertTrue(button.exists)
        // button.tap()
    }}
}}
'''


def main():
    parser = argparse.ArgumentParser(description="Generate test file")
    parser.add_argument("name", help="Test class name (e.g., TaskTests)")
    parser.add_argument("--for", dest="target", help="Target type being tested")
    parser.add_argument("--path", "-p", default=".", help="Output directory")
    parser.add_argument("--ui", action="store_true", help="Generate XCUITest instead of unit test")
    parser.add_argument("--swiftdata", action="store_true", help="Generate SwiftData model test")
    args = parser.parse_args()

    name = to_pascal_case(args.name)
    if not name.endswith("Tests"):
        name += "Tests"

    output_path = Path(args.path)
    if not output_path.exists():
        output_path.mkdir(parents=True)

    file_path = output_path / f"{name}.swift"
    
    if file_path.exists():
        print(f"Error: File already exists: {file_path}", file=sys.stderr)
        sys.exit(1)

    if args.ui:
        content = create_ui_test(name)
    elif args.swiftdata and args.target:
        content = create_swiftdata_test(name, args.target)
    else:
        content = create_unit_test(name, args.target)

    file_path.write_text(content)
    print(f"✅ Created: {file_path}")


if __name__ == "__main__":
    main()
