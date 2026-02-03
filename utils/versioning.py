# utils/versioning.py
import os
import re

def get_next_version(topic: str, ext: str, output_dir: str = "outputs"):
    """
    Returns next versioned filename for a topic.
    Example: linear_regression_v1.pptx
    """
    os.makedirs(output_dir, exist_ok=True)

    safe_topic = re.sub(r"[^a-zA-Z0-9_]", "_", topic.lower())
    pattern = re.compile(rf"{safe_topic}_v(\d+)\.{ext}")

    versions = []

    for f in os.listdir(output_dir):
        match = pattern.match(f)
        if match:
            versions.append(int(match.group(1)))

    next_version = max(versions) + 1 if versions else 1

    filename = f"{safe_topic}_v{next_version}.{ext}"
    return os.path.join(output_dir, filename)
