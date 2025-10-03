#!/usr/bin/env python3
"""
Add contact names to phone numbers across all conversations and dashboards.
"""

import json
import os
import sys
import glob
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.paths import CONVERSATIONS_DIR

NAME_MAPPING_FILE = CONVERSATIONS_DIR / "contact_names.json"

def load_name_mapping():
    """Load existing name mapping"""
    if NAME_MAPPING_FILE.exists():
        with open(str(NAME_MAPPING_FILE), 'r') as f:
            return json.load(f)
    return {}

def save_name_mapping(mapping):
    """Save name mapping to file"""
    with open(str(NAME_MAPPING_FILE), 'w') as f:
        json.dump(mapping, f, indent=2)

def add_name(phone_number, name):
    """Add a name for a phone number"""
    mapping = load_name_mapping()

    # Normalize phone number (remove spaces, dashes)
    normalized = phone_number.replace('-', '').replace(' ', '').replace('+', '')

    # Find matching conversations
    matches = []
    for file in os.listdir(str(CONVERSATIONS_DIR)):
        if file.endswith('.json') and not file.startswith('00_'):
            file_normalized = file.replace('-', '').replace('_', '')
            if normalized in file_normalized:
                matches.append(file)

    if not matches:
        print(f"⚠️  No conversations found for {phone_number}")
        print(f"   Searched for normalized number: {normalized}")
        return False

    # Add to mapping
    mapping[phone_number] = name
    save_name_mapping(mapping)

    print(f"✓ Added name mapping: {phone_number} → {name}")
    print(f"  Found {len(matches)} conversation file(s)")

    return True

def apply_names_to_files():
    """Apply names to all JSON and text files"""
    mapping = load_name_mapping()

    if not mapping:
        print("No name mappings found. Use add_name() first.")
        return

    updated_count = 0

    # Update all JSON conversation files
    for json_file in glob.glob(str(CONVERSATIONS_DIR / "*.json")):
        if json_file.endswith(('00_MASTER_INDEX.json', '00_RELATIONSHIP_CATEGORIES.json', 'contact_names.json')):
            continue

        with open(json_file, 'r') as f:
            data = json.load(f)

        original_name = data.get('conversation_name', '')
        updated = False

        # Check if conversation name matches any phone number in mapping
        for phone, name in mapping.items():
            normalized_phone = phone.replace('-', '').replace(' ', '').replace('+', '')
            normalized_conv = original_name.replace('-', '').replace(' ', '').replace('+', '')

            if normalized_phone in normalized_conv:
                data['conversation_name'] = name
                updated = True
                break

        if updated:
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            updated_count += 1

    print(f"✓ Updated {updated_count} conversation files with names")

    # Recreate dashboards with new names
    print("\nRecreating dashboards with names...")
    recreate_dashboards()

def recreate_dashboards():
    """Recreate all dashboards with updated names"""
    from create_message_viewer_dashboard import create_message_viewer_dashboard

    # Find all conversation JSON files (not analysis files)
    conv_files = glob.glob(str(CONVERSATIONS_DIR / "*.json"))
    conv_files = [f for f in conv_files if not any(x in f for x in ['_analysis.json', '00_MASTER', '00_SUMMARY', 'contact_names.json'])]

    for i, conv_file in enumerate(conv_files, 1):
        print(f"  [{i}/{len(conv_files)}] Recreating dashboard...")
        try:
            create_message_viewer_dashboard(conv_file)
        except Exception as e:
            print(f"    Error: {e}")

    print(f"✓ Recreated {len(conv_files)} dashboards")

