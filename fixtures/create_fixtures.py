"""
Runs as a separate script.
Prepares raw data with fixtures and creates ready-to-use data in `.json`
format in the `./ready/` subdirectory.
"""

import re
import datetime as dt
from glob import glob
from pathlib import Path


def replace_date(text: str) -> str:
    """
    Searches all patterns of the form `{%TODAY-X%}` in the text and
    converts them to date form. The translation is based on today's date
    and the direction and size of the offset.

    Example (for the date 2007-06-15):
     "{%TODAY-5%}"   -> "2007-06-10" (- 5 days)
     "{%TODAY+5%}"   -> "2007-06-20" (+ 5 days)
     "{%TODAY-0%}"   -> "2007-06-15" (today, it only works like this)
     "{%TODAY+365%}" -> "2008-06-14"
    """

    today_pattern = re.compile(r"{%TODAY[+-]\d+%}")
    templates = set(today_pattern.findall(text))
    today = dt.date.today()

    for template in templates:
        offset = template[7:-2]
        delta = dt.timedelta(days=int(offset))
        text = text.replace(template, str(today + delta))

    return text


def main():
    """
    One by one it reads all files from the `./raw/` subdirectory,
    prepares them to a ready form and writes them to the `./ready/`
    subdirectory.
    """

    root_dir = Path(__file__).parent.resolve()
    raw_dir = root_dir / "raw"
    ready_dir = root_dir / "ready"

    files = glob("*.json", root_dir=raw_dir)

    for file_name in files:
        with open(raw_dir / file_name, "r") as raw_file:
            text = raw_file.read()

        text = replace_date(text)

        with open(ready_dir / file_name, "w") as data_file:
            data_file.write(text)


if __name__ == "__main__":
    main()
