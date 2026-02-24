import re


def get_languages_from_header(header_text: str) -> list[tuple[str, float]]:
    language_matches = re.finditer(
        r"(?P<lang>\w{2,3}(-\w+)?)(;q\=(?P<weight>\d+\.?\d+))?",
        header_text,
        re.IGNORECASE,
    )

    languages = []
    for match in language_matches:
        weight = match.group("weight") or 1
        languages.append((match.group("lang"), float(weight)))

    return sorted(languages, key=lambda x: x[1], reverse=True)
