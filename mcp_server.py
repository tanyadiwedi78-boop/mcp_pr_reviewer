import os 
import requests
from mcp.server.fastmcp import FastMCP
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_ID")



# Initialize MCP Server
mcp = FastMCP("Complete_PR_Reviewer_MCP")


# ==============================================================================
# 1. RESOURCE (Internal Documentation / Standards)
# ==============================================================================
@mcp.resource("guidelines://python-standards")
def get_coding_standards() -> str:
    """Returns team coding guidelines for AI code review."""
    return """
    TEAM CODING STANDARDS:
    1. Functions must have explicit docstrings and type annotations.
    2. Never hardcode API keys or sensitive credentials.
    3. Use descriptive variable naming conventions (e.g., 'user_count').
    4. Handle API and IO exceptions gracefully.
    """


# ==============================================================================
# 2. PROMPT (Clickable Automation Workflow)
# ==============================================================================
@mcp.prompt()
def review_pr_workflow(owner: str, repo: str, pr_number: int) -> str:
    """End-to-end automated pull request audit workflow."""
    return f"""
    Execute full PR review process:
    1. Read internal guidelines from 'guidelines://python-standards'.
    2. Fetch code changes for '{owner}/{repo}', PR #{pull_number} using 'get_github_pr_diff'.
    3. Audit code diff for security issues and guideline compliance.
    4. Generate a clean structured summary.
    5. Save review directly to Notion using 'save_to_notion'.
    """


# ==============================================================================
# 3. TOOLS (API Read / Write Operations)
# ==============================================================================
@mcp.tool()
def get_github_pr_diff(owner: str, repo: str, pull_number: int) -> str:
    """Fetches raw diff content of a specific GitHub PR."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return f"GitHub API Error ({response.status_code}): {response.text}"
    except Exception as err:
        return f"Connection Failed: {str(err)}"


@mcp.tool()
def save_to_notion(review_summary: str) -> str:
    """Appends summary text as a block to the target Notion page."""
    notion = Client(auth=NOTION_TOKEN)
    try:
        notion.blocks.children.append(
            block_id=NOTION_PAGE_ID,
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": review_summary}}]
                }
            }]
        )
        return "Success: Summary appended to Notion page."
    except Exception as err:
        return f"Notion API Error: {str(err)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')

