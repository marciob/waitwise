# waitwise

Replace Claude Code's spinner with anything useful.

While Claude Code works, its spinner shows a random word such as "Pondering…". waitwise is a Claude Code plugin that replaces those words with content that you choose.

When you run the setup, your own Claude asks what you want to see. You can give any theme, and Claude writes the list for you. Or you can start from a preset. Some examples:

```
✻ Owning beats owing…                 (affirmations)
✻ Rain falls. The build waits…        (Zen)
✻ madrugar — to get up early…         (Spanish flashcards)
```

## Requirements

- Claude Code
- Python 3, available as `python3`

## Install

Run these commands in a Claude Code session:

1. Add the marketplace from GitHub:
   ```
   /plugin marketplace add marciob/waitwise
   ```
2. Install the plugin:
   ```
   /plugin install waitwise@waitwise
   ```
3. Run the setup:
   ```
   /waitwise:setup
   ```

The new lines show in the spinner of your next message. You do not have to restart Claude Code.

## Commands

| Command | Result |
|---|---|
| `/waitwise:setup` | Claude asks which use case you want and installs it. |
| `/waitwise:setup <preset-id>` | Installs that preset immediately. |
| `/waitwise:setup status` | Shows what is installed now. |
| `/waitwise:setup restore` | Puts back the spinner that you had before waitwise. |

## Presets

### Mindset

| ID | Content |
|---|---|
| `positive-affirmations` | 2,000 affirmations. Most are about prosperity, money and career. |
| `stoic-wisdom` | 600 short lines of Stoic wisdom. 80 of them are paraphrases of Seneca, Marcus Aurelius, Epictetus, Musonius Rufus and Zeno. |
| `zen-monk` | 500 calm, short lines in the voice of a Zen monk. |

### Learn a language

Each line shows a word or phrase and its English meaning.

| ID | Content |
|---|---|
| `flashcards-spanish` | 500 Spanish words and phrases, A2 to B2 |
| `flashcards-french` | 500 French words and phrases, A2 to B2 |
| `flashcards-german` | 500 German words and phrases with articles, A2 to B2 |
| `flashcards-japanese` | 500 Japanese words with romaji, JLPT N5 to N3 |

### Custom theme

Select "Custom theme" in the setup. Claude asks for a theme, a tone and a language. Then it writes 300 lines and installs them.

## How it works

- Claude Code reads the `spinnerVerbs` key in `~/.claude/settings.json`. If you set `CLAUDE_CONFIG_DIR`, it reads the file in that folder.
- Claude Code selects one random line each time the spinner appears. The line stays until the spinner closes.
- If a task list has a step in progress, the spinner shows that step instead of a line from your list.
- The script `plugins/waitwise/scripts/spinner.py` writes only the `spinnerVerbs` key. It does not change other settings.
- The first time you install a list, the script saves your old `spinnerVerbs` value in `waitwise-state.json`. The `restore` command uses this file.
- If `settings.json` is not valid JSON, the script stops and changes nothing.

## Uninstall

1. Run `/waitwise:setup restore` to put back your old spinner.
2. Run `/plugin uninstall waitwise@waitwise`.

If you uninstall the plugin first, your list stays in `settings.json`. To remove it, delete the `spinnerVerbs` key from that file.

## Add a preset

1. Make a folder `plugins/waitwise/presets/<id>/`.
2. Put one line per verb in `lines.txt`. Keep each line at 60 characters or fewer. Do not put punctuation at the end, because Claude Code adds "…".
3. Add `preset.json`:
   ```json
   { "name": "Display name", "description": "One sentence.", "language": "en", "group": "Mindset" }
   ```
   The setup groups the presets by `group`.
4. Run `claude plugin validate .` from the repository root.

## License

MIT
