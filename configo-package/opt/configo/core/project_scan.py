import os

def scan_project():
    # Example: look for requirements.txt, package.json, etc.
    files = os.listdir('.')
    if 'requirements.txt' in files:
        return "Python"
    if 'package.json' in files:
        return "Node.js"
    return None 