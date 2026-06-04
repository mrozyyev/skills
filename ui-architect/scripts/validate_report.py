"""
Validate a UI Architect report for completeness.

Checks that the report covers all required sections.
Usage: python validate_report.py <path-to-report.md>
"""

import sys
import re

REQUIRED_SECTIONS = [
    "Architecture Overview",
    "Provider / Context Tree",
    "Screen Layout",
    "Header",
    "Scrolling",
    "Keyboard Handling",
    "Input Bar",
    "Content Rendering",
    "Animations",
    "Edge Cases",
    "Data Model",
    "Dependencies",
    "Key Implementation Notes",
]

SECTION_ALIASES = {
    "Architecture": "Architecture Overview",
    "Component Tree": "Architecture Overview",
    "Provider": "Provider / Context Tree",
    "Context": "Provider / Context Tree",
    "Layout": "Screen Layout",
    "Composer": "Input Bar",
    "Message": "Content Rendering",
    "Bubble": "Content Rendering",
}


def check_report(filepath: str) -> dict:
    with open(filepath) as f:
        content = f.read()

    results = {}
    for section in REQUIRED_SECTIONS:
        # Check for ## Section Name or ### Section Name
        pattern = re.compile(
            r"^#+\s+" + re.escape(section), re.MULTILINE | re.IGNORECASE
        )
        found = bool(pattern.search(content))
        if not found:
            # Check aliases
            for alias_pattern, mapped in SECTION_ALIASES.items():
                if mapped == section:
                    alias_re = re.compile(
                        r"^#+\s+" + re.escape(alias_pattern), re.MULTILINE | re.IGNORECASE
                    )
                    if alias_re.search(content):
                        found = True
                        break
        results[section] = found

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_report.py <path-to-report.md>")
        sys.exit(1)

    filepath = sys.argv[1]
    results = check_report(filepath)

    missing = [s for s, f in results.items() if not f]
    present = [s for s, f in results.items() if f]

    total = len(results)
    passed = len(present)
    score = passed / total * 100

    print(f"Report: {filepath}")
    print(f"Score: {score:.0f}% ({passed}/{total} sections)")
    print()

    if missing:
        print("MISSING SECTIONS:")
        for s in missing:
            print(f"  - {s}")
        print()
    else:
        print("All required sections present!")

    if score < 100:
        print("TIP: Read references/methodology.md for guidance on each section.")
        sys.exit(1)


if __name__ == "__main__":
    main()
