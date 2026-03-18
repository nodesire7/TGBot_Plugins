#!/usr/bin/env python3
"""
Generate index.json from plugin manifests.

This script scans all plugins and creates a unified index for the marketplace.
"""

import json
import os
from pathlib import Path
from datetime import datetime

PLUGINS_DIR = Path(__file__).parent.parent / "plugins"
INDEX_PATH = Path(__file__).parent.parent / "index.json"


def load_manifest(plugin_dir: Path) -> dict:
    """Load plugin manifest."""
    manifest_path = plugin_dir / "manifest.json"

    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path) as f:
            return json.load(f)
    except:
        return None


def generate_index() -> dict:
    """Generate the plugin index."""
    plugins = []
    categories = {}

    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue

        manifest = load_manifest(plugin_dir)
        if not manifest:
            continue

        # Build plugin entry
        plugin_entry = {
            "id": manifest.get("id", plugin_dir.name),
            "name": manifest.get("name", plugin_dir.name),
            "version": manifest.get("version", "1.0.0"),
            "author": manifest.get("author", "Unknown"),
            "description": manifest.get("description", ""),
            "category": manifest.get("category", "other"),
            "icon": manifest.get("icon", "📦"),
            "keywords": manifest.get("keywords", []),
            "hooks": manifest.get("hooks", []),
            "permissions": manifest.get("permissions", []),
            "commands": manifest.get("commands", []),
            "path": f"plugins/{plugin_dir.name}"
        }

        plugins.append(plugin_entry)

        # Track categories
        cat = manifest.get("category", "other")
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

    # Build category list
    category_list = [
        {"id": cat_id, "name": cat_id.replace("_", " ").title(), "count": count}
        for cat_id, count in sorted(categories.items())
    ]

    return {
        "version": "1.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "plugins": plugins,
        "categories": category_list
    }


def main():
    """Generate and save index."""
    print("Generating plugin index...")

    index = generate_index()

    # Check if index changed
    if INDEX_PATH.exists():
        with open(INDEX_PATH) as f:
            old_index = json.load(f)

        # Compare plugins (ignore timestamp)
        old_plugins = sorted(old_index.get("plugins", []), key=lambda x: x["id"])
        new_plugins = sorted(index["plugins"], key=lambda x: x["id"])

        if old_plugins == new_plugins:
            print("Index unchanged")
            return

    # Save index
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"Index generated: {len(index['plugins'])} plugins")


if __name__ == "__main__":
    main()
