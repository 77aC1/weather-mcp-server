import httpx
import os
from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool
async def get_weather(city: str) -> str:
    """查询城市实时天气"""
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            # 地理编码
            r = await c.get("https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "zh"})
            data = r.json()
            if "results" not in data or not data["results"]:
                return f"找不到城市：{city}"
            loc = data["results"][0]
            lat, lon, name = loc["latitude"], loc["longitude"], loc["name"]

            # 天气
            w = await c.get("https://api.open-meteo.com/v1/forecast",
                params={"latitude": lat, "longitude": lon,
                        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                        "timezone": "auto"})
            now = w.json()["current"]
            return f"📍{name}\n🌡️{now['temperature_2m']}°C\n💧湿度{now['relative_humidity_2m']}%\n🌬️风速{now['wind_speed_10m']}km/h"
    except Exception as e:
        return f"查询失败：{e}"

@mcp.tool
async def get_forecast(city: str) -> str:
    """查询城市7天预报"""
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get("https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "zh"})
            data = r.json()
            if "results" not in data or not data["results"]:
                return f"找不到城市：{city}"
            loc = data["results"][0]
            lat, lon, name = loc["latitude"], loc["longitude"], loc["name"]

            f = await c.get("https://api.open-meteo.com/v1/forecast",
                params={"latitude": lat, "longitude": lon,
                        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                        "timezone": "auto", "forecast_days": 7})
            d = f.json()["daily"]
            lines = [f"📅{name} 7天预报"]
            for i in range(len(d["time"])):
                lines.append(f"📆{d['time'][i]} 🌡️{d['temperature_2m_min'][i]}~{d['temperature_2m_max'][i]}°C")
            return "\n".join(lines)
    except Exception as e:
        return f"查询失败：{e}"

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
