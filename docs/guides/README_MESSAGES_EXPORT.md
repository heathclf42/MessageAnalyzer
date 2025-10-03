# OurVinyl Messages Export - Instructions

This script extracts iMessages from your Messages database for the key contacts related to your OurVinyl debt case.

## Target Contacts

The script will extract messages from:
- Sean Brna: +1 (224) 436-4643
- Mike Moen (Personal): +1 (251) 232-0363
- Mike Moen (Business): +1 (615) 586-2259
- Jordan Schneider: (586) 206-9645
- Mike Reuther (Personal): (636) 346-6287
- Mike Reuther (Business): (615) 586-2745

## How to Use

### Step 1: Close Messages App
Make sure the Messages app is completely closed before running the script.

```bash
# Force quit Messages if needed
killall Messages
```

### Step 2: Make the Script Executable

```bash
chmod +x extract_ourvinyl_messages.py
```

### Step 3: Run the Script

```bash
python3 extract_ourvinyl_messages.py
```

Or if you need to run it with full path:

```bash
python3 /path/to/extract_ourvinyl_messages.py
```

### Step 4: Review the Output

The script will create a file called `ourvinyl_messages.json` containing all messages from these contacts.

## Output Format

The JSON file will have this structure:

```json
{
  "export_date": "2025-10-01T13:30:00",
  "total_contacts": 6,
  "total_messages": 150,
  "conversations": {
    "Sean Brna": {
      "contact_name": "Sean Brna",
      "contact_identifier": "+12244364643",
      "messages": [
        {
          "message_id": 12345,
          "date": "2025-02-28T15:44:00",
          "date_formatted": "2025-02-28 03:44:00 PM",
          "text": "Hey, I owe you an apology...",
          "is_from_me": false,
          "has_attachments": false,
          "service": "iMessage"
        }
      ]
    }
  }
}
```

## Troubleshooting

### Permission Denied Error

If you get a permission error, make sure Terminal (or whatever terminal you're using) has Full Disk Access:

1. Go to System Settings > Privacy & Security > Full Disk Access
2. Add your terminal application (Terminal, iTerm, etc.)
3. Restart your terminal and try again

### Database Not Found

If the script can't find the database, verify the location:

```bash
ls -la ~/Library/Messages/chat.db
```

### No Messages Found

If the script runs but finds 0 messages, the phone numbers might be stored in a different format. You can check what's in your database:

```bash
sqlite3 ~/Library/Messages/chat.db "SELECT DISTINCT id FROM handle LIMIT 20;"
```

This will show you how phone numbers are stored in your database.

## Next Steps

Once you have the JSON file:

1. Open it in any text editor or JSON viewer
2. Search for keywords related to your debt case:
   - "$8500" or "$8.5k"
   - "March 2022"
   - "debt" or "owe"
   - "payment"
   - "contract" or "equity"
3. Review the conversations with Sean Brna, Mike Moen, and Jordan about Mike Reuther's spending and lack of transparency

## Privacy Note

This script only reads your local Messages database. It doesn't send any data anywhere. The output file (`ourvinyl_messages.json`) stays on your computer until you delete it.
