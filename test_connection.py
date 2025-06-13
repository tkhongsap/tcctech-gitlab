#!/usr/bin/env python3
"""Test GitLab connection without all dependencies."""

import os
import requests

# Read environment variables directly
gitlab_url = os.environ.get('GITLAB_URL')
gitlab_token = os.environ.get('GITLAB_API_TOKEN')

# If not in env, read from .env file
if not gitlab_url or not gitlab_token:
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key == 'GITLAB_URL' and not gitlab_url:
                        gitlab_url = value
                    elif key == 'GITLAB_API_TOKEN' and not gitlab_token:
                        gitlab_token = value

print(f"GitLab URL: {gitlab_url}")
print(f"Token: {gitlab_token[:10]}..." if gitlab_token else "No token")

# Test connection
headers = {'PRIVATE-TOKEN': gitlab_token}
try:
    response = requests.get(f"{gitlab_url.rstrip('/')}/api/v4/projects", headers=headers, params={'per_page': 1})
    if response.status_code == 200:
        print("\n✓ Connection successful!")
        print(f"Found {len(response.json())} project(s)")
    else:
        print(f"\n✗ Connection failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n✗ Error: {e}")