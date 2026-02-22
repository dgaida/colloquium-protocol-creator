import os
import re
import sys


def increment_version():
    filepath = "pyproject.toml"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        sys.exit(1)

    with open(filepath) as f:
        lines = f.readlines()

    new_lines = []
    found = False
    for line in lines:
        if not found and line.strip().startswith('version = "'):
            match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', line)
            if match:
                major, minor, patch = map(int, match.groups())
                old_version = f"{major}.{minor}.{patch}"

                patch += 1
                if patch > 9:
                    patch = 0
                    minor += 1
                if minor > 9:
                    minor = 0
                    major += 1

                new_version = f"{major}.{minor}.{patch}"
                line = line.replace(f'version = "{old_version}"', f'version = "{new_version}"')
                found = True
                print(f"Incrementing version: {old_version} -> {new_version}")
        new_lines.append(line)

    if found:
        with open(filepath, "w") as f:
            f.writelines(new_lines)
    else:
        print("Error: Could not find version string in pyproject.toml")
        sys.exit(1)


if __name__ == "__main__":
    increment_version()
