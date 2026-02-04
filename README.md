# Clawstr Automated Skill Orchestrator

An intelligent automation system for the Clawstr AI Agent framework that discovers, analyzes, consolidates, and publishes AI skills with zero manual intervention.

## Overview

The Skill Orchestrator acts as an autonomous custodian that:

1. **Discovers** all .md files in the ./skills/ directory
2. **Clusters** skills using semantic similarity analysis
3. **Identifies** duplicates and overlapping skills
4. **Consolidates** them into unified master skills
5. **Publishes** updated skills with incremented versions
6. **Archives** original files for versioning
7. **Commits & Pushes** changes automatically
8. **Broadcasts** skill updates to the Clawstr ecosystem via Nostr

## Autonomous Operation Loop

The orchestrator maintains its autonomy through a continuous heartbeat loop that runs every 6 hours:

### The Loop:
1. **Discovery**: Scans `./skills/*.md` for YAML frontmatter
2. **Analysis**: Uses semantic similarity to group related skills
3. **Consolidation**: Merges similar skills, increments versions, archives originals
4. **Publication**: Updates master skills and commits changes
5. **Broadcasting**: Publishes updates to Nostr for Clawstr ecosystem integration
6. **Sleep**: Waits 6 hours before next cycle

### Nostr Integration:
- **Identity**: Broadcasts Kind 0 metadata with agent profile
- **Skills**: Publishes Kind 30023 events for each updated skill
- **Token Launch**: Posts Kind 1 event to launch governance token on Clawnch
- **Relay**: Connects to `wss://lightningrelay.com` for ecosystem compatibility

### Initial Setup:
Upon first run, the agent:
- Broadcasts its metadata to establish presence in Clawstr
- Launches its governance token on Clawnch (one-time operation)
- Begins the autonomous orchestration cycle

This creates a fully autonomous agent that continuously improves the skill ecosystem without human intervention.

## Deployment Options

### 🚀 GitHub Actions Deployment (Recommended)

Your repository is already configured with GitHub Actions for automated orchestration. This is the **recommended deployment method** for full functionality.

#### **Current Setup:**
- ✅ **Automated**: Runs every 6 hours automatically
- ✅ **Full Features**: Git operations, ML clustering, Nostr broadcasting
- ✅ **Free**: Uses GitHub's free tier
- ✅ **Integrated**: Works with GitHub's permission system

#### **Setup Instructions:**

1. **Set up Repository Secrets:**
   Go to your GitHub repository → Settings → Secrets and variables → Actions

   Add these secrets:
   ```
   NOSTR_NSEC     → Your Nostr private key (nsec1...)
   NOSTR_RELAY    → wss://lightningrelay.com
   AGENT_NAME     → ClawOrchestrator
   TOKEN_TICKER   → CLAWOSTRA
   ```

2. **The workflow will:**
   - Run automatically every 6 hours
   - Discover and analyze skills
   - Consolidate duplicates using ML
   - Commit and push changes
   - Broadcast updates to Nostr

3. **Manual Triggers:**
   You can also trigger runs manually:
   - Go to Actions tab → "Skill Orchestration" → "Run workflow"
   - Choose mode: `normal`, `dry-run`, or `force`

#### **Workflow Features:**
- **Scheduled Runs**: Every 6 hours (`0 */6 * * *`)
- **Manual Dispatch**: Run on-demand with different modes
- **Environment Variables**: Securely stored as GitHub secrets
- **Git Integration**: Automatic commits with detailed messages
- **Error Handling**: Continues even if individual steps fail
- **Logging**: Full logs available in Actions tab

#### **Monitoring:**
- Check the **Actions** tab for run history
- View detailed logs for each execution
- See commit history for bot-generated changes
- Monitor Nostr broadcasts in your relay

### ☁️ Vercel Deployment (Limited)

For web API access, you can deploy a limited version to Vercel:

#### Setup:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

#### Available Endpoints:
- `GET /health` - Health check
- `POST /orchestrate` - Trigger skill discovery (read-only)
- `GET /metadata` - Get agent metadata

#### ⚠️ Limitations:
- **No Background Processing**: Cannot run continuous heartbeat
- **No Git Operations**: Cannot commit/push changes
- **No ML Clustering**: Sentence transformers excluded (too large)
- **Read-Only**: Can only discover skills, not modify them
- **Timeout Limits**: 30-second execution limit

