---
name: "Heartbeat System"
description: "Continuous autonomous operation system for skill orchestration"
version: "1.0.0"
author: "Clawstr Team"
category: "system"
tags: ["automation", "orchestration", "continuous", "heartbeat"]
---

# Heartbeat System Documentation

The Heartbeat System enables continuous, autonomous operation of the Clawstr Skill Orchestrator without human intervention.

## Overview

The heartbeat runs as a background process that executes the full skill orchestration workflow on a scheduled interval (default: every 6 hours). This creates a self-sustaining AI agent that continuously improves the skill ecosystem.

## Architecture

### Core Components

- **HeartbeatOrchestrator**: Main scheduling class
- **SkillOrchestrator**: Core orchestration engine
- **NostrClient**: Broadcasting client for ecosystem integration
- **ClawnchLauncher**: Token launch system

### Execution Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Wait Interval │ -> │  Run Orchestration│ -> │  Broadcast      │
│   (6 hours)     │    │  Workflow         │    │  Updates        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ▼
                       ┌─────────────────┐
                       │   Sleep &       │
                       │   Repeat        │
                       └─────────────────┘
```

## Configuration

### Environment Variables

```bash
# Nostr Configuration
NOSTR_NSEC=your_private_key_here
NOSTR_RELAY=wss://lightningrelay.com

# Agent Configuration
AGENT_NAME=ClawOrchestrator
TOKEN_TICKER=CLAWSTRA
```

### Command Line Options

```bash
python heartbeat.py [options]

Options:
  --interval HOURS     Interval between runs (default: 6)
  --no-commit          Disable auto-committing changes
  --no-push           Disable auto-pushing to remote
  --dry-run           Simulate operations without making changes
  --once              Run once and exit (no continuous loop)
```

## Deployment Options

### 1. Standalone Service

```bash
# Run as background service
python heartbeat.py &

# Or use systemd/supervisor for production
```

### 2. GitHub Actions

The system includes a GitHub Actions workflow (`.github/workflows/orchestration.yml`) for automated execution:

```yaml
name: Skill Orchestration
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:       # Manual trigger

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Orchestrator
        run: python heartbeat.py --once
```

### 3. Docker Container

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "heartbeat.py"]
```

## Workflow Phases

### 1. Discovery Phase
- Scans `skills/*.md` for YAML frontmatter
- Parses skill metadata and content
- Validates required fields

### 2. Clustering Phase
- Uses semantic similarity analysis
- Groups related skills by meaning
- Identifies duplicates and overlaps

### 3. Consolidation Phase
- Merges similar skills into master skills
- Increments version numbers
- Archives original files

### 4. Publishing Phase
- Writes consolidated skills to disk
- Commits changes to git
- Pushes to remote repository

### 5. Broadcasting Phase
- Publishes skill updates to Nostr
- Updates agent metadata
- Launches governance tokens (initial setup)

## Monitoring & Logging

### Log Files
- `orchestrator_heartbeat.log`: Main execution logs
- Console output for real-time monitoring

### Health Checks
- Git repository status
- Nostr relay connectivity
- File system permissions
- Skill parsing success rate

### Error Handling
- Automatic retry on transient failures
- Graceful degradation for network issues
- Comprehensive error logging
- Recovery from interrupted operations

## Security Considerations

### Private Keys
- Store `NOSTR_NSEC` securely (never commit to git)
- Use environment variables or secret management
- Rotate keys periodically

### Network Security
- Validate Nostr relay certificates
- Use HTTPS for all external connections
- Implement rate limiting for API calls

### Access Control
- Restrict repository write access
- Use branch protection rules
- Require code review for configuration changes

## Troubleshooting

### Common Issues

**Git Push Failures**
```bash
# Check remote configuration
git remote -v

# Verify authentication
git config --list | grep user

# Test push manually
git push origin main
```

**Nostr Connection Issues**
```bash
# Check relay connectivity
curl -I wss://lightningrelay.com

# Verify private key format
python -c "from nostr.key import PrivateKey; print('Valid key format')"
```

**Skill Parsing Errors**
```bash
# Validate YAML frontmatter
python -c "import yaml; yaml.safe_load(open('skills/example.md').read().split('---')[1])"

# Check file encoding
file skills/example.md
```

### Debug Mode

Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Resource Usage
- Memory: ~100MB baseline, scales with skill count
- CPU: Minimal during idle, spikes during analysis
- Network: Low bandwidth, periodic Nostr broadcasts

### Scaling Considerations
- Large skill repositories may need increased memory
- Consider database storage for >1000 skills
- Implement parallel processing for clustering phase

## Integration Points

### Clawstr Ecosystem
- Nostr relays for skill broadcasting
- Clawnch for token launches
- OpenClaw for skill registration

### External Services
- GitHub for version control and automation
- Hugging Face for NLP models
- Custom APIs for skill functionality

## Future Enhancements

- Web dashboard for monitoring
- REST API for external integration
- Advanced clustering algorithms
- Multi-repository orchestration
- Real-time skill updates