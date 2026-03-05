# Installing Pathfinder for Codex

Enable Pathfinder skills in Codex via native skill discovery. Clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the Pathfinder repository:**
   ```bash
   git clone https://github.com/srpadrono/Pathfinder.git ~/.codex/pathfinder
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/pathfinder/skills ~/.agents/skills/pathfinder
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\pathfinder" "$env:USERPROFILE\.codex\pathfinder\skills"
   ```

3. **Restart Codex** (quit and relaunch the CLI) to discover the skills.

## Verify

```bash
ls -la ~/.agents/skills/pathfinder
```

You should see a symlink pointing to your Pathfinder skills directory.

## Usage

Codex will discover skills automatically from `~/.agents/skills/pathfinder/`.
The `using-pathfinder` meta-skill provides routing to all other skills.

### Tool Mapping

When Pathfinder skills reference tools by canonical names, use Codex equivalents:

| Canonical Tool | Codex Equivalent |
|----------------|------------------|
| `Read` | `read_file` |
| `Edit` | `edit_file` |
| `Bash` | `shell` |
| `Skill` tool | Read `skills/` file directly |

### Key Commands

Start the Pathfinder workflow by telling Codex:

- "Load the pathfinder:surveying skill and start a survey"
- "Load the pathfinder:scouting skill and write tests"
- "Load the pathfinder:building skill and implement"
- "Load the pathfinder:reporting skill and generate a report"

## Updating

```bash
cd ~/.codex/pathfinder && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/pathfinder
```

Optionally delete the clone: `rm -rf ~/.codex/pathfinder`
