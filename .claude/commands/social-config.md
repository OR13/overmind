---
description: Configure social media posting preferences — topic keywords, posting frequency, preferred times, default platforms. Use when the user wants to view or change social media skill settings.
---

## Social Media Configuration

Manage preferences for the social media skills (`/post-content`, `/filter-follows`, `/discover-accounts`).

**State directory:** `$OVERMIND_ROOT/.git-ignored/social-media/` — `OVERMIND_ROOT` must be set in your shell. See `knowledge/playbooks/social-media/README.md`.

## User Input

```text
$ARGUMENTS
```

## Execution

### 1. Ensure data directory exists

Run this command to create the directory if missing:

```bash
mkdir -p "${OVERMIND_ROOT:?OVERMIND_ROOT must point at your overmind clone — see knowledge/playbooks/social-media/README.md}/.git-ignored/social-media"
```

### 2. Load or seed preferences

Read the current preferences file:

```bash
cat $OVERMIND_ROOT/.git-ignored/social-media/preferences.json 2>/dev/null
```

If the file does not exist or is empty, create it with these defaults:

```json
{
  "maxPostsPerDay": 2,
  "preferredTimes": ["09:00", "17:00"],
  "timezone": "America/Chicago",
  "defaultPlatforms": ["bluesky", "xcom"],
  "topicKeywords": [
    "agentic software development",
    "AI product methodology",
    "human-agent collaboration",
    "LLM tooling"
  ]
}
```

Write the defaults using the Write tool to `$OVERMIND_ROOT/.git-ignored/social-media/preferences.json`.

### 3. Parse subcommand from $ARGUMENTS

Determine which operation the user wants:

- **No arguments or "show"**: Display the current configuration in a readable format. Show each field with its current value. End here.

- **"set frequency N"**: Update `maxPostsPerDay` to N (integer, 1-10). Write the updated JSON back.

- **"set timezone ZONE"**: Update `timezone` to the provided IANA timezone string (e.g., "US/Eastern", "America/New_York", "UTC"). Write the updated JSON back.

- **"set platforms PLATFORM_LIST"**: Update `defaultPlatforms`. Accept "bluesky", "xcom", or "both". Map "both" to `["bluesky", "xcom"]`. Write the updated JSON back.

- **"set time HH:MM"** or **"set times HH:MM,HH:MM"**: Update `preferredTimes` array. Accept one or more comma-separated times in HH:MM format. Write the updated JSON back.

- **"add keyword PHRASE"**: Append the phrase to the `topicKeywords` array (if not already present). Write the updated JSON back.

- **"remove keyword PHRASE"**: Remove the phrase from `topicKeywords` (if present). Write the updated JSON back.

### 4. Write updated preferences

After any modification, write the complete updated JSON object to `$OVERMIND_ROOT/.git-ignored/social-media/preferences.json` using the Write tool. Preserve all fields — only modify the one being changed.

### 5. Confirm to user

After any change, display:
- The field that was modified
- The old value and new value
- The full current configuration

If the subcommand is not recognized, show the available subcommands:
- `/social-config` — show current config
- `/social-config set frequency N` — set max posts per day
- `/social-config set timezone ZONE` — set timezone
- `/social-config set platforms both|bluesky|xcom` — set default platforms
- `/social-config set time HH:MM` — set preferred posting times
- `/social-config add keyword "PHRASE"` — add a topic keyword
- `/social-config remove keyword "PHRASE"` — remove a topic keyword
