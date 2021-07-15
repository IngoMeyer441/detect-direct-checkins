#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from typing import Iterable

__author__ = "Ingo Meyer"
__email__ = "i.meyer@fz-juelich.de"
__copyright__ = "Copyright © 2021 Forschungszentrum Jülich GmbH. All rights reserved."
__license__ = "MIT"
__version_info__ = (0, 1, 1)
__version__ = ".".join(map(str, __version_info__))


class FoundNoSymbolicNameError(Exception):
    pass


def get_argumentparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
%(prog)s is a pre-commit framework hook to allow only merge commits on specific branches.
""",
    )
    parser.add_argument(
        "-b",
        "--branch",
        action="append",
        dest="branch",
        help="branch which must only contain merge commits, can be given multiple times",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        action="append",
        dest="ignore",
        help="commit hashes which will be ignored, can be given multiple times",
    )
    parser.add_argument(
        "-r",
        "--allow-root",
        action="store_true",
        dest="allow_root",
        help="allow root commits (commits without parents)",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        dest="print_version",
        help="print the version number and exit",
    )
    return parser


def parse_arguments() -> argparse.Namespace:
    parser = get_argumentparser()
    args = parser.parse_args()
    return args


def check_arguments(args: argparse.Namespace) -> None:
    if not args.branch:
        print("Please pass at least one branch to check.", file=sys.stderr)
        sys.exit(1)


def get_symbolic_name(commit_hash: str) -> str:
    try:
        symbolic_name = subprocess.check_output(
            ["git", "name-rev", "--name-only", "--no-undefined", commit_hash],
            universal_newlines=True,
        ).strip()
    except subprocess.CalledProcessError as e:
        raise FoundNoSymbolicNameError(
            'Could not find a symbolic name for the commit hash "{}".'.format(commit_hash)
        ) from e
    return symbolic_name


def has_only_merge_commits(
    branches: Iterable[str], ignored_commit_hashes: Iterable[str], allow_root_commit: bool
) -> bool:
    found_direct_commits = False
    for branch in branches:
        try:
            subprocess.check_call(
                ["git", "rev-parse", "--quiet", "--verify", branch],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            print('WARNING: Branch "{}" does not exist and is ignored.'.format(branch), file=sys.stderr)
            continue
        rev_list_output = subprocess.check_output(
            [
                "git",
                "rev-list",
                "--first-parent",
                "--min-parents={:d}".format(1 if allow_root_commit else 0),
                "--max-parents=1",
                branch,
            ],
            universal_newlines=True,
        ).strip()
        direct_commits = (
            [commit_hash for commit_hash in rev_list_output.split("\n") if commit_hash not in ignored_commit_hashes]
            if rev_list_output
            else []
        )
        if direct_commits:
            found_direct_commits = True
            print('Branch "{}" has direct checkins:'.format(branch), file=sys.stderr)
            for commit in direct_commits:
                try:
                    symbolic_name = get_symbolic_name(commit)
                    print("\t{hash}\t{name}".format(hash=commit, name=symbolic_name), file=sys.stderr)
                except FoundNoSymbolicNameError:
                    print("\t{hash}".format(hash=commit), file=sys.stderr)
    return not found_direct_commits


def main() -> None:
    args = parse_arguments()
    if args.print_version:
        print("{}, version {}".format(os.path.basename(sys.argv[0]), __version__))
        sys.exit(0)
    check_arguments(args)
    if not has_only_merge_commits(args.branch, args.ignore if args.ignore is not None else [], args.allow_root):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
