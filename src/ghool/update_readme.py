import re
from pathlib import Path

from click.testing import CliRunner

MARKERS_RE = re.compile("<!-- usage -->(.*?)<!-- end usage -->", re.DOTALL)


def main():
    from .cli import main

    res = CliRunner().invoke(main, ["--help"])
    readme_path = Path(__file__).parent.parent.parent / "README.md"
    assert readme_path.is_file()
    readme = readme_path.read_text()
    readme = MARKERS_RE.sub(f"<!-- usage -->\n```bash\n{res.output}\n```\n<!-- end usage -->", readme)
    readme_path.write_text(readme)


if __name__ == "__main__":
    main()
