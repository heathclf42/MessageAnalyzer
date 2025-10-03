#!/usr/bin/env python3
"""
Extract ALL conversations from Messages database, sorted by message count.
Creates organized output files for each conversation.
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.paths import DATABASE_PATH, CONVERSATIONS_DIR

# Configuration
MIN_MESSAGES = 5  # Only include conversations with at least this many messages

def normalize_phone(phone):
    """Remove all non-digit characters from phone number"""
    if not phone:
        return ""
    return ''.join(c for c in phone if c.isdigit())

def cocoa_timestamp_to_datetime(cocoa_timestamp):
    """Convert Cocoa Core Data timestamp to Python datetime"""
    if cocoa_timestamp is None:
        return None
    # Cocoa timestamps are nanoseconds since 2001-01-01
    unix_timestamp = cocoa_timestamp / 1000000000 + 978307200
    return datetime.fromtimestamp(unix_timestamp)

def extract_text_from_attributed_body(attributed_body):
    """Extract plain text from attributedBody BLOB"""
    if not attributed_body:
        return None

    try:
        text = attributed_body.decode('utf-8', errors='ignore')
        patterns = [
            r'NSString\x01\x94\x84\x01\+([^\x84\x85\x86\x00]+)',
            r'NSString.*?\+([^\x00\x84\x85]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                extracted = match.group(1)
                cleaned = ''.join(c for c in extracted if c.isprintable() or c in '\n\r\t')
                cleaned = cleaned.strip()
                cleaned = re.sub(r'iI[^\s]*NSDictionary.*$', '', cleaned, flags=re.DOTALL)
                cleaned = re.sub(r'NSDictionary.*$', '', cleaned, flags=re.DOTALL)
                cleaned = re.sub(r'iI\s*$', '', cleaned)
                cleaned = re.sub(r'iI$', '', cleaned)

                # Remove leading special characters that are artifacts
                cleaned = re.sub(r'^[&*,;]+\s*', '', cleaned)

                # Remove trailing special characters that are artifacts
                cleaned = re.sub(r'\s*[;,]+$', '', cleaned)

                # Remove uppercase letter pairs at the beginning
                if len(cleaned) > 2 and cleaned[0].isupper() and cleaned[1].isupper():
                    cleaned = cleaned[1:]

                cleaned = cleaned.strip()
                if cleaned and len(cleaned) > 0:
                    return cleaned
        return None
    except Exception as e:
        return None

def sanitize_filename(name):
    """Create safe filename from contact name/number"""
    # Remove or replace unsafe characters
    safe = re.sub(r'[^\w\s\-\+]', '', name)
    safe = safe.replace(' ', '_')
    return safe[:100]  # Limit length

def get_contact_name(contact_id):
    """Generate a readable name for a contact"""
    if not contact_id:
        return "Unknown"
    if contact_id.startswith('+'):
        # Format phone number nicely
        digits = contact_id[1:] if contact_id.startswith('+') else contact_id
        if len(digits) == 11 and digits.startswith('1'):
            # US number
            return f"{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
        return contact_id
    return contact_id

def extract_all_conversations():
    """Extract all conversations from the database"""

    if not DATABASE_PATH.exists():
        print(f"Error: Messages database not found at {DATABASE_PATH}")
        return None

    # Create output directory
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()

        print("Analyzing conversations in database...")

        # Get all chats with message counts
        chat_query = """
        SELECT
            chat.ROWID as chat_rowid,
            chat.chat_identifier,
            chat.display_name,
            COUNT(DISTINCT message.ROWID) as message_count
        FROM chat
        LEFT JOIN chat_message_join ON chat.ROWID = chat_message_join.chat_id
        LEFT JOIN message ON chat_message_join.message_id = message.ROWID
        GROUP BY chat.ROWID
        HAVING message_count >= ?
        ORDER BY message_count DESC
        """

        cursor.execute(chat_query, (MIN_MESSAGES,))
        chats = cursor.fetchall()

        print(f"Found {len(chats)} conversations with {MIN_MESSAGES}+ messages")

        all_conversations = []

        for idx, (chat_rowid, chat_id, display_name, msg_count) in enumerate(chats, 1):
            print(f"Processing {idx}/{len(chats)}: {chat_id} ({msg_count} messages)...")

            # Get participants for this chat
            participant_query = """
            SELECT DISTINCT handle.id
            FROM chat_handle_join
            JOIN handle ON chat_handle_join.handle_id = handle.ROWID
            WHERE chat_handle_join.chat_id = ?
            """
            cursor.execute(participant_query, (chat_rowid,))
            participants = [row[0] for row in cursor.fetchall()]

            # Get messages for this chat
            message_query = """
            SELECT
                message.ROWID as message_id,
                message.date as message_date,
                message.text,
                message.attributedBody,
                message.is_from_me,
                message.cache_has_attachments,
                handle.id as sender_id,
                handle.service
            FROM message
            LEFT JOIN handle ON message.handle_id = handle.ROWID
            LEFT JOIN chat_message_join ON message.ROWID = chat_message_join.message_id
            WHERE chat_message_join.chat_id = ?
            ORDER BY message.date ASC
            """

            cursor.execute(message_query, (chat_rowid,))
            messages = cursor.fetchall()

            # Process messages
            message_list = []
            for msg in messages:
                msg_id, msg_date, text, attributed_body, is_from_me, has_attachments, sender_id, service = msg

                # Extract text
                if not text and attributed_body:
                    text = extract_text_from_attributed_body(attributed_body)

                if not text:
                    continue

                # Determine sender
                if is_from_me:
                    sender_name = "YOU"
                else:
                    sender_name = get_contact_name(sender_id) if sender_id else "Unknown"

                dt = cocoa_timestamp_to_datetime(msg_date)

                message_list.append({
                    "message_id": msg_id,
                    "date": dt.isoformat() if dt else None,
                    "date_formatted": dt.strftime("%Y-%m-%d %I:%M:%S %p") if dt else None,
                    "text": text,
                    "sender": sender_name,
                    "is_from_me": bool(is_from_me),
                    "has_attachments": bool(has_attachments),
                    "service": service
                })

            if not message_list:
                continue

            # Determine conversation name
            is_group = len(participants) > 1
            if is_group:
                conv_name = f"Group_{chat_id}"
                participant_names = [get_contact_name(p) for p in participants]
            else:
                conv_name = get_contact_name(participants[0]) if participants else chat_id
                participant_names = [conv_name]

            # Calculate date range
            dates = [m['date'] for m in message_list if m['date']]
            date_range = f"{dates[0][:10]} to {dates[-1][:10]}" if dates else "Unknown"

            conversation_data = {
                "chat_id": chat_id,
                "conversation_name": conv_name,
                "participants": participant_names,
                "is_group": is_group,
                "message_count": len(message_list),
                "date_range": date_range,
                "messages": message_list
            }

            all_conversations.append(conversation_data)

            # Save individual conversation file
            safe_name = sanitize_filename(conv_name)
            file_prefix = f"{len(all_conversations):04d}_{len(message_list):05d}_msgs"

            # Save text file
            txt_file = CONVERSATIONS_DIR / f"{file_prefix}_{safe_name}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                if is_group:
                    f.write(f"GROUP CONVERSATION\n")
                    f.write(f"Participants: {', '.join(participant_names)}\n")
                else:
                    f.write(f"CONVERSATION WITH: {conv_name}\n")
                f.write(f"Date Range: {date_range}\n")
                f.write(f"Message Count: {len(message_list)}\n")
                f.write("=" * 80 + "\n\n")

                for msg in message_list:
                    sender = msg['sender']
                    date = msg['date_formatted'] or msg['date']
                    f.write(f"[{date}] {sender}:\n")
                    f.write(f"{msg['text']}\n")
                    if msg['has_attachments']:
                        f.write("  [Has attachments]\n")
                    f.write("\n")

            # Save JSON file
            json_file = CONVERSATIONS_DIR / f"{file_prefix}_{safe_name}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

        conn.close()

        # Create master index
        master_index = {
            "export_date": datetime.now().isoformat(),
            "total_conversations": len(all_conversations),
            "total_messages": sum(c['message_count'] for c in all_conversations),
            "conversations": [
                {
                    "rank": idx + 1,
                    "name": c['conversation_name'],
                    "participants": c['participants'],
                    "is_group": c['is_group'],
                    "message_count": c['message_count'],
                    "date_range": c['date_range'],
                    "files": {
                        "text": f"{idx+1:04d}_{c['message_count']:05d}_msgs_{sanitize_filename(c['conversation_name'])}.txt",
                        "json": f"{idx+1:04d}_{c['message_count']:05d}_msgs_{sanitize_filename(c['conversation_name'])}.json"
                    }
                }
                for idx, c in enumerate(all_conversations)
            ]
        }

        # Save master index
        index_file = CONVERSATIONS_DIR / "00_MASTER_INDEX.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(master_index, f, indent=2, ensure_ascii=False)

        # Save readable summary
        summary_file = CONVERSATIONS_DIR / "00_SUMMARY.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ALL CONVERSATIONS SUMMARY\n")
            f.write(f"Export Date: {master_index['export_date']}\n")
            f.write(f"Total Conversations: {master_index['total_conversations']}\n")
            f.write(f"Total Messages: {master_index['total_messages']}\n")
            f.write("=" * 80 + "\n\n")

            f.write("CONVERSATIONS (sorted by message count):\n\n")
            for conv in master_index['conversations']:
                conv_type = "GROUP" if conv['is_group'] else "1-on-1"
                f.write(f"#{conv['rank']:04d} [{conv_type}] {conv['name']}\n")
                f.write(f"      Messages: {conv['message_count']:,} | Range: {conv['date_range']}\n")
                if conv['is_group']:
                    f.write(f"      Participants: {', '.join(conv['participants'])}\n")
                f.write("\n")

        return master_index

    except Exception as e:
        print(f"Error extracting conversations: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("Extracting all conversations from Messages database...")
    print(f"Database: {DATABASE_PATH}")
    print(f"Output Directory: {CONVERSATIONS_DIR}")
    print(f"Minimum messages per conversation: {MIN_MESSAGES}")
    print()

    result = extract_all_conversations()

    if result:
        print(f"\n✓ Successfully exported all conversations!")
        print(f"✓ Total conversations: {result['total_conversations']}")
        print(f"✓ Total messages: {result['total_messages']:,}")
        print(f"\nFiles saved to: {CONVERSATIONS_DIR}")
        print("\nKey files:")
        print(f"  - 00_SUMMARY.txt - Overview of all conversations")
        print(f"  - 00_MASTER_INDEX.json - Machine-readable index")
        print(f"  - Individual conversation files (numbered by message count)")
    else:
        print("✗ Failed to extract conversations")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
