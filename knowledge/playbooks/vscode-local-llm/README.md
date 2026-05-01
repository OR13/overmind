# VS Code + Local LLM (no inference cost)

Native VS Code chat backed by a local Ollama model, via GitHub Copilot
Chat's "Bring Your Own Model" (BYOM) feature. Inference happens entirely
on your machine; the chat UI is the one already built into VS Code.

## Stack

- **Ollama** — local model server (<https://ollama.com>)
- **GitHub Copilot Chat** — VS Code extension that provides the native
  chat UI and supports custom model providers (BYOM)
- **Gemma 4** (`gemma4:latest` in Ollama) — chat / edit model
- **GitHub account** — required to sign into Copilot Chat. The free
  Copilot tier is sufficient; no paid subscription needed for BYOM use.

## Why this path

VS Code itself has no built-in chat UI; the "native" chat panel is
provided by the Copilot Chat extension. BYOM lets you point Copilot
Chat at any local OpenAI-compatible or Ollama-compatible endpoint, so
all generation happens on your machine even though the chat UI is
Microsoft's. No third-party AI extensions, no inference fees.

## Requirements

- VS Code 1.99 or newer (for BYOM "Manage Models" UI)
- Copilot Chat extension 0.20+ (BYOM-capable)
- Ollama running locally on `http://localhost:11434` with at least one
  model pulled

Confirm:

```sh
code --version
code --list-extensions --show-versions | grep github.copilot-chat
ollama list
curl -s http://localhost:11434/api/tags | head -c 200
```

## One-time setup

1. **Sign into GitHub Copilot in VS Code.** Command Palette →
   `GitHub Copilot: Sign In`. The free tier is fine; you only need
   the auth, not the hosted models.

2. **Open the Chat panel.** `⌃⌘I` (macOS) or click the chat icon in
   the activity bar.

3. **Add Ollama as a model provider.**
   - Click the model picker dropdown at the top of the chat input.
   - Choose `Manage Models…`
   - Select `Ollama`.
   - Confirm the endpoint `http://localhost:11434` (the default).
   - Toggle on `gemma4:latest` (and any others you want available).

4. **Select Gemma 4 in the chat.** Use the same model picker; pick
   `gemma4:latest (Ollama)`.

5. **Send a test message.** First reply is slow (model loads into
   RAM); subsequent replies are fast.

## Verifying inference is local

- Watch Ollama: `ollama ps` should show `gemma4:latest` actively
  loaded after your first message.
- Network: no outbound calls during chat generation. (Copilot Chat
  may still call GitHub for telemetry/auth/feature flags; only the
  model inference is guaranteed local.)

## Tracked configuration

`chatLanguageModels.json` in this directory is the canonical version of
VS Code's chat-provider registration. It's symlinked into:

```
~/Library/Application Support/Code/User/chatLanguageModels.json
```

so editing the tracked file (and reloading VS Code) applies changes
immediately. To recreate the symlink on a fresh machine:

```sh
ln -sf "$(pwd)/chatLanguageModels.json" \
       "$HOME/Library/Application Support/Code/User/chatLanguageModels.json"
```

Run from this directory.

**What this file does — and doesn't — capture.** It registers Ollama as
a chat-model *provider* (the endpoint URL VS Code talks to). It does
**not** record which specific Ollama models are toggled on; that
selection lives in the Copilot Chat extension's globalStorage and is
re-applied through the `Manage Models…` UI. So if you set this up on a
new machine, the symlink restores the provider for free, but you'll
still need to walk through `Manage Models… → Ollama → toggle gemma4`
once.

## Caveats

- **GitHub auth is required.** The Copilot Chat extension won't let you
  use chat (even with a custom model) until you've signed in. Free tier
  works for BYOM.
- **Not every Copilot feature stays local.** Next Edit Suggestions, code
  completions in the editor margin, and some `@workspace` indexing
  still go through GitHub's hosted models. Disable them in settings if
  you want strict local-only behavior:

  ```json
  "github.copilot.nextEditSuggestions.enabled": false,
  "github.copilot.enable": { "*": false }
  ```

  Chat itself, with the model picker pointed at Ollama, runs entirely
  on your machine.

- **Memory.** Gemma 4 (9.6 GB on disk) needs ~12 GB free RAM to load.
  On smaller systems switch to `gemma3:latest` (3.3 GB) or
  `gemma2:2b` (1.6 GB) by re-running the BYOM toggle for those models.

## Alternatives considered

- **Continue.dev** — mature local-first VS Code extension. Rejected:
  goal here is to use the native VS Code chat, not a third-party UI.
- **Cline / Roo Code / Twinny** — third-party extensions; same reason
  for rejection.
- **Ollama from terminal only** — no editor integration; loses inline
  edits and chat-with-selection ergonomics.
