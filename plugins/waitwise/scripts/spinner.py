#!/usr/bin/env python3
"""Manage the Claude Code spinner verbs (the line shown while Claude works).

Commands:
  list                      Show the bundled presets as JSON.
  apply --preset ID         Install a bundled preset.
  apply --file PATH         Install a custom list (one line per verb).
  status                    Show what is installed now.
  restore                   Put back the spinnerVerbs value from before waitwise.

Options for apply:
  --mode replace|append     replace hides the default verbs (default: replace).

Only the "spinnerVerbs" key in settings.json is changed. The previous value is
saved once, so "restore" can put it back.
"""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
PRESETS_DIR = PLUGIN_ROOT / "presets"
MAX_LEN = 60


def config_dir():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def settings_path():
    return config_dir() / "settings.json"


def state_path():
    return config_dir() / "waitwise-state.json"


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def read_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{path} is not valid JSON ({e}). Nothing was changed.")


def write_json_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".waitwise-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def load_lines(path):
    lines = []
    seen = set()
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip().rstrip(".!")
        if line and line not in seen:
            seen.add(line)
            lines.append(line)
    if not lines:
        fail(f"{path} has no lines.")
    return lines


def presets():
    out = []
    for d in sorted(PRESETS_DIR.iterdir()):
        meta_file, lines_file = d / "preset.json", d / "lines.txt"
        if not (meta_file.exists() and lines_file.exists()):
            continue
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        meta["id"] = d.name
        meta["count"] = len(load_lines(lines_file))
        out.append(meta)
    return out


def cmd_list(_):
    print(json.dumps(presets(), indent=2, ensure_ascii=False))


def cmd_apply(args):
    if bool(args.preset) == bool(args.file):
        fail("use exactly one of --preset or --file.")
    if args.preset:
        lines_file = PRESETS_DIR / args.preset / "lines.txt"
        if not lines_file.exists():
            ids = ", ".join(p["id"] for p in presets())
            fail(f"unknown preset '{args.preset}'. Presets: {ids}")
        source = f"preset:{args.preset}"
    else:
        lines_file = Path(args.file).expanduser()
        if not lines_file.exists():
            fail(f"{lines_file} does not exist.")
        source = f"file:{lines_file.resolve()}"
    lines = load_lines(lines_file)
    too_long = [l for l in lines if len(l) > MAX_LEN]

    settings = read_json(settings_path(), {})
    state = read_json(state_path(), None)
    if state is None:
        # First install: keep the value from before waitwise for "restore".
        state = {"previous": settings.get("spinnerVerbs")}
    state["source"] = source
    state["mode"] = args.mode
    state["count"] = len(lines)

    settings["spinnerVerbs"] = {"mode": args.mode, "verbs": lines}
    write_json_atomic(settings_path(), settings)
    write_json_atomic(state_path(), state)

    print(f"Installed {len(lines)} lines from {source} (mode: {args.mode}) into {settings_path()}")
    if too_long:
        print(f"warning: {len(too_long)} lines are over {MAX_LEN} characters and may be cut off on narrow terminals.")


def cmd_status(_):
    settings = read_json(settings_path(), {})
    state = read_json(state_path(), None)
    sv = settings.get("spinnerVerbs")
    print(json.dumps({
        "settings": str(settings_path()),
        "installed_by_waitwise": state is not None,
        "source": state and state.get("source"),
        "mode": sv and sv.get("mode"),
        "count": sv and len(sv.get("verbs", [])),
        "sample": sv and sv.get("verbs", [])[:3],
    }, indent=2, ensure_ascii=False))


def cmd_restore(_):
    state = read_json(state_path(), None)
    if state is None:
        fail("waitwise has not installed anything, so there is nothing to restore.")
    settings = read_json(settings_path(), {})
    if state.get("previous") is None:
        settings.pop("spinnerVerbs", None)
    else:
        settings["spinnerVerbs"] = state["previous"]
    write_json_atomic(settings_path(), settings)
    state_path().unlink()
    print(f"Restored the spinner verbs from before waitwise in {settings_path()}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(func=cmd_list)
    a = sub.add_parser("apply")
    a.add_argument("--preset")
    a.add_argument("--file")
    a.add_argument("--mode", choices=["replace", "append"], default="replace")
    a.set_defaults(func=cmd_apply)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("restore").set_defaults(func=cmd_restore)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
