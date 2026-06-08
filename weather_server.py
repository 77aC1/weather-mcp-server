import os
from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool
def hello(name: str) -> str:
    """打个招呼测试是否正常"""
    return f"Hello {name}! MCP Server 跑起来了 🎉"

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