#### Environment Variables for Vercel:
```bash
NOSTR_NSEC=your_private_key
NOSTR_RELAY=wss://lightningrelay.com
AGENT_NAME=ClawOrchestrator
```

### � Railway Deployment (Recommended for Full Functionality)

Railway provides full Python application support with persistent storage, background processes, and continuous operation:

#### **Setup:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

#### **Environment Variables:**
Set these in Railway dashboard (`railway variables`):

```bash
NOSTR_NSEC=your_private_key_here
NOSTR_RELAY=wss://lightningrelay.com
AGENT_NAME=ClawOrchestrator
TOKEN_TICKER=CLAWOSTRA
```

#### **Features on Railway:**
- ✅ **Full Autonomous Operation**: Heartbeat runs continuously
- ✅ **Git Operations**: Commit and push changes automatically
- ✅ **ML Processing**: Sentence transformers work normally
- ✅ **Persistent Storage**: File system persists between runs
- ✅ **Health Monitoring**: HTTP health checks available
- ✅ **Background Processes**: Multiple services can run

#### **Access Points:**
- **Health Check**: `https://your-app.railway.app/health`
- **Service Info**: `https://your-app.railway.app/`
- **Logs**: `railway logs`

#### **Scaling:**
Railway automatically scales based on usage. For production workloads, consider their Pro plan for more resources.

### 🖥️ Local Development

For development and testing:

```bash
# Clone and setup
git clone https://github.com/yourusername/clawstr-skill-orchestrator.git
cd clawstr-skill-orchestrator

# Copy environment template
cp .env.example .env
# Edit .env with your values

# Install dependencies
pip install -r requirements.txt

# Test single run
python heartbeat.py --run-once --no-commit

# Run continuously (development only)
python heartbeat.py --interval 1  # Run every hour for testing

# Health check
python heartbeat.py --health-check
```

#### **Development Tips:**
- Use `--no-commit` for testing without affecting git history
- Use `--run-once` to test single executions
- Check logs in `orchestrator_heartbeat.log`
- Use shorter intervals for faster testing

### Class Structure

#### `SkillOrchestrator` (Main Engine)

The central orchestration class with distinct workflow phases:

```python
class SkillOrchestrator:
    # Discovery Phase
    discover_skills(target_dir) → List[Skill]
    _parse_skill_file(file_path) → Skill
    
    # Clustering Phase
    cluster_skills(threshold) → Dict[cluster_id, List[Skill]]
    
    # Consolidation Phase
    consolidate_cluster(cluster_id) → MasterSkill
    _merge_descriptions(skills) → str
    _merge_bodies(skills) → str
    _increment_version(version_str) → str
    
    # Publishing Phase
    publish_consolidated_skill(skill, output_dir) → Path
    archive_original_skills(skill_names) → List[Path]
    
    # Git Operations
    commit_changes(message) → str
    push_changes(remote, branch) → bool
    
    # Full Workflow
    run_full_orchestration(...) → Dict[results]
```

#### `NLPHelper` (Semantic Analysis)

Handles skill similarity detection using sentence transformers:

```python
class NLPHelper:
    get_embedding(text) → np.ndarray
    compute_similarity(text1, text2) → float
    cluster_skills(skills, threshold) → Dict[cluster_id, List[Skill]]
    find_duplicates(skills, threshold) → List[Tuple]
```

**Key Features:**
- Uses `all-MiniLM-L6-v2` model for lightweight embeddings
- Cosine similarity for comparison
- Built-in caching to avoid redundant computations
- Configurable thresholds for fine-tuning sensitivity

#### `GitManager` (Repository Management)

Automates Git operations:

```python
class GitManager:
    add_files(file_paths) → None
    remove_files(file_paths) → None
    commit(message, author_name, author_email) → str
    push(remote, branch) → None
    create_branch(branch_name) → None
    checkout_branch(branch_name) → None
    get_file_history(file_path, max_count) → List[dict]
```

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- Git configured with user credentials
- pip package manager

### Step 1: Clone & Navigate

```bash
git clone <repository-url> clawstr-skill-orchestrator
cd clawstr-skill-orchestrator
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

The dependencies include:

- **PyYAML** (6.0.1): Parse YAML frontmatter in SKILL.md files
- **GitPython** (3.1.40): Automated repository operations
- **sentence-transformers** (2.2.2): Semantic embeddings
- **scikit-learn** (included via sentence-transformers): Similarity metrics
- **openai** (1.3.8): Optional LLM API integration
- **python-dotenv** (1.0.0): Environment variable management
- **colorama** (0.4.6): Colored terminal output
- **tqdm** (4.66.1): Progress bars

## SKILL.md File Format

Skills must follow this format with YAML frontmatter:

```markdown
---
name: Skill Name
description: A brief description of what this skill does
version: 1.0.0
author: Your Name
category: skill_category
tags:
  - tag1
  - tag2
