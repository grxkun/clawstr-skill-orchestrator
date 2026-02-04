#!/usr/bin/env python3
"""
Health Check Server for Railway

Provides HTTP health check endpoint for Railway deployment monitoring.
"""

import os
import sys
import json
import logging
from flask import Flask, jsonify
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health')
def health_check():
    """Railway health check endpoint."""
    try:
        # Check if we're in a git repository
        if not Path('.git').exists():
            return jsonify({
                "status": "unhealthy",
                "error": "Not a git repository"
            }), 500

        # Check if required environment variables are set
        required_env = ['NOSTR_NSEC', 'AGENT_NAME']
        missing_env = [env for env in required_env if not os.getenv(env)]

        if missing_env:
            return jsonify({
                "status": "unhealthy",
                "error": f"Missing environment variables: {missing_env}"
            }), 500

        # Check if skills directory exists
        if not Path('skills').exists():
            return jsonify({
                "status": "warning",
                "message": "Skills directory not found"
            }), 200

        # Count skills
        skill_files = list(Path('skills').glob('*.md'))
        skill_count = len(skill_files)

        return jsonify({
            "status": "healthy",
            "skills_count": skill_count,
            "git_repo": True,
            "environment": "configured"
        })

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/')
def root():
    """Root endpoint with basic info."""
    return jsonify({
        "service": "Clawstr Skill Orchestrator",
        "version": "1.0.0",
        "status": "running"
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)