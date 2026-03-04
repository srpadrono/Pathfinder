# Installation

## Requirements

- Python 3
- Git
- A UI test framework (auto-detected)

## Setup

```bash
git clone https://github.com/srpadrono/Pathfinder.git ~/.pathfinder
cd your-project
python3 ~/.pathfinder/scripts/pathfinder-init.py
```

## Verify

Tell your AI agent `/map` — it should invoke `pathfinder:mapping` and start discovering journeys.
