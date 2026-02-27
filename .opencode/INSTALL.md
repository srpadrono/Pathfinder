# Installing Pathfinder for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- Git installed

## Installation Steps

### 1. Clone Pathfinder

```bash
git clone https://github.com/srpadrono/Pathfinder.git ~/.config/opencode/pathfinder
```

### 2. Register the Plugin

Create a symlink so OpenCode discovers the plugin:

```bash
mkdir -p ~/.config/opencode/plugins
rm -f ~/.config/opencode/plugins/pathfinder.js
ln -s ~/.config/opencode/pathfinder/.opencode/plugins/pathfinder.js ~/.config/opencode/plugins/pathfinder.js
```

### 3. Symlink Skills

Create a symlink so OpenCode's native skill tool discovers Pathfinder skills:

```bash
mkdir -p ~/.config/opencode/skills
rm -rf ~/.config/opencode/skills/pathfinder
ln -s ~/.config/opencode/pathfinder/skills ~/.config/opencode/skills/pathfinder
```

### 4. Restart OpenCode

Restart OpenCode. The plugin will automatically inject Pathfinder context at session start.

Verify by asking: "do you have Pathfinder skills?"

## Usage

### Loading a Skill

Use OpenCode's native `skill` tool:

```
use skill tool to load pathfinder/surveying
```

### Slash Commands (via natural language)

Since OpenCode doesn't have slash commands, use natural language:

- "Start a survey" (triggers `pathfinder:surveying`)
- "Scout this feature" (triggers `pathfinder:scouting`)
- "Build this feature" (triggers `pathfinder:building`)
- "Generate a report" (triggers `pathfinder:reporting`)

### Tool Mapping

When Pathfinder skills reference tools by canonical names, OpenCode equivalents are:

| Canonical Tool       | OpenCode Equivalent   |
|----------------------|-----------------------|
| `Skill` tool         | `skill` tool          |
| `TodoWrite`          | `todowrite`           |
| `Task` tool          | `task` tool           |
| `Read`               | `read`                |
| `Edit`               | `edit`                |
| `Bash`               | `bash`                |

## Updating

```bash
cd ~/.config/opencode/pathfinder && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm -f ~/.config/opencode/plugins/pathfinder.js
rm -rf ~/.config/opencode/skills/pathfinder
```

Optionally delete the clone: `rm -rf ~/.config/opencode/pathfinder`
