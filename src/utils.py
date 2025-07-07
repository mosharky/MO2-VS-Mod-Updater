import re


def parse_version(version: str) -> tuple[int]:
    """Takes a version string and parses it into a tuple; useful for comparisons

    Args:
        version (str): _Version number as a string_

    Returns:
        tuple: _Version as a tuple, where each element is a number_
    """
    # Replace the first dash with a dot for uniform splitting
    parts = version.replace("-", ".", 1).split(".")
    key = []

    for part in parts:
        # Converting versioning strings to negative numbers for better comparison to release (0)
        match part:
            case str() if part.isdigit():
                key.append(int(part))
            case "pre":
                key.append(-2)
            case "rc":
                key.append(-1)
            case _:
                key.append(-3)

    # Prevents case where fourth digit is needed for comparison with string versions
    key.append(0)

    return tuple(key)


def normalize_version(version: str) -> str:
    """Removes a trailing '.0' from a version string."""
    return version[:-2]


def fix_json_string(json_string: str) -> str:
    """Fixes a JSON string by removing trailing commas."""
    # Remove trailing commas before } or ]
    json_str = re.sub(r",(\s*[}\]])", r"\1", json_string)
    return json_str