---

# Skill Documentation

## Overview
Detailed description...

## Workflow Steps

1. Step 1: Description
2. Step 2: Description
3. Step 3: Description

## Configuration
...
```

**Required Fields:**
- `name`: Unique skill identifier
- `description`: Semantic description (used for clustering)

**Optional Fields:**
- `version`: Semantic version (default: 1.0.0)
- `author`: Skill creator
- `category`: Skill category
- `tags`: List of keywords

## Usage

### Manual Single Run

```bash
python orchestrator.py
```

### Programmatic Usage

```python
from orchestrator import SkillOrchestrator, SkillOrchestratorConfig

# Initialize
config = SkillOrchestratorConfig()
config.similarity_threshold = 0.7  # Adjust clustering sensitivity
config.duplicate_threshold = 0.9   # Adjust duplicate detection

orchestrator = SkillOrchestrator(
    repo_path="/path/to/skills",
    config=config,
    enable_git=True
)

# Run full workflow
result = orchestrator.run_full_orchestration(
    target_dir="skills",
    auto_commit=True,
    auto_push=False
)

print(f"Consolidated {result['skills_consolidated']} skill clusters")
```

### Continuous Execution (Heartbeat)

Run orchestration every 6 hours:

```bash
python heartbeat.py --repo . --interval 6
```

**Options:**

```
--repo PATH           Repository path (default: current directory)
--interval HOURS      Run interval in hours (default: 6)
--run-once            Run once and exit (default: continuous)
--no-commit           Disable auto-commit
--auto-push           Enable auto-push to remote
```

## Workflow Logic

### Phase 1: Discovery

Scans for all SKILL.md files and parses YAML frontmatter:

```
skills/
├── data_processing_skill.md
├── api_integration_skill.md
├── data_validation_skill.md
└── api_connector_skill.md
```

Output:
```
[
  {name: "data_processing_skill", description: "...", ...},
  {name: "api_integration_skill", description: "...", ...},
  ...
]
```

### Phase 2: Clustering

Uses semantic similarity (cosine distance on embeddings) to group skills:

```
Cluster 1 (Data Processing):
  - data_processing_skill (similarity: 1.0)
  - data_validation_skill (similarity: 0.87)

Cluster 2 (API Integration):
  - api_integration_skill (similarity: 1.0)
  - api_connector_skill (similarity: 0.92)
```

**Threshold Configuration:**
- `similarity_threshold = 0.6`: Used for clustering
- `duplicate_threshold = 0.85`: Used for duplicate detection

### Phase 3: Consolidation

Creates master skills by merging clustered skills:

**For Cluster 1:**
- **Master Name:** `data_processing_skill_Master`
- **Description:** Merged descriptions (deduplicated)
- **Body:** Consolidated workflow steps
- **Version:** Incremented (e.g., 1.0.0 → 1.0.1)
- **Metadata:** Includes `merged_from` list

### Phase 4: Publishing

Writes consolidated master skills to SKILL.md files:

```
skills/
├── data_processing_skill_Master.md  (NEW)
├── api_integration_skill_Master.md  (NEW)
└── ...
```

### Phase 5: Archiving

Moves original skills to archive for versioning:

```
archive/
├── data_processing_skill.md
├── data_validation_skill.md
├── api_integration_skill.md
└── api_connector_skill.md
```

### Phase 6 & 7: Git Operations

Automatically commits and optionally pushes changes:

```bash
git add skills/ archive/
git commit -m "Orchestration: Consolidated 2 skill clusters"
git push origin main
```

## Configuration

### SkillOrchestratorConfig

```python
class SkillOrchestratorConfig:
    similarity_threshold = 0.6      # Clustering sensitivity
    duplicate_threshold = 0.85      # Duplicate detection sensitivity
    archive_dir = "archive"         # Archive directory
    skills_dir = "skills"           # Skills directory
    auto_commit = True              # Auto-commit changes
    auto_push = False               # Auto-push changes
