#!/usr/bin/env python

from arcadepy import Arcade
import json

client = Arcade()  # Automatically finds the `ARCADE_API_KEY` env variable

USER_ID = "kig@kig.re"
TOOL_NAME = "Github.GetRepository"

auth_response = client.tools.authorize(
    tool_name=TOOL_NAME,
    user_id=USER_ID,
)

if auth_response.status != "completed":
    print(f"Click this link to authorize: {auth_response.url}")

# Wait for the authorization to complete
client.auth.wait_for_completion(auth_response)

tool_input = {"owner": "kigster", "repo": "githuh"}

response = client.tools.execute(
    tool_name=TOOL_NAME,
    input=tool_input,
    user_id=USER_ID,
)

print(json.dumps(response.output.value))
