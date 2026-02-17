from mcp.server.fastmcp import FastMCP
import asyncio

mcp = FastMCP("Test")
print(f"Is callable: {callable(mcp)}")
try:
    # Check if it has asgi related attributes
    print(f"Has app: {hasattr(mcp, 'app')}")
except:
    pass
