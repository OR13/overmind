#!/usr/bin/env python3
"""
One-shot migration: legacy post-log.json -> per-post MD files.

Reads $OVERMIND_ROOT/.git-ignored/social-media/post-log.json and writes
one MD per entry under $OVERMIND_ROOT/memory/private/social-media/posts/
with metadata in YAML frontmatter and the post text as the MD body.

Backfills missing post text via Bluesky's public AppView when a
bluesky_uri is present.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

BSKY_PUBLIC_API = "https://public.api.bsky.app/xrpc/app.bsky.feed.getPosts"


def overmind_root() -> Path:
    root = os.environ.get("OVERMIND_ROOT")
    if not root:
        print("Error: OVERMIND_ROOT not set", file=sys.stderr)
        sys.exit(1)
    return Path(root)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def fetch_bluesky_post(at_uri: str) -> dict[str, Any] | None:
    qs = urllib.parse.urlencode({"uris": at_uri})
    url = f"{BSKY_PUBLIC_API}?{qs}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  warn: failed to fetch {at_uri}: {e}", file=sys.stderr)
        return None
    posts = payload.get("posts", [])
    if not posts:
        return None
    return posts[0]


def slug_from_entry(entry: dict[str, Any], bsky_post: dict[str, Any] | None) -> str:
    title = ""
    if bsky_post:
        embed = bsky_post.get("record", {}).get("embed", {})
        ext = embed.get("external") if isinstance(embed, dict) else None
        if isinstance(ext, dict):
            title = ext.get("title", "") or ""
    if not title:
        url = entry.get("url", "")
        path = urllib.parse.urlparse(url).path
        title = path.rstrip("/").rsplit("/", 1)[-1] or url
    slug = slugify(title)
    return slug or "post"


def write_post_md(path: Path, metadata: dict[str, Any], body: str) -> None:
    frontmatter = yaml.dump(metadata, sort_keys=False, allow_unicode=True).strip()
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n")


def migrate() -> None:
    root = overmind_root()
    log_path = root / ".git-ignored" / "social-media" / "post-log.json"
    posts_dir = root / "memory" / "private" / "social-media" / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    if not log_path.exists():
        print(f"No legacy log at {log_path}", file=sys.stderr)
        sys.exit(1)

    entries: list[dict[str, Any]] = json.loads(log_path.read_text())
    print(f"Migrating {len(entries)} entries from {log_path}")

    seen_slugs: set[str] = set()
    for entry in entries:
        url = entry.get("url", "")
        at_uri = entry.get("blueskyUri") or entry.get("bluesky_uri")
        bsky_post = fetch_bluesky_post(at_uri) if at_uri else None

        text = ""
        title = ""
        description = ""
        if bsky_post:
            record = bsky_post.get("record", {})
            text = record.get("text", "") or ""
            embed = record.get("embed", {})
            ext = embed.get("external") if isinstance(embed, dict) else None
            if isinstance(ext, dict):
                title = ext.get("title", "") or ""
                description = ext.get("description", "") or ""

        base_slug = slug_from_entry(entry, bsky_post)
        slug = base_slug
        counter = 1
        while slug in seen_slugs or (posts_dir / f"{slug}.md").exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        seen_slugs.add(slug)

        metadata: dict[str, Any] = {
            "name": slug,
            "description": f"Social media post: {title or url}",
            "url": url,
            "title": title,
            "external_description": description,
            "content_id": entry.get("contentId") or entry.get("content_id"),
            "platforms": entry.get("platforms", []),
            "posted_at": entry.get("postedAt") or entry.get("posted_at"),
            "text_hash": entry.get("textHash") or entry.get("text_hash"),
            "bluesky_uri": at_uri,
            "xcom_tweet_id": entry.get("xcomTweetId") or entry.get("xcom_tweet_id"),
            "engagement": entry.get("engagement", {"likes": 0, "reposts": 0, "replies": 0}),
        }
        # drop empty optional fields for cleanliness
        for k in ("title", "external_description", "xcom_tweet_id"):
            if metadata.get(k) in (None, ""):
                metadata.pop(k, None)

        out_path = posts_dir / f"{slug}.md"
        write_post_md(out_path, metadata, text)
        print(f"  wrote {out_path.name} ({len(text)} chars body)")


if __name__ == "__main__":
    migrate()