```

## Merging Strategy

### Description Merging

- Concatenates unique descriptions from clustered skills
- Removes exact duplicates
- Preserves semantic meaning

### Body Merging

- Extracts workflow steps from each skill
- Deduplicates identical sections
- Combines into unified workflow
- Preserves structured markdown headers

### Version Incrementing

- Semantic versioning (major.minor.patch)
- Patches version on consolidation
- Example: 1.2.3 → 1.2.4

## GitHub Actions Integration

Automatically run orchestration on a schedule:

1. **Scheduled Execution** (every 6 hours):
   ```yaml
   - cron: '0 */6 * * *'
   ```

2. **Manual Trigger** (workflow_dispatch)

3. **Automatic Commits** on changes

See `.github/workflows/orchestration.yml` for full configuration.

### Setting Up GitHub Actions

1. The workflow file is already in `.github/workflows/orchestration.yml`
2. No additional setup needed - it will run automatically
3. Monitor execution in **Actions** tab of your GitHub repo

## OpenClaw Integration

The Skill Orchestrator can be registered as a native skill with the **Clawstr Agent Framework** via **OpenClaw**.

### What is OpenClaw?

[OpenClaw](https://openclaw.ai) is an open-source agent framework that allows you to build autonomous AI agents with composable skills. The Skill Orchestrator integrates seamlessly as a skill within any OpenClaw/Clawstr agent.

### Registration

#### Option 1: CLI Registration

```bash
# Register the orchestrator with your Clawstr agent
python heartbeat.py --register-with-clawstr
```

#### Option 2: Programmatic Registration

```python
from utils.openclaw_integration import register_with_clawstr
from clawstr import Agent

# Create or use existing agent
agent = Agent()

# Register the orchestrator skill
register_with_clawstr(agent)

# Now you can use it in your agent workflows
```

#### Option 3: Manual Script

```bash
python register_skill.py
```

### Using the Skill in Your Agent

Once registered, call the orchestrator from your Clawstr agent:

```python
from clawstr import Agent

agent = Agent()

# Execute orchestration
result = agent.execute_skill(
    'SkillOrchestrator',
    target_dir='skills',
    similarity_threshold=0.6,
    auto_commit=True,
    dry_run=False
)

print(result)
# Output:
# {
#     "status": "success",
#     "skills_discovered": 12,
#     "clusters": 4,
#     "consolidated": 3
# }
```

### Skill Parameters

When calling the orchestrator skill, pass these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_dir` | str | "skills" | Directory containing SKILL.md files |
| `similarity_threshold` | float | 0.6 | Clustering threshold (0-1) |
| `auto_commit` | bool | True | Auto-commit changes to git |
| `dry_run` | bool | False | Simulate without making changes |

### Skill Metadata

The orchestrator skill is registered with the following metadata:

```json
{
    "name": "SkillOrchestrator",
    "description": "Automated skill orchestrator that discovers, clusters, consolidates, and publishes AI skills with semantic analysis",
    "version": "1.0.0",
    "author": "Clawstr Team",
    "tags": ["automation", "skill-management", "consolidation"]
}
```

### OpenClaw Architecture

```
┌─────────────────────────────────────────┐
│        Clawstr Agent                    │
└────────────────────────────────────────┬┘
                                         │
                    ┌────────────────────┴──────────────┐
                    │ Registered Skills                │
                    │ ├─ SkillOrchestrator (THIS!)     │
                    │ ├─ DataProcessor                 │
                    │ ├─ APIConnector                  │
                    │ └─ ...other skills               │
                    └─────────────────────────────────┘
```

When your Clawstr agent needs to optimize skills, it can call the SkillOrchestrator skill automatically.



The orchestrator includes robust error handling:

- **Syntax Errors in SKILL.md**: Logged and skipped
- **Git Failures**: Logged with rollback to previous state
- **NLP Processing**: Gracefully falls back to name-based clustering
- **File Write Failures**: Prevents deletion of originals

**All operations are logged to:**
- Console output (INFO level)
- `orchestrator_heartbeat.log` (if running heartbeat)

## API Reference

### SkillOrchestrator

#### `discover_skills(target_dir: Optional[str]) → List[Dict]`

Discover all SKILL.md files in target directory.

**Parameters:**
- `target_dir`: Directory to scan (default: config.skills_dir)

**Returns:**
- List of parsed skill dictionaries

**Example:**
```python
skills = orchestrator.discover_skills("skills")
```