def list_unmapped_conversations():
    """List all conversations that don't have names assigned"""
    mapping = load_name_mapping()

    unmapped = []

    for json_file in glob.glob(str(CONVERSATIONS_DIR / "*.json")):
        if json_file.endswith(('00_MASTER_INDEX.json', '00_RELATIONSHIP_CATEGORIES.json', 'contact_names.json')):
            continue

        with open(json_file, 'r') as f:
            data = json.load(f)

        conv_name = data.get('conversation_name', '')

        # Check if it's a phone number (not already named)
        if any(char.isdigit() for char in conv_name) and not any(conv_name == name for name in mapping.values()):
            # Check if already mapped
            is_mapped = False
            for phone in mapping.keys():
                normalized_phone = phone.replace('-', '').replace(' ', '').replace('+', '')
                normalized_conv = conv_name.replace('-', '').replace(' ', '').replace('+', '')
                if normalized_phone in normalized_conv:
                    is_mapped = True
                    break

            if not is_mapped:
                msg_count = data.get('total_messages', 0)
                date_range = data.get('date_range', 'Unknown')
                unmapped.append({
                    'number': conv_name,
                    'messages': msg_count,
                    'date_range': date_range
                })

    # Sort by message count
    unmapped.sort(key=lambda x: x['messages'], reverse=True)

    return unmapped

def interactive_add_names():
    """Interactive mode to add names"""
    print("=" * 80)
    print("CONTACT NAME MAPPER")
    print("=" * 80)
    print()

    unmapped = list_unmapped_conversations()

    if not unmapped:
        print("✓ All conversations already have names assigned!")
        return

    print(f"Found {len(unmapped)} unmapped conversations:\n")

    for i, conv in enumerate(unmapped, 1):
        print(f"{i}. {conv['number']}")
        print(f"   {conv['messages']:,} messages | {conv['date_range']}")
        print()

    print("\nOptions:")
    print("1. Add name for a specific number")
    print("2. Add names interactively (go through each)")
    print("3. Exit")
    print()

    choice = input("Choose option (1-3): ").strip()

    if choice == '1':
        phone = input("\nEnter phone number (e.g., 773-308-3425): ").strip()
        name = input("Enter name: ").strip()
        if add_name(phone, name):
            if input("\nApply names to all files now? (y/n): ").lower() == 'y':
                apply_names_to_files()

    elif choice == '2':
        for conv in unmapped:
            print(f"\n{conv['number']} ({conv['messages']:,} messages)")
            name = input("Enter name (or 'skip'): ").strip()
            if name.lower() != 'skip' and name:
                add_name(conv['number'], name)

        if input("\nApply names to all files now? (y/n): ").lower() == 'y':
            apply_names_to_files()

    print("\n✓ Done!")

def bulk_add_names(name_dict):
    """
    Bulk add names from a dictionary

    Example:
        bulk_add_names({
            "773-308-3425": "John Smith",
            "717-475-5530": "Samantha Condit",
            "309-657-8625": "Jane Doe"
        })
    """
    mapping = load_name_mapping()

    for phone, name in name_dict.items():
        mapping[phone] = name
        print(f"  Added: {phone} → {name}")

    save_name_mapping(mapping)
    print(f"\n✓ Added {len(name_dict)} names to mapping")

    if input("\nApply names to all files now? (y/n): ").lower() == 'y':
        apply_names_to_files()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'add' and len(sys.argv) == 4:
            # python add_contact_names.py add "773-308-3425" "John Smith"
            add_name(sys.argv[2], sys.argv[3])
            if input("\nApply names to all files now? (y/n): ").lower() == 'y':
                apply_names_to_files()

        elif command == 'apply':
            # python add_contact_names.py apply
            apply_names_to_files()

        elif command == 'list':
            # python add_contact_names.py list
            unmapped = list_unmapped_conversations()
            print(f"\n{len(unmapped)} unmapped conversations:")
            for conv in unmapped:
                print(f"  {conv['number']} - {conv['messages']:,} messages")

        else:
            print("Usage:")
            print("  python add_contact_names.py add <phone> <name>")
            print("  python add_contact_names.py apply")
            print("  python add_contact_names.py list")
            print("  python add_contact_names.py        (interactive mode)")
    else:
        # Interactive mode
        interactive_add_names()
