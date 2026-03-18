#!/usr/bin/env python3
"""
Validate all plugins in the marketplace.

Checks:
- manifest.json exists and is valid
- main.py exists and has valid syntax
- README.md exists
- All required fields present in manifest
"""

import json
import os
import sys
import ast
from pathlib import Path

PLUGINS_DIR = Path(__file__).parent.parent / "plugins"
SCHEMA_PATH = Path(__file__).parent.parent / "docs" / "manifest_schema.json"

REQUIRED_MANIFEST_FIELDS = ["id", "name", "version", "author", "description", "main", "hooks"]
VALID_HOOKS = ["on_join", "on_leave", "on_message", "on_command", "on_callback", "on_error",
               "on_verify", "on_edited_message", "on_channel_post", "on_inline_query",
               "on_poll", "on_poll_answer", "on_my_chat_member", "on_chat_member",
               "on_chat_join_request"]
VALID_PERMISSIONS = ["read_messages", "send_messages", "edit_messages", "delete_messages",
                     "kick_members", "restrict_members", "promote_members", "invite_members",
                     "pin_messages", "manage_chat", "manage_topics"]


def validate_manifest(manifest_path: Path) -> list:
    """Validate manifest.json file."""
    errors = []

    if not manifest_path.exists():
        return ["manifest.json not found"]

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in manifest.json: {e}"]

    # Check required fields
    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    # Validate field formats
    if "id" in manifest:
        plugin_id = manifest["id"]
        if not plugin_id.replace("_", "").replace("-", "").isalnum():
            errors.append(f"Invalid plugin ID format: {plugin_id}")
        if not plugin_id[0].islower():
            errors.append(f"Plugin ID must start with lowercase: {plugin_id}")

    if "version" in manifest:
        version = manifest["version"]
        parts = version.split(".")
        if len(parts) < 2 or len(parts) > 3:
            errors.append(f"Invalid version format (use semver): {version}")

    if "hooks" in manifest:
        for hook in manifest["hooks"]:
            if hook not in VALID_HOOKS:
                errors.append(f"Unknown hook: {hook}")

    if "permissions" in manifest:
        for perm in manifest["permissions"]:
            if perm not in VALID_PERMISSIONS:
                errors.append(f"Unknown permission: {perm}")

    return errors


def validate_main_py(main_path: Path) -> list:
    """Validate main.py file."""
    errors = []

    if not main_path.exists():
        return ["main.py not found"]

    try:
        with open(main_path) as f:
            source = f.read()

        # Check syntax
        ast.parse(source)

        # Check for plugin export
        if "plugin = " not in source:
            errors.append("main.py must export 'plugin' variable")

    except SyntaxError as e:
        errors.append(f"Syntax error in main.py: {e}")

    return errors


def validate_readme(readme_path: Path) -> list:
    """Validate README.md exists."""
    if not readme_path.exists():
        return ["README.md not found"]
    return []


def validate_plugin(plugin_dir: Path) -> dict:
    """Validate a single plugin directory."""
    result = {
        "path": str(plugin_dir.relative_to(PLUGINS_DIR.parent)),
        "valid": True,
        "errors": []
    }

    # Validate manifest
    manifest_errors = validate_manifest(plugin_dir / "manifest.json")
    result["errors"].extend([f"manifest: {e}" for e in manifest_errors])

    # Read manifest for main file
    manifest_path = plugin_dir / "manifest.json"
    main_file = "main.py"
    if manifest_path.exists():
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
                main_file = manifest.get("main", "main.py")
        except:
            pass

    # Validate main.py
    main_errors = validate_main_py(plugin_dir / main_file)
    result["errors"].extend([f"main: {e}" for e in main_errors])

    # Validate README
    readme_errors = validate_readme(plugin_dir / "README.md")
    result["errors"].extend([f"readme: {e}" for e in readme_errors])

    result["valid"] = len(result["errors"]) == 0
    return result


def main():
    """Validate all plugins."""
    print("Validating plugins...")
    print(f"Plugins directory: {PLUGINS_DIR}")
    print()

    if not PLUGINS_DIR.exists():
        print(f"ERROR: Plugins directory not found: {PLUGINS_DIR}")
        sys.exit(1)

    plugin_dirs = [d for d in PLUGINS_DIR.iterdir() if d.is_dir()]

    if not plugin_dirs:
        print("No plugins found to validate")
        sys.exit(0)

    results = []
    valid_count = 0
    invalid_count = 0

    for plugin_dir in sorted(plugin_dirs):
        result = validate_plugin(plugin_dir)
        results.append(result)

        if result["valid"]:
            valid_count += 1
            print(f"✓ {plugin_dir.name}")
        else:
            invalid_count += 1
            print(f"✗ {plugin_dir.name}")
            for error in result["errors"]:
                print(f"  - {error}")

    print()
    print(f"Results: {valid_count} valid, {invalid_count} invalid")

    if invalid_count > 0:
        sys.exit(1)

    print("All plugins valid!")


if __name__ == "__main__":
    main()
