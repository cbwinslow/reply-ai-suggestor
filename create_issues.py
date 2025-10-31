#!/usr/bin/env python3
"""
Script to parse tasks.md and create issues on GitHub and GitLab
"""

import re
import requests
import json
from typing import List, Dict, Tuple

# Configuration
GITHUB_TOKEN = "<REPLACE_WITH_YOUR_GITHUB_TOKEN>"
GITHUB_REPO = "cbwinslow/reply-ai-suggestor"
GITLAB_TOKEN = "<REPLACE_WITH_YOUR_GITLAB_TOKEN>"
GITLAB_PROJECT = "cbwinslow/reply-ai-suggestor"
GITLAB_URL = "https://gitlab.com"

# API URLs
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
GITLAB_API_URL = f"{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECT.replace('/', '%2F')}/issues"


def parse_tasks_md(file_path: str) -> List[Dict]:
    """Parse tasks.md and extract all tasks with their metadata."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    tasks = []
    current_section = ""
    current_label = ""
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Detect section headers (## 1. Backend, ## 2. Android, etc.)
        section_match = re.match(r'^##\s+\d+\.\s+(.+)$', line)
        if section_match:
            current_section = section_match.group(1)
            # Map section to label
            label_map = {
                "Backend": "backend",
                "Android (IME + App)": "android",
                "Docs & Policy": "documentation",
                "QA, CI & Security": "ci/qa",
                "Housekeeping (repo hygiene)": "housekeeping"
            }
            current_label = label_map.get(current_section, "general")
            i += 1
            continue
        
        # Detect main task items (- [ ] Task description)
        task_match = re.match(r'^-\s+\[\s*\]\s+(.+)$', line)
        if task_match and not line.startswith('  '):  # Top-level task
            title = task_match.group(1).strip()
            body_lines = []
            acceptance_criteria = []
            microgoals = []
            
            # Look ahead for details
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                
                # Stop if we hit another top-level task or section
                if re.match(r'^-\s+\[\s*\]\s+', next_line) and not next_line.startswith('  '):
                    break
                if re.match(r'^##\s+', next_line):
                    break
                if next_line.strip() == '---':
                    break
                
                # Collect acceptance criteria
                if 'Acceptance criteria:' in next_line or 'acceptance criteria:' in next_line:
                    criteria_text = next_line.split(':', 1)[1].strip() if ':' in next_line else ''
                    if criteria_text:
                        acceptance_criteria.append(criteria_text)
                    j += 1
                    continue
                
                # Collect microgoals (indented tasks)
                microgoal_match = re.match(r'^\s+-\s+\[\s*\]\s+(.+)$', next_line)
                if microgoal_match:
                    microgoals.append(microgoal_match.group(1).strip())
                    j += 1
                    continue
                
                # Collect other body content
                if next_line.strip() and not next_line.strip().startswith('- Microgoals:'):
                    body_lines.append(next_line.strip())
                
                j += 1
            
            # Build issue body
            body_parts = []
            
            if microgoals:
                body_parts.append("## Microgoals")
                for mg in microgoals:
                    body_parts.append(f"- [ ] {mg}")
                body_parts.append("")
            
            if acceptance_criteria:
                body_parts.append("## Acceptance Criteria")
                for ac in acceptance_criteria:
                    body_parts.append(f"- {ac}")
                body_parts.append("")
            
            if body_lines:
                body_parts.extend(body_lines)
            
            body = '\n'.join(body_parts).strip()
            
            tasks.append({
                'title': title,
                'body': body if body else 'No additional details provided.',
                'labels': [current_label],
                'section': current_section
            })
            
            i = j
            continue
        
        i += 1
    
    return tasks


def create_github_issue(task: Dict) -> bool:
    """Create an issue on GitHub."""
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'title': task['title'],
        'body': task['body'],
        'labels': task['labels']
    }
    
    try:
        response = requests.post(GITHUB_API_URL, headers=headers, json=data)
        if response.status_code == 201:
            issue_number = response.json()['number']
            print(f"✓ GitHub Issue #{issue_number} created: {task['title']}")
            return True
        else:
            print(f"✗ Failed to create GitHub issue: {task['title']}")
            print(f"  Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error creating GitHub issue: {task['title']}")
        print(f"  Error: {str(e)}")
        return False


def create_gitlab_issue(task: Dict) -> bool:
    """Create an issue on GitLab."""
    headers = {
        'PRIVATE-TOKEN': GITLAB_TOKEN,
        'Content-Type': 'application/json'
    }
    
    data = {
        'title': task['title'],
        'description': task['body'],
        'labels': ','.join(task['labels'])
    }
    
    try:
        response = requests.post(GITLAB_API_URL, headers=headers, json=data)
        if response.status_code == 201:
            issue_iid = response.json()['iid']
            print(f"✓ GitLab Issue #{issue_iid} created: {task['title']}")
            return True
        else:
            print(f"✗ Failed to create GitLab issue: {task['title']}")
            print(f"  Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error creating GitLab issue: {task['title']}")
        print(f"  Error: {str(e)}")
        return False


def main():
    """Main execution function."""
    print("=" * 80)
    print("Creating Issues from tasks.md")
    print("=" * 80)
    print()
    
    # Parse tasks
    print("Parsing tasks.md...")
    tasks = parse_tasks_md('tasks.md')
    print(f"Found {len(tasks)} tasks to create\n")
    
    # Create GitHub issues
    print("-" * 80)
    print("Creating GitHub Issues...")
    print("-" * 80)
    github_success = 0
    for task in tasks:
        if create_github_issue(task):
            github_success += 1
    
    print()
    print("-" * 80)
    print("Creating GitLab Issues...")
    print("-" * 80)
    gitlab_success = 0
    for task in tasks:
        if create_gitlab_issue(task):
            gitlab_success += 1
    
    # Summary
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Total tasks: {len(tasks)}")
    print(f"GitHub issues created: {github_success}/{len(tasks)}")
    print(f"GitLab issues created: {gitlab_success}/{len(tasks)}")
    print()


if __name__ == '__main__':
    main()