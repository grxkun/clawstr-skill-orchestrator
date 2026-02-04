from flask import Flask, request, jsonify
import os
from orchestrator import SkillOrchestrator
from nostr_client import NostrClient
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for Vercel."""
    return jsonify({"status": "healthy", "service": "clawstr-orchestrator"})

@app.route('/orchestrate', methods=['POST'])
def trigger_orchestration():
    """Trigger a single orchestration run."""
    try:
        # Get configuration from environment
        repo_path = os.getcwd()

        # Initialize orchestrator
        orchestrator = SkillOrchestrator(repo_path)

        # Run discovery phase only (no git operations on Vercel)
        skills = orchestrator.discover_skills()

        # Return results
        return jsonify({
            "status": "success",
            "skills_discovered": len(skills),
            "skills": [{"name": s["name"], "version": s["version"]} for s in skills[:5]]
        })

    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/metadata')
def get_metadata():
    """Get agent metadata for Nostr broadcasting."""
    try:
        client = NostrClient()
        metadata = client.get_metadata()
        return jsonify(metadata)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel expects this for serverless functions
if __name__ == '__main__':
    app.run(debug=True)