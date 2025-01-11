import dataclasses
import datetime
from itertools import count
from multiprocessing.pool import ThreadPool
from typing import Iterable

import click
import httpx
import rich.progress
from rich import print

from ghool.helpers import get_github_client


@dataclasses.dataclass(frozen=True)
class PRSearchInfo:
    data: dict

    @property
    def username(self) -> str:
        return self.data["user"]["login"]

    @property
    def pr_api_url(self) -> str:
        return self.data["pull_request"]["url"]

    @property
    def repository_qname(self) -> str:
        repo_api_url = self.data["repository_url"]
        return repo_api_url.partition("https://api.github.com/repos/")[-1]

    @property
    def title(self) -> str:
        return self.data["title"]

    @property
    def created_at(self) -> datetime.datetime:
        return datetime.datetime.fromisoformat(self.data["created_at"])

    def close(self, cli: httpx.Client) -> None:
        res = cli.patch(
            self.pr_api_url,
            json={"state": "closed"},
            headers={"Accept": "application/vnd.github+json"},
        )
        res.raise_for_status()


def search_pulls(cli, user: str) -> Iterable[PRSearchInfo]:
    for page in rich.progress.track(count(1), description="Searching PRs"):
        res = cli.get(
            "/search/issues",
            params={
                "q": f"is:pr is:open author:dependabot[bot] user:{user}",
                "per_page": 100,
                "page": page,
            },
        )
        res.raise_for_status()
        items = res.json()["items"]
        yield from (PRSearchInfo(data=item) for item in items)
        if len(items) < 100:
            break


@click.command(help="Close PRs created by Dependabot.")
@click.option("--user", "-u", required=True, help="GitHub username to scope the search to.")
@click.option("--really", is_flag=True, help="Actually close the PRs.")
@click.pass_context
def close_dependabot_prs(ctx, user: str, really: bool) -> None:
    with get_github_client(ctx) as cli:
        results = []
        for res in sorted(search_pulls(cli, user), key=lambda res: res.repository_qname):
            assert res.username == "dependabot[bot]"
            print(res.repository_qname, res.title, res.created_at)
            results.append(res)
        if really:
            with ThreadPool() as pool:
                for _ in rich.progress.track(
                    pool.imap_unordered(lambda res: res.close(cli), results),
                    total=len(results),
                    description="Closing PRs",
                ):
                    pass
        else:
            print("Use --really to close PRs.")
