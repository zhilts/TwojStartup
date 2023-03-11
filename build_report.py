# -*- coding: utf-8 -*-
import os
import re
import argparse
import contextlib

from collections import namedtuple
from functools import wraps
from odf.text import LineBreak, H, P, Span, S
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties

parser = argparse.ArgumentParser(description="Reduce video size")
parser.add_argument('-i', '--include', action='append', help="Add pattern to include", default=[])
parser.add_argument('-e', '--exclude', action='append', help="Add pattern to exclude", default=[])
args = parser.parse_args()


def compile_regexes(*patterns):
    return tuple([re.compile(pattern, re.IGNORECASE) for pattern in patterns])


EXCLUDE_PATTERNS = compile_regexes(r".*node_modules", r".*site-packages", r".*\.git", r".*\.idea", r".*\.log$")
INCLUDE_EXTENSIONS = ("java", "[tj]sx", "py", "md", "txt", "json", "ya?ml", "sh", "s?css", "conf", "html", "ini")
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


def include(filepath, include_patterns, exclude_patterns):
    return (not any_matches(exclude_patterns, filepath)) and any_matches(include_patterns, filepath)


@wrap_result(tuple)
def get_files(base_path, custom_include, custom_exclude):
    full_include = INCLUDE_PATTERNS + compile_regexes(*(fr"{pattern}" for pattern in custom_include))
    full_exclude = EXCLUDE_PATTERNS + compile_regexes(*(fr"{pattern}" for pattern in custom_exclude))
    for root, dirs, files in os.walk(base_path, followlinks=True):
        for filename in files:
            filepath = os.path.join(root, filename)
            if include(filepath, full_include, full_exclude):
                yield filepath


StyleSheets = namedtuple("StyleSheets", ["file_title", "code"])


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

    yield doc, StyleSheets(file_title, code)
    doc.save(filename)


def main():
    base_path = os.getcwd()
    files = sorted(get_files(base_path, args.include, args.exclude))
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
            doc.text.addElement(P())


if __name__ == "__main__":
    main()
