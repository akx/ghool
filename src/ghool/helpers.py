import httpx


def get_github_client(ctx):
    return httpx.Client(
        base_url="https://api.github.com",
        headers={
            "Authorization": f"Bearer {ctx.obj['token']}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
