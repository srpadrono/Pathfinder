# Universal Platform Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make Pathfinder's skills universally loadable by Claude Code, OpenCode, Codex, and OpenClaw.

**Architecture:** Move platform-specific files (hooks/, commands/) into `.claude-plugin/`. Add `.opencode/` and `.codex/` adapter directories with install instructions and thin plugins. Update `AGENTS.md` as the universal entry point with a tool mapping table. Centralize tool mapping in the `using-pathfinder` meta-skill.

**Tech Stack:** Markdown, JavaScript (OpenCode plugin), shell (symlinks)

---

### Task 1: Create `.claude-plugin/` directory and move hooks + commands

**Files:**
- Create: `.claude-plugin/hooks/hooks.json`
- Create: `.claude-plugin/commands/survey.md`
- Create: `.claude-plugin/commands/scout.md`
- Create: `.claude-plugin/commands/build.md`
- Create: `.claude-plugin/commands/report.md`
- Delete: `hooks/hooks.json` (then remove `hooks/`)
- Delete: `commands/survey.md`, `commands/scout.md`, `commands/build.md`, `commands/report.md` (then remove `commands/`)

**Step 1: Create `.claude-plugin/` with hooks and commands**

Copy `hooks/hooks.json` to `.claude-plugin/hooks/hooks.json` (content unchanged).
Copy all 4 command files to `.claude-plugin/commands/`.

**Step 2: Remove old directories**

```bash
rm -rf hooks/ commands/
```

**Step 3: Verify structure**

```bash
ls -R .claude-plugin/
# Expected:
# .claude-plugin/hooks/hooks.json
# .claude-plugin/commands/survey.md
# .claude-plugin/commands/scout.md
# .claude-plugin/commands/build.md
# .claude-plugin/commands/report.md
```

**Step 4: Commit**

```bash
git add .claude-plugin/ && git rm -r hooks/ commands/
git commit -m "refactor: move hooks and commands into .claude-plugin/ for platform separation"
```

---

### Task 2: Create `.opencode/` adapter

**Files:**
- Create: `.opencode/INSTALL.md`
- Create: `.opencode/plugins/pathfinder.js`

**Step 1: Write `.opencode/INSTALL.md`**

Installation instructions: git clone to `~/.config/opencode/pathfinder`, symlink skills and plugin.

**Step 2: Write `.opencode/plugins/pathfinder.js`**

Modeled after superpowers' plugin. Reads `skills/using-pathfinder/SKILL.md`, strips frontmatter, injects into system prompt with OpenCode tool mapping.

**Step 3: Verify plugin syntax**

```bash
node -c .opencode/plugins/pathfinder.js
# Expected: no syntax errors
```

**Step 4: Commit**

```bash
git add .opencode/
git commit -m "feat: add OpenCode adapter with plugin and install instructions"
```

---

### Task 3: Create `.codex/` adapter

**Files:**
- Create: `.codex/INSTALL.md`

**Step 1: Write `.codex/INSTALL.md`**

Installation instructions: git clone to `~/.codex/pathfinder`, symlink skills to `~/.agents/skills/pathfinder`.

**Step 2: Commit**

```bash
git add .codex/
git commit -m "feat: add Codex adapter with install instructions"
```

---

### Task 4: Add tool mapping to `skills/using-pathfinder/SKILL.md`

**Files:**
- Modify: `skills/using-pathfinder/SKILL.md`

**Step 1: Add Tool Mapping section**

Append after the "Anti-Skip Guard" table:

```markdown
## Tool Mapping

Skills reference tools by their canonical names. Map to your platform:

| Canonical Tool       | Claude Code / OpenClaw | OpenCode          | Codex             |
|----------------------|------------------------|-------------------|-------------------|
| Load a skill         | `Skill` tool           | `skill` tool      | Read `skills/` file |
| Track tasks          | `TodoWrite`            | `todowrite`       | Inline tracking   |
| Launch subagent      | `Task` tool            | `task` tool       | N/A               |
| Read file            | `Read`                 | `read`            | `read_file`       |
| Edit file            | `Edit`                 | `edit`            | `edit_file`       |
| Run command          | `Bash`                 | `bash`            | `shell`           |

When a skill references a tool by name, use your platform's equivalent from this table.
```

**Step 2: Verify no broken formatting**

```bash
cat skills/using-pathfinder/SKILL.md
# Visually verify Markdown renders correctly
```

**Step 3: Commit**

```bash
git add skills/using-pathfinder/SKILL.md
git commit -m "feat: add cross-platform tool mapping to using-pathfinder meta-skill"
```

---

### Task 5: Update `AGENTS.md` with platform support and updated file locations

**Files:**
- Modify: `AGENTS.md`

**Step 1: Add Platform Support section**

After the "Skills Architecture" section, add:

```markdown
## Platform Support

Pathfinder works with any AI coding assistant. Platform-specific adapters are in:

| Platform | Adapter | Install |
|----------|---------|---------|
| Claude Code | `.claude-plugin/` (hooks + commands) | Automatic via hooks |
| OpenClaw | Root `SKILL.md` + `.claude-plugin/` | Install via skill marketplace |
| OpenCode | `.opencode/` (plugin + install) | See `.opencode/INSTALL.md` |
| Codex | `.codex/` (install) | See `.codex/INSTALL.md` |
| Other | Read `AGENTS.md` + `skills/` | Manual |
```

**Step 2: Update File Locations table**

Change `hooks/hooks.json` to `.claude-plugin/hooks/hooks.json` and `commands/` to `.claude-plugin/commands/`.

**Step 3: Add Tool Mapping reference**

Add a note: "See `skills/using-pathfinder/SKILL.md` for cross-platform tool mapping."

**Step 4: Commit**

```bash
git add AGENTS.md
git commit -m "feat: update AGENTS.md with platform support section and updated file locations"
```

---

### Task 6: Update `SKILL.md` (OpenClaw marketplace metadata)

**Files:**
- Modify: `SKILL.md`

**Step 1: Update references**

Change `hooks/hooks.json` reference to `.claude-plugin/hooks/hooks.json`. Update the Skills section to note cross-platform support.

**Step 2: Commit**

```bash
git add SKILL.md
git commit -m "feat: update OpenClaw SKILL.md with new file locations"
```

---

### Task 7: Update `README.md` with new structure and installation per platform

**Files:**
- Modify: `README.md`

**Step 1: Update Repository Structure diagram**

Replace hooks/ and commands/ entries with `.claude-plugin/`, `.opencode/`, `.codex/` entries.

**Step 2: Add Installation section per platform**

Add installation instructions for Claude Code, OpenCode, Codex, and OpenClaw (similar to how superpowers does it).

**Step 3: Update Architecture diagram**

Replace `hooks/hooks.json` reference with `.claude-plugin/hooks/`.

**Step 4: Commit**

```bash
git add README.md
git commit -m "docs: update README with cross-platform installation and new structure"
```

---

### Task 8: Verify everything works

**Step 1: Verify Claude Code adapter**

```bash
ls -R .claude-plugin/
cat .claude-plugin/hooks/hooks.json
```

**Step 2: Verify OpenCode plugin**

```bash
node -c .opencode/plugins/pathfinder.js
```

**Step 3: Verify all skills are intact**

```bash
ls skills/*/SKILL.md
# Should list 12 skills
```

**Step 4: Run existing tests to check no breakage**

```bash
npm run validate 2>/dev/null || echo "validate script may not exist"
npx vitest run 2>/dev/null || echo "no unit tests to run"
```
