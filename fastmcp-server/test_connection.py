import os
import sys

# Set OpenC3 environment variables explicitly
os.environ["OPENC3_API_HOSTNAME"] = "training20.openc3.com"
os.environ["OPENC3_API_PORT"] = "443"
os.environ["OPENC3_API_SCHEMA"] = "https"
os.environ["OPENC3_SCRIPT_API_HOSTNAME"] = "training20.openc3.com"
os.environ["OPENC3_SCRIPT_API_PORT"] = "443"
os.environ["OPENC3_SCRIPT_API_SCHEMA"] = "https"
os.environ["OPENC3_API_USER"] = "admin"
os.environ["OPENC3_API_PASSWORD"] = "admin"

print("Environment variables set:")
for key in ["OPENC3_API_HOSTNAME", "OPENC3_API_PORT", "OPENC3_API_SCHEMA", 
            "OPENC3_SCRIPT_API_HOSTNAME", "OPENC3_SCRIPT_API_PORT", "OPENC3_SCRIPT_API_SCHEMA"]:
    print(f"  {key}: {os.environ.get(key)}")

from openc3 import script
from openc3.script.script import get_cmd_tlm_api_client

print("\nChecking API client configuration...")
try:
    client = get_cmd_tlm_api_client()
    print(f"Client URL: {client.url}")
    print(f"Client headers: {client.headers}")
except Exception as e:
    print(f"Error getting client: {e}")

print("\nAttempting to send a command...")
try:
    result = script.cmd("INST", "ABORT", {})
    print(f"Command sent successfully: {result}")
except Exception as e:
    print(f"Error sending command: {e}")
    import traceback
    traceback.print_exc()