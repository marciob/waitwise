---
name: setup
description: Set up what Claude Code shows in its spinner (the line shown while Claude works). Use when the user wants to install, change, customize or remove their spinner verbs, e.g. positive affirmations, Stoic wisdom, or a custom theme.
argument-hint: "[preset-id | restore | status]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/spinner.py *)
---

# Set up the spinner

The spinner line is the text Claude Code shows while it works, such as "Pondering…". Claude Code picks one random line from a list each time the spinner appears, and keeps that line until the spinner closes. This skill installs that list in the `spinnerVerbs` key of the user's `settings.json`. The change takes effect on the next spinner. No restart is necessary.

All changes go through this script. Do not edit `settings.json` yourself.

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/spinner.py list|status|restore
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/spinner.py apply --preset <id> [--mode replace|append]
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/spinner.py apply --file <path> [--mode replace|append]
```

## Shortcuts

If the user gave an argument (`$ARGUMENTS`), do this and stop:
- `restore`: run `restore` and tell the user the old spinner is back.
- `status`: run `status` and describe the result in one or two sentences.
- A preset id: run `apply --preset <id>` and go to step 4.

## Steps

1. Run `list` to get the presets.
2. Use AskUserQuestion to ask which use case the user wants. AskUserQuestion shows at most 4 options, so ask in two steps:
   1. Ask for the group. Make one option for each `group` value in the preset list, and describe it with the names of its presets. Also add one option labeled "Custom theme", described as "Tell me a theme and I write the list for you".
   2. If the user selected a group with more than one preset, ask for the preset in that group. Use the preset `name` as the label and the `description` plus the line count as the description. If the group has more than 4 presets, show the 3 most likely ones; the user can type another one in "Other".
3. Apply the choice:
   - **A preset**: run `apply --preset <id>`.
   - **Custom theme**: follow "Write a custom list" below.
4. Tell the user what is installed now and that they can see it in the spinner of their next message. Also tell them how to undo it: `/waitwise:setup restore`.

Use `--mode replace` (the default), which hides Claude Code's default verbs. Use `--mode append` only if the user wants to keep the default verbs mixed in.

## Write a custom list

1. Ask only what you cannot infer, in one AskUserQuestion call with up to three questions:
   - **Theme**: what the lines are about. Offer 3 ideas that fit what you know about the user, for example their language, work or interests.
   - **Tone**: for example sincere, calm, energetic or dry.
   - **Language**: the language of the lines.
2. Write 300 lines, unless the user asked for a different number. Rules for each line:
   - 60 characters or fewer. Aim for 3 to 9 words.
   - No punctuation at the end. Claude Code adds "…" after each line.
   - Concrete and specific. Do not write generic poster lines.
   - Vary how the lines start. No two lines start with the same three words.
   - No two lines have almost the same meaning.
3. Save the lines, one per line, to `${CLAUDE_PLUGIN_DATA}/custom/<short-theme-slug>.txt`.
4. Run `apply --file <that path>`.
5. Show the user 5 random lines from the list, then do step 4 of "Steps".
