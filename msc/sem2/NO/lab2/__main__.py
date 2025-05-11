import re
import sys
from pathlib import Path


def strip_comments(code: str) -> str:
    """Remove // line comments and /* block comments */."""
    code = re.sub(r"//.*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return code


def count_switch_branches(code: str) -> int:
    """Return Σ (cases_in_switch − 1) over all switch statements."""
    switch_pat = re.compile(r"switch\s*\([^)]*\)\s*\{")
    case_pat = re.compile(r"\bcase\b")
    pos = 0
    total = 0

    while True:
        m = switch_pat.search(code, pos)
        if not m:
            break
        i = m.end()
        depth = 1
        while depth and i < len(code):
            if code[i] == "{":
                depth += 1
            elif code[i] == "}":
                depth -= 1
            i += 1
        switch_body = code[m.end() : i - 1]
        cases = len(case_pat.findall(switch_body))
        total += max(0, cases - 1)
        pos = i
    return total


def count_decisions(code: str) -> int:
    """Return d – the number of decision points."""
    code = strip_comments(code)
    code = re.sub(r'"(\\.|[^"\\])*"', "", code)

    d = count_switch_branches(code)  # switch branches
    d += len(re.findall(r"\bif\b", code))  # if
    d += len(re.findall(r"\bfor\b", code))  # for
    d += len(re.findall(r"\bwhile\b", code))  # while
    d += len(re.findall(r"&&|\|\|", code))  # short-circuit
    d += len(re.findall(r"\?", code))  # ternary
    return d


def cyclomatic_number(path: str) -> int:
    code = Path(path).read_text(encoding="utf-8", errors="ignore")
    d = count_decisions(code)
    return d + 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cyclomatic.py <file.c>")
        sys.exit(1)
    v = cyclomatic_number(sys.argv[1])
    print(f"Cyclomatic complexity v(G) = {v}")
