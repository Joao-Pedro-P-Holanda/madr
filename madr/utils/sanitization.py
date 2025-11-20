import re


def sanitize_name(name: str):
    without_extra_whitespace = re.sub(r"\s+", " ", name.strip())
    without_numbers = re.sub(r"[0-9]", "", without_extra_whitespace)
    alpha_lowercase_only = re.sub(r"[^\w ]", "", without_numbers.lower())
    return alpha_lowercase_only
