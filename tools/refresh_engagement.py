#!/usr/bin/env python3
"""
Refresh engagement counts on stored social posts from Bluesky's public AppView.

Reads each MD under $OVERMIND_ROOT/memory/private/social-media/posts/, batches
their bluesky_uri values into getPosts, and updates the `engagement` block in
frontmatter (likes/reposts/replies/quotes/bookmarks). Body text is preserved.
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

BSKY_PUBLIC_API = "https://public.api.bsky.app/xrpc/app.bsky.feed.getPosts"
BATCH_SIZE = 25  # getPosts accepts up to 25 uris per call


def overmind_root() -> Path:
    root = os.environ.get("OVERMIND_ROOT")
    if not root:
        print("Error: OVERMIND_ROOT not set", file=sys.stderr)
        sys.exit(1)
    return Path(root)


def parse_md(path: Path) -> tuple[dict[str, Any], str]:
    content = path.read_text()
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    metadata: dict[str, Any] = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n").rstrip() + "\n"
    return metadata, body


def write_md(path: Path, metadata: dict[str, Any], body: str) -> None:
    frontmatter = yaml.dump(metadata, sort_keys=False, allow_unicode=True).strip()
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n")


def fetch_posts(uris: list[str]) -> dict[str, dict[str, Any]]:
    """Return {uri: post} for each requested uri (missing keys mean no result)."""
    out: dict[str, dict[str, Any]] = {}
    for i in range(0, len(uris), BATCH_SIZE):
        batch = uris[i : i + BATCH_SIZE]
        qs = urllib.parse.urlencode([("uris", u) for u in batch])
        url = f"{BSKY_PUBLIC_API}?{qs}"
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                payload = json.load(resp)
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
            print(f"  warn: batch fetch failed: {e}", file=sys.stderr)
            continue
        for post in payload.get("posts", []):
            out[post["uri"]] = post
    return out


def main() -> None:
    root = overmind_root()
    posts_dir = root / "memory" / "private" / "social-media" / "posts"
    if not posts_dir.exists():
        print(f"No posts directory at {posts_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted(posts_dir.glob("*.md"))
    parsed: list[tuple[Path, dict[str, Any], str]] = []
    uris: list[str] = []
    for f in files:
        meta, body = parse_md(f)
        parsed.append((f, meta, body))
        uri = meta.get("bluesky_uri")
        if uri:
            uris.append(uri)

    print(f"Refreshing engagement for {len(uris)} bluesky posts...")
    results = fetch_posts(uris)
    now_iso = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    updated = 0
    for path, meta, body in parsed:
        uri = meta.get("bluesky_uri")
        post = results.get(uri) if uri else None
        if not post:
            continue
        meta["engagement"] = {
            "likes": post.get("likeCount", 0),
            "reposts": post.get("repostCount", 0),
            "replies": post.get("replyCount", 0),
            "quotes": post.get("quoteCount", 0),
            "bookmarks": post.get("bookmarkCount", 0),
        }
        meta["engagement_refreshed_at"] = now_iso
        write_md(path, meta, body)
        eng = meta["engagement"]
        print(
            f"  {path.name}: "
            f"{eng['likes']}L {eng['reposts']}R {eng['replies']}C "
            f"{eng['quotes']}Q {eng['bookmarks']}B"
        )
        updated += 1

    print(f"Done. Updated {updated}/{len(parsed)} posts.")


if __name__ == "__main__":
    main()
