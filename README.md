# ghool (github tool)

A collection of tools to interact with GitHub in ways that are cumbersome via the UI.

## Installation

* If you have `uv` installed, you should be able to `uv run -m ghool` from the root of the repository.
* Otherwise, you can `pip install -e .` and `ghool`.

## Usage

<!-- usage -->
```bash
Usage: main [OPTIONS] COMMAND [ARGS]...

Options:
  --token TOKEN  GitHub token (e.g. personal access token). Also read from
                 GITHUB_TOKEN.  [required]
  --help         Show this message and exit.

Commands:
  close-dependabot-prs  Close PRs created by Dependabot.

```
<!-- end usage -->