#### `cluster_skills(threshold: Optional[float]) → Dict[str, List[Dict]]`

Cluster discovered skills by semantic similarity.

**Parameters:**
- `threshold`: Similarity threshold 0-1 (default: config.similarity_threshold)

**Returns:**
- Dictionary mapping cluster IDs to skill lists

**Example:**
```python
clusters = orchestrator.cluster_skills(threshold=0.7)
for cluster_id, skills in clusters.items():
    print(f"{cluster_id}: {len(skills)} skills")
```

#### `consolidate_cluster(cluster_id: str) → Optional[Dict]`

Consolidate a cluster into a single master skill.

**Parameters:**
- `cluster_id`: ID of the cluster to consolidate

**Returns:**
- Consolidated skill dictionary, or None if only 1 skill

**Example:**
```python
master_skill = orchestrator.consolidate_cluster("cluster_0")
```

#### `publish_consolidated_skill(skill: Dict, output_dir: Optional[str]) → Optional[Path]`

Write consolidated skill to a SKILL.md file.

**Parameters:**
- `skill`: Consolidated skill dictionary
- `output_dir`: Output directory (default: config.skills_dir)

**Returns:**
- Path to written file, or None on failure

**Example:**
```python
file_path = orchestrator.publish_consolidated_skill(master_skill)
```

#### `run_full_orchestration(...) → Dict[str, Any]`

Execute the complete workflow.

**Parameters:**
- `target_dir`: Directory containing skills
- `auto_commit`: Enable auto-commit (default: True)
- `auto_push`: Enable auto-push (default: False)

**Returns:**
```python
{
    "status": "success",
    "skills_discovered": 4,
    "clusters_created": 2,
    "skills_consolidated": 2,
    "skills_published": 2,
    "skills_archived": 4,
    "published_files": [...],
    "archived_files": [...]
}
```

### NLPHelper

#### `compute_similarity(text1: str, text2: str) → float`

Compute cosine similarity between two texts.

**Returns:** Similarity score 0-1

#### `cluster_skills(skills: List[Dict], threshold: float) → Dict`

Cluster skills by semantic similarity.

**Returns:** Dictionary of clusters

#### `find_duplicates(skills: List[Dict], threshold: float) → List[Tuple]`

Find potentially duplicate skills.

**Returns:** List of (skill1, skill2, similarity) tuples

### GitManager

#### `commit(message: str, author_name: Optional[str]) → Optional[str]`

Create a commit with staged changes.

**Returns:** Commit hash, or None if no changes

#### `push(remote: str, branch: Optional[str]) → None`

Push commits to remote repository.

## Logging

The orchestrator uses Python's standard logging module:

- **Console**: INFO level and above
- **File** (heartbeat): All levels, including DEBUG

### Log Format

```
2024-02-04 10:30:45,123 - orchestrator - INFO - Discovered skill: data_processing_skill (skills/data_processing_skill.md)
```

## Troubleshooting

### Issue: No skills discovered

**Solution:** Ensure SKILL.md files exist in the target directory and have proper YAML frontmatter.

### Issue: Skills not clustering

**Solution:** Increase `similarity_threshold` to a lower value (e.g., 0.5). Adjust descriptions to be more descriptive.

### Issue: Git commit fails

**Solution:** Ensure Git is configured with user name and email:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Issue: Missing dependencies

**Solution:** Reinstall requirements:
```bash
pip install --upgrade -r requirements.txt
```

## Performance

- **Discovery:** ~1 skill per 10ms (I/O bound)
- **Clustering:** ~50 skills per second (NLP bound, with caching)
- **Consolidation:** Instant (string operations)
- **Publishing:** ~1 skill per 5ms (I/O bound)

For 100 skills: ~2-3 seconds end-to-end

## Future Enhancements

- [ ] Web UI for orchestrator management
- [ ] Real-time webhook notifications
- [ ] Advanced merge conflict resolution
- [ ] Machine learning-based skill recommendation
- [ ] Integration with Clawstr Agent Platform
- [ ] Multi-repository support
- [ ] Custom merge strategies

## Contributing

Contributions welcome! Please:

1. Follow PEP 8 style guide
2. Add tests for new features
3. Update README with changes
4. Submit pull requests to `main`

## License

See LICENSE file for details.

## Support

For issues, feature requests, or questions:

- Open an issue on GitHub
- Check existing documentation
- Review code comments and docstrings

---

**Built with ❤️ for the Clawstr AI Agent Framework**
