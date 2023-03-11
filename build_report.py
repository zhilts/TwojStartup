#!/usr/bin/env ./venv/bin/python
# -*- coding: utf-8 -*-
import os
import re
from collections import namedtuple
from functools import wraps

from odf.text import LineBreak, H, P, Span, S
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties
import contextlib


def compile_regexes(*patterns):
    return tuple([re.compile(pattern, re.IGNORECASE) for pattern in patterns])


EXCLUDE_PATTERNS = compile_regexes(r".*node_modules", r".*site-packages", r".*\.git", r".*\.idea")
INCLUDE_EXTENSIONS = ("java", "[tj]sx", "py", "md", "txt", "json", "ya?ml", "sh")
INCLUDE_PATTERNS = compile_regexes(
    *(rf".*\.{ext}" for ext in INCLUDE_EXTENSIONS),
    r".*\.gitignore",
    ".*dockerfile"
)


def wrap_result(wrapper_fn):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            result = fn(*args, **kwargs)
            return wrapper_fn(result)

        return decorator

    return wrapper


def any_matches(regexes, filename):
    return any((regex.match(filename) for regex in regexes))


def include(filepath):
    return not any_matches(EXCLUDE_PATTERNS, filepath) and any_matches(INCLUDE_PATTERNS, filepath)


@wrap_result(tuple)
def get_files(base_path):
    for root, dirs, files in os.walk(base_path, followlinks=True):
        for filename in files:
            filepath = os.path.join(root, filename)
            if include(filepath):
                yield filepath


Styles = namedtuple("Styles", ["file_title", "code"])


@contextlib.contextmanager
def odt_doc(filename):
    doc = OpenDocumentText()

    file_title = Style(name="Heading 1", family="paragraph")
    file_title.addElement(
        TextProperties(attributes={'fontsize': "14pt", 'fontweight': "bold", 'fontfamily': "Courier New"}))
    doc.styles.addElement(file_title)

    code = Style(name="Code", family="paragraph")
    code.addElement(TextProperties(attributes={'fontsize': "12pt", 'fontfamily': "Courier New"}))
    doc.styles.addElement(code)

    yield doc, Styles(file_title, code)
    doc.save(filename)


def main():
    base_path = os.getcwd()
    files = sorted(get_files(base_path))
    count = len(files)
    print(f"{count} files found")
    with odt_doc(f"Report_{os.path.split(base_path)[-1]}.odt") as (doc, styles):
        for file in files:
            path_formatted = file.replace(base_path, ".")
            print(path_formatted)
            h = H(outlinelevel=1, stylename=styles.file_title, text=path_formatted)
            doc.text.addElement(h)
            with open(file, "r") as inp:
                body = inp.read()

                p = P(stylename=styles.code)
                for line in body.split("\n"):
                    for i, chunk in enumerate(line.split(" ")):
                        if i > 0:
                            p.addElement(S())
                        p.addElement(Span(text=chunk))
                    p.addElement(LineBreak())
                doc.text.addElement(p)


if __name__ == "__main__":
    main()
