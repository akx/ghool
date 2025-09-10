import dataclasses
from collections import Counter, defaultdict
from itertools import count
from typing import Iterable

import click
import httpx
import rich.progress
from rich import print
from rich.table import Table

from ghool.helpers import get_github_client


@dataclasses.dataclass(frozen=True)
class RepoInfo:
    data: dict

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def full_name(self) -> str:
        return self.data["full_name"]

    @property
    def license_name(self) -> str:
        license_info = self.data.get("license")
        if license_info:
            return license_info.get("name", "Unknown")
        return "No License"

    @property
    def description(self) -> str:
        return self.data.get("description", "") or ""

    @property
    def language(self) -> str:
        return self.data.get("language", "") or ""


def get_org_repos(cli: httpx.Client, org: str) -> Iterable[RepoInfo]:
    for page in rich.progress.track(count(1), description="Fetching repositories"):
        res = cli.get(
            f"/orgs/{org}/repos",
            params={
                "per_page": 100,
                "page": page,
            },
        )
        res.raise_for_status()
        repos = res.json()
        yield from (RepoInfo(data=repo) for repo in repos)
        if len(repos) < 100:
            break


@click.command(help="List an organization's repositories and summarize by license.")
@click.option("--org", "-o", required=True, help="GitHub organization name.")
@click.pass_context
def org_licenses(ctx, org: str) -> None:
    with get_github_client(ctx) as cli:
        repos = list(get_org_repos(cli, org))

    if not repos:
        print(f"[yellow]No repositories found for organization {org}.[/yellow]")
        return

    license_groups = defaultdict(list)
    for repo in repos:
        license_groups[repo.license_name].append(repo)

    license_counts = Counter(repo.license_name for repo in repos)

    print(f"[bold]Organization: {org}[/bold]")
    print(f"[bold]Total repositories: {len(repos)}[/bold]\n")

    # License summary table
    table = Table(title="License Summary")
    table.add_column("License", style="cyan")
    table.add_column("Count", justify="right", style="magenta")

    for license_name, n in license_counts.most_common():
        table.add_row(license_name, str(n))

    print(table)

    for license_name in sorted(license_groups.keys()):
        repos_with_license = sorted(license_groups[license_name], key=lambda r: r.name)
        print(f"\n[bold]{license_name} ({len(repos_with_license)} repositories):[/bold]")

        detail_table = Table()
        detail_table.add_column("Repository", style="green")
        detail_table.add_column("Language", style="blue")
        detail_table.add_column("Description", style="white")

        for repo in repos_with_license:
            detail_table.add_row(
                repo.full_name,
                repo.language,
                repo.description[:80] + "..." if len(repo.description) > 80 else repo.description,
            )

        print(detail_table)
