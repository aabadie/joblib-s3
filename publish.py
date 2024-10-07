#!/usr/bin/env python3
import os
import sys
import subprocess

def run_command(command):
    process = subprocess.run(command, shell=True, check=True)
    return process.returncode

def main():
    if len(sys.argv) != 2:
        print("Usage: python publish.py <version>")
        print("Example: python publish.py 0.2.0")
        sys.exit(1)

    version = sys.argv[1]
    if not version.startswith('v'):
        version = f'v{version}'

    commands = [
        f'git tag {version}',
        f'git push origin {version}',
        'rm -rf dist/ build/ *.egg-info',
        'python -m build',
        'python -m twine upload dist/*'
    ]

    for command in commands:
        print(f"Executing: {command}")
        try:
            run_command(command)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {command}")
            print(f"Error: {e}")
            sys.exit(1)

    print(f"Successfully published version {version}")

if __name__ == "__main__":
    main()
