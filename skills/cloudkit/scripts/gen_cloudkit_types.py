#!/usr/bin/env python3
"""
Generate CloudKit record wrapper types from SwiftData models.

Scans SwiftData @Model classes and generates corresponding CloudKit
CKRecord wrapper structs with type-safe accessors.

Usage:
    python3 gen_cloudkit_types.py <model_file> [--output <dir>]

Options:
    --output    Output directory (default: ./CloudKitTypes)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class ModelProperty:
    name: str
    swift_type: str
    is_optional: bool
    is_relationship: bool
    relationship_type: Optional[str] = None


@dataclass
class SwiftDataModel:
    name: str
    properties: List[ModelProperty]


# Map Swift types to CloudKit-compatible types
TYPE_MAP = {
    'String': ('String', 'as? String ?? ""'),
    'Int': ('Int64', 'as? Int64 ?? 0'),
    'Int64': ('Int64', 'as? Int64 ?? 0'),
    'Double': ('Double', 'as? Double ?? 0.0'),
    'Float': ('Double', 'as? Double ?? 0.0'),
    'Bool': ('Int64', 'as? Int64 == 1'),
    'Date': ('Date', 'as? Date ?? .now'),
    'Data': ('Data', 'as? Data ?? Data()'),
    'URL': ('String', 'as? String').replace('as? String', 'flatMap { URL(string: $0 as? String ?? "") }'),
    'UUID': ('String', 'as? String ?? ""'),
}


def parse_model_file(content: str) -> List[SwiftDataModel]:
    """Parse SwiftData model definitions from Swift content."""
    models = []

    # Find @Model class definitions
    model_pattern = r'@Model\s+(?:final\s+)?class\s+(\w+)\s*(?::\s*[\w,\s]+)?\s*\{'

    for model_match in re.finditer(model_pattern, content):
        model_name = model_match.group(1)
        start_pos = model_match.end()

        # Find the matching closing brace
        brace_count = 1
        end_pos = start_pos
        for i, char in enumerate(content[start_pos:]):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = start_pos + i
                    break

        model_body = content[start_pos:end_pos]
        properties = parse_properties(model_body)

        models.append(SwiftDataModel(
            name=model_name,
            properties=properties
        ))

    return models


def parse_properties(model_body: str) -> List[ModelProperty]:
    """Parse properties from model body."""
    properties = []

    # Pattern for var declarations
    var_pattern = r'(?:@Relationship[^)]*\)\s*)?var\s+(\w+)\s*:\s*([^\n=]+?)(?:\s*=|$|\n)'

    for match in re.finditer(var_pattern, model_body):
        name = match.group(1)
        type_str = match.group(2).strip()

        # Skip computed properties (have get/set)
        if 'get' in type_str or 'set' in type_str:
            continue

        # Check if optional
        is_optional = type_str.endswith('?')
        if is_optional:
            type_str = type_str[:-1]

        # Check if relationship
        is_relationship = '@Relationship' in match.group(0)
        relationship_type = None

        if is_relationship:
            # Extract relationship type
            if type_str.startswith('['):
                relationship_type = re.search(r'\[(\w+)\]', type_str)
                relationship_type = relationship_type.group(1) if relationship_type else None
            else:
                relationship_type = type_str

        properties.append(ModelProperty(
            name=name,
            swift_type=type_str,
            is_optional=is_optional,
            is_relationship=is_relationship,
            relationship_type=relationship_type
        ))

    return properties


def generate_cloudkit_type(model: SwiftDataModel) -> str:
    """Generate CloudKit record wrapper for a model."""
    record_type = model.name

    code = f'''import CloudKit

/// CloudKit record wrapper for {model.name}
struct Cloud{model.name}: Identifiable, Sendable {{
    let record: CKRecord

    var id: CKRecord.ID {{ record.recordID }}

    init(record: CKRecord = CKRecord(recordType: "{record_type}")) {{
        self.record = record
    }}

    static let recordType = "{record_type}"

'''

    # Generate properties
    for prop in model.properties:
        if prop.is_relationship:
            # Skip relationships for now (would need CKReference)
            code += f'    // TODO: Relationship {prop.name} -> {prop.relationship_type}\n'
            continue

        swift_type = prop.swift_type
        ck_type, getter = TYPE_MAP.get(swift_type, ('CKRecordValue', f'as? {swift_type}'))

        if prop.is_optional:
            code += f'''    var {prop.name}: {swift_type}? {{
        get {{ record["{prop.name}"] {getter} }}
        set {{ record["{prop.name}"] = newValue as? CKRecordValue }}
    }}

'''
        else:
            # Handle Bool specially
            if swift_type == 'Bool':
                code += f'''    var {prop.name}: Bool {{
        get {{ (record["{prop.name}"] as? Int64 ?? 0) == 1 }}
        set {{ record["{prop.name}"] = (newValue ? 1 : 0) as Int64 }}
    }}

'''
            elif swift_type == 'UUID':
                code += f'''    var {prop.name}: UUID {{
        get {{ UUID(uuidString: record["{prop.name}"] as? String ?? "") ?? UUID() }}
        set {{ record["{prop.name}"] = newValue.uuidString }}
    }}

'''
            else:
                code += f'''    var {prop.name}: {swift_type} {{
        get {{ record["{prop.name}"] {getter} }}
        set {{ record["{prop.name}"] = newValue as? CKRecordValue }}
    }}

'''

    code += '}\n'

    # Generate extension for manager
    code += f'''
// MARK: - CloudKit Manager Extension

extension Cloud{model.name} {{
    /// Create query for fetching all {model.name} records
    static func fetchAllQuery(sortBy key: String = "createdAt", ascending: Bool = false) -> CKQuery {{
        let query = CKQuery(
            recordType: recordType,
            predicate: NSPredicate(value: true)
        )
        query.sortDescriptors = [NSSortDescriptor(key: key, ascending: ascending)]
        return query
    }}
}}
'''

    return code


def main():
    parser = argparse.ArgumentParser(description='Generate CloudKit types from SwiftData models')
    parser.add_argument('model_file', help='SwiftData model file to process')
    parser.add_argument('--output', default='./CloudKitTypes', help='Output directory')
    args = parser.parse_args()

    file_path = Path(args.model_file)

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Read model file
    content = file_path.read_text()

    # Parse models
    models = parse_model_file(content)

    if not models:
        print(f"No @Model classes found in {file_path}")
        print("Ensure your file contains SwiftData @Model class definitions")
        sys.exit(0)

    print(f"Found {len(models)} SwiftData model(s)")

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate CloudKit types
    for model in models:
        cloudkit_code = generate_cloudkit_type(model)

        output_file = output_dir / f'Cloud{model.name}.swift'
        output_file.write_text(cloudkit_code)

        print(f"✅ Generated: {output_file}")
        print(f"   Properties: {len([p for p in model.properties if not p.is_relationship])}")
        print(f"   Relationships: {len([p for p in model.properties if p.is_relationship])}")


if __name__ == '__main__':
    main()
