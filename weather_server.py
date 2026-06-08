import os
import json
import urllib.request
from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool
def get_weather(city: str) -> str:
    url = "https://api.open-meteo.com/v1/forecast?latitude=39.9&longitude=116.4&current=temperature_2m,wind_speed_10m&timezone=Asia/Shanghai"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
        w = data["current"]
        return f"北京 {w['temperature_2m']}°C 风速{w['wind_speed_10m']}km/h"

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
