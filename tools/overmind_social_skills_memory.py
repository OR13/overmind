#!/usr/bin/env python3
"""
Overmind Social Skills Memory Tool
Manages social media state in private memory using MD with YAML frontmatter.
Uses frontmatter for metadata and the MD body for content (text).
"""

import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# Required environment variable
OVERMIND_ROOT = os.environ.get("OVERMIND_ROOT")


def get_memory_dir() -> Path:
    if not OVERMIND_ROOT:
        print("Error: OVERMIND_ROOT environment variable not set.", file=sys.stderr)
        sys.exit(1)
    path = Path(OVERMIND_ROOT) / "memory" / "private" / "social-media"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_posts_dir() -> Path:
    path = get_memory_dir() / "posts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_md_yaml(file_path: Path) -> dict[str, Any]:
    if not file_path.exists():
        return {}
    content = file_path.read_text()
    if not content.startswith("---"):
        try:
            return yaml.safe_load(content) or {}
        except yaml.YAMLError:
            return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        data: dict[str, Any] = yaml.safe_load(parts[1]) or {}
        body = parts[2].strip()
        if body:
            # For posts, the body is the 'text' content
            data["text"] = body
        return data
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {file_path}: {e}", file=sys.stderr)
        return {}


def write_md_yaml(file_path: Path, data: dict[str, Any], description: str) -> None:
    # Separate body (text) from metadata
    metadata = data.copy()
    body = metadata.pop("text", "")

    metadata["name"] = file_path.stem
    metadata["description"] = description

    yaml_frontmatter = yaml.dump(metadata, sort_keys=False, indent=2, allow_unicode=True)
    content = f"---\n{yaml_frontmatter.strip()}\n---\n\n{str(body).strip()}\n"
    file_path.write_text(content)


def get_preferences() -> dict[str, Any]:
    path = get_memory_dir() / "preferences.md"
    data = read_md_yaml(path)

    defaults: dict[str, Any] = {
        "max_posts_per_day": 2,
        "preferred_times": ["09:00", "17:00"],
        "timezone": "UTC",
        "default_platforms": ["bluesky", "xcom"],
        "topic_keywords": [],
        "voice": "Thoughtful and direct. Share what stood out and why; avoid bland summaries.",
        "seeds": {"bluesky": [], "xcom": []},
        "keep_list": [],
    }

    if not data:
        data = defaults
        write_md_yaml(path, data, "Social media preferences and configuration.")
    else:
        for k, v in defaults.items():
            if k not in data:
                data[k] = v

    return data


def save_preferences(data: dict[str, Any]) -> None:
    path = get_memory_dir() / "preferences.md"
    write_md_yaml(path, data, "Social media preferences and configuration.")


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def cmd_config(args: argparse.Namespace) -> None:
    data = get_preferences()

    if args.action == "get":
        print(json.dumps(data, indent=2))
    elif args.action == "set":
        key = args.key
        value = args.value
        if key == "max_posts_per_day":
            data[key] = int(value)
        elif key == "topic_keywords":
            data[key] = [v.strip() for v in value.split(",")]
        elif key in ["timezone", "voice"]:
            data[key] = value
        elif key in ["preferred_times", "default_platforms"]:
            data[key] = [v.strip() for v in value.split(",")]
        else:
            print(f"Error: Unknown config key {key}", file=sys.stderr)
            sys.exit(1)
        save_preferences(data)
        print(f"Updated {key}")


def cmd_log(args: argparse.Namespace) -> None:
    posts_dir = get_posts_dir()

    if args.action == "check":
        url = args.url
        for f in posts_dir.glob("*.md"):
            data = read_md_yaml(f)
            if data.get("url") == url:
                print("true")
                return
        print("false")
    elif args.action == "add":
        post_data = json.loads(args.data)
        if "posted_at" not in post_data:
            post_data["posted_at"] = datetime.now(UTC).isoformat().replace("+00:00", "") + "Z"

        title = post_data.get("title", "post")
        slug = slugify(title)
        if not slug or slug == "post":
            slug = slugify(post_data["url"].split("/")[-1] or "post")

        original_slug = slug
        counter = 1
        while (posts_dir / f"{slug}.md").exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        write_md_yaml(posts_dir / f"{slug}.md", post_data, f"Social media post: {title}")
        print(f"Post added to log as {slug}.md")
    elif args.action == "list":
        limit = args.limit or 10
        files = sorted(posts_dir.glob("*.md"), key=os.path.getmtime)
        results: list[dict[str, Any]] = []
        for f in files[-limit:]:
            results.append(read_md_yaml(f))
        print(json.dumps(results, indent=2))


def cmd_seeds(args: argparse.Namespace) -> None:
    data = get_preferences()
    seeds = data.get("seeds", {"bluesky": [], "xcom": []})

    if args.action == "get":
        print(json.dumps(seeds, indent=2))
    elif args.action == "set":
        platform = args.platform
        handles = [h.strip() for h in args.handles.split(",")]
        seeds[platform] = handles
        data["seeds"] = seeds
        save_preferences(data)
        print(f"Updated seeds for {platform}")


def cmd_keep_list(args: argparse.Namespace) -> None:
    data = get_preferences()
    accounts: list[str] = data.get("keep_list", [])

    if args.action == "get":
        print(json.dumps(accounts, indent=2))
    elif args.action == "add":
        handle = args.handle
        if handle not in accounts:
            accounts.append(handle)
            data["keep_list"] = accounts
            save_preferences(data)
            print(f"Added {handle} to keep_list.")
    elif args.action == "remove":
        handle = args.handle
        if handle in accounts:
            accounts.remove(handle)
            data["keep_list"] = accounts
            save_preferences(data)
            print(f"Removed {handle} from keep_list.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Overmind Social Skills Memory Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Config
    p_config = subparsers.add_parser("config")
    p_config.add_argument("action", choices=["get", "set"])
    p_config.add_argument("key", nargs="?")
    p_config.add_argument("value", nargs="?")
    p_config.set_defaults(func=cmd_config)

    # Log
    p_log = subparsers.add_parser("log")
    p_log.add_argument("action", choices=["add", "list", "check"])
    p_log.add_argument("--url")
    p_log.add_argument("--data")
    p_log.add_argument("--limit", type=int)
    p_log.set_defaults(func=cmd_log)

    # Seeds
    p_seeds = subparsers.add_parser("seeds")
    p_seeds.add_argument("action", choices=["get", "set"])
    p_seeds.add_argument("platform", nargs="?")
    p_seeds.add_argument("handles", nargs="?")
    p_seeds.set_defaults(func=cmd_seeds)

    # Keep-list
    p_keep = subparsers.add_parser("keep-list")
    p_keep.add_argument("action", choices=["get", "add", "remove"])
    p_keep.add_argument("handle", nargs="?")
    p_keep.set_defaults(func=cmd_keep_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
