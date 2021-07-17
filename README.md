# detect-direct-checkins

## Overview

The `detect-direct-checkins` utility can be used to detect non-merge commits on given branches in a Git repository. It
can be run as a [pre-commit framework](https://pre-commit.com/) hook.

## Example Usage

### Command line tool

`detect-direct-checkins` is available on PyPI for Python 3.5+ and can be installed with `pip`:

```bash
python3 -m pip install detect-direct-checkins
```

If you use Arch Linux or one of its derivatives, you can also install `detect-direct-checkins` from the
[AUR](https://aur.archlinux.org/packages/python-detect-direct-checkins/):

```bash
yay -S python-detect-direct-checkins
```

You also find self-contained executables for 64-bit Linux distributions and macOS High Sierra and newer on the
[releases page](https://github.com/IngoMeyer441/detect-direct-checkins/releases/latest). They are created with
[PyInstaller](http://www.pyinstaller.org) and only require glibc >= 2.17 on Linux (should be fine on any recent
Linux system).

After the installation, switch your working directory to a Git repository you would like to check and run

```bash
detect-direct-checkins --branch release --allow-root
```

to check a branch ``release`` for non-merge commits (but ignore initial root commits without parents).

### Usage as a pre-commit hook

Add

```yaml
- repo: https://github.com/IngoMeyer441/detect-direct-checkins
  rev: 0.1.2
  hooks:
  - id: detect-direct-checkins
  - args: ['--branch=release', '--allow-root']
```

to your `.pre-commit-config.yaml` to detect direct checkins to a branch `release`. The `--allow-root` switch ignores
root commits (initial commits without parents).

The `--branch` argument can be given multiple times to check more than one branch.

This check is a `post-commit` check, so make sure to install the pre-commit framework as a `post-commit` hook:

```bash
pre-commit install --hook-type post-commit
```

I recommend to set `default_stages: ['commit']` in your `.pre-commit-config.yaml`. Otherwise, most checks will run
twice (in the `pre-commit` and `post-commit` stage).

**Important note**: Since this is a `post-commit` hook, this check **will not avoid the creation of disallowed
commits**. It only tells you that a disallowed commit has been created. However, you can run

```bash
pre-commit run --hook-type post-commit
```

as part of your CI pipeline to enforce this check. Direct-checkins to protected branches will cause this check to fail
in a CI job.

## Options

These options are supported:

- `--branch`: Branch which must only contain merge commits, can be given multiple times.
- `--ignore`: Commit hashes which will be ignored, can be given multiple times
- `--allow-root`: Allow root commits (commits without parents).

## Contributing

Please open [an issue on GitHub](https://github.com/IngoMeyer441/detect-direct-checkins/issues/new) if you
experience bugs or miss features. Please consider to send a pull request if you can spend time on fixing the issue
yourself. This project uses [pre-commit](https://pre-commit.com) itself to ensure code quality and a consistent code
style. Run

```bash
make git-hooks-install
```

to install all linters as Git hooks in your local clone of `detect-direct-checkins`.
