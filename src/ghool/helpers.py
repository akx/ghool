import httpx


def get_github_client(ctx):
    headers = {"X-GitHub-Api-Version": "2022-11-28"}
    if ctx.obj.get("token"):
        headers["Authorization"] = f"Bearer {ctx.obj['token']}"

    return httpx.Client(
        base_url="https://api.github.com",
        headers=headers,
    )
