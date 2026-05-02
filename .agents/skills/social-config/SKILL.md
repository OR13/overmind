---
name: social-config
description: Configure social media posting preferences — topic keywords, voice, posting frequency, preferred times, default platforms. Use when the user wants to view or change social media skill settings.
---

## Social Media Configuration

Manage preferences for the social media skills (`/post-content`, `/filter-follows`, `/discover-accounts`).

**State directory:** `$OVERMIND_ROOT/.git-ignored/social-media/` — `OVERMIND_ROOT` must be set in your shell. See `memory/playbooks/social-media/README.md`.

## User Input

```text
$ARGUMENTS
```

## Execution

### 1. Ensure data directory exists

Run this command to create the directory if missing:

```bash
mkdir -p "${OVERMIND_ROOT:?OVERMIND_ROOT must point at your overmind clone — see memory/playbooks/social-media/README.md}/.git-ignored/social-media"
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
  "timezone": "UTC",
  "defaultPlatforms": ["bluesky", "xcom"],
  "topicKeywords": [],
  "voice": "Thoughtful and direct. Share what stood out and why; avoid bland summaries; professional but with conviction."
}
```

After seeding, tell the user that `topicKeywords` is empty and they need to add at least one before `/post-content` or `/discover-accounts` will work — show the `add keyword` subcommand example.

`/discover-accounts` reads its seed handles from a separate markdown file — `$OVERMIND_ROOT/.git-ignored/social-media/seeds.md` — which is created and edited directly by the user. That file is not managed by `/social-config`; this skill should not offer to mutate it.

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

- **"set voice DESCRIPTION"**: Update `voice` to the provided string. The voice describes the tone and stance `/post-content` should use when drafting hot takes (e.g., "analytical contrarian", "earnest enthusiast", "deadpan observer"). Free-form — the more specific the description, the more consistent the output. Write the updated JSON back.

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
- `/social-config set voice "DESCRIPTION"` — set the voice/tone for drafted posts

For `/discover-accounts` seed handles: edit `$OVERMIND_ROOT/.git-ignored/social-media/seeds.md` directly. The file is created with a default template the first time `/discover-accounts` runs.
