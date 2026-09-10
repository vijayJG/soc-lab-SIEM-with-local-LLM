"""
socai.py - SOC AI Engine

Fetches Wazuh security alerts and sends them to a locally running
Ollama LLM for structured SOC analyst-style analysis.

Requirements:
    pip install requests

Usage:
    python3 socai.py

The Ollama server must be running on the Windows host and accessible
over LAN at the IP defined in OLLAMA_API below.
"""

import requests
import json

# IP of the Windows host running Ollama, exposed over LAN
OLLAMA_API = "http://192.168.0.10:11434/api/generate"


def analyze_alert(alert):
    """
    Send a Wazuh alert to the local LLM and return a structured analysis.

    Args:
        alert (dict): A Wazuh alert object containing agent and rule fields.

    Returns:
        str: The LLM's plain-text SOC analysis.
    """
    prompt = f"""
You are a SOC analyst AI.

Analyze the following security alert:

Agent: {alert['agent']['name']}
Alert: {alert['rule']['description']}

Return:
1. Severity
2. Attack explanation
3. MITRE ATT&CK mapping
4. Recommended actions
"""

    response = requests.post(
        OLLAMA_API,
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


if __name__ == "__main__":
    # Sample alert for testing - replace with live Wazuh alert data as needed
    sample_alert = {
        "agent": {"name": "DESKTOP-D30007T"},
        "rule": {
            "description": "Multiple failed login attempts detected"
        }
    }

    result = analyze_alert(sample_alert)
    print("\n--- SOC AI OUTPUT ---\n")
    print(result)
