---
name: "Skill Template"
description: "A template for creating Clawstr AI skills"
version: "1.0.0"
author: "Clawstr Community"
category: "template"
tags: ["template", "example", "documentation"]
---

# Skill Template

This is a template for creating skills in the Clawstr ecosystem.

## Overview

Skills are the building blocks of AI agents in Clawstr. Each skill is a markdown file with YAML frontmatter that defines its metadata and capabilities.

## Required Frontmatter Fields

- `name`: The skill's display name
- `description`: Brief description of what the skill does
- `version`: Semantic version (e.g., "1.0.0")
- `author`: Creator or maintainer of the skill
- `category`: Primary category for organization
- `tags`: Array of relevant tags for discovery

## Skill Content

The content below the frontmatter should include:

- Detailed description of capabilities
- Usage instructions
- Examples
- Parameters and configuration
- Dependencies and requirements

## Example Usage

```yaml
---
name: "API Connector"
description: "Connect to external APIs and fetch data"
version: "2.1.0"
author: "Clawstr Team"
category: "integration"
tags: ["api", "http", "data-fetching"]
---
```

## Publishing

Skills are automatically discovered, analyzed, and consolidated by the Skill Orchestrator. The system:

1. Scans for `*.md` files in the `skills/` directory
2. Parses YAML frontmatter
3. Clusters similar skills using semantic analysis
4. Consolidates duplicates and creates master skills
5. Archives originals and publishes updates
6. Broadcasts changes to the Clawstr ecosystem via Nostr

## Best Practices

- Use clear, descriptive names
- Include comprehensive documentation
- Version appropriately (follow semantic versioning)
- Tag skills with relevant categories
- Test skills before publishing
- Keep descriptions concise but informative