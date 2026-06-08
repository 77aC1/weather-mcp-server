import httpx
import os
from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool
async def get_weather(city: str) -> str:
    """查询城市实时天气"""
    async with httpx.AsyncClient(timeout=15) as c:
        # 1. 用免费API获取城市坐标
        geo = await c.get("https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "zh"})
        geo_data = geo.json()
        if not geo_data.get("results"):
            return f"找不到城市：{city}"
        
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        name = geo_data["results"][0].get("name", city)
        
        # 2. 获取天气
        w = await c.get("https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "current_weather": "true",
                "timezone": "auto"
            })
        wd = w.json()["current_weather"]
        
        return f"📍{name}\n🌡️{wd['temperature']}°C\n🌬️风速{wd['windspeed']}km/h {wd['winddirection']}°\n☁️天气代码{wd['weathercode']}"

@mcp.tool
async def get_forecast(city: str) -> str:
    """查询城市7天预报"""
    async with httpx.AsyncClient(timeout=15) as c:
        geo = await c.get("https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "zh"})
        geo_data = geo.json()
        if not geo_data.get("results"):
            return f"找不到城市：{city}"
        
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        name = geo_data["results"][0].get("name", city)
        
        f = await c.get("https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                "timezone": "auto",
                "forecast_days": 7
            })
        fd = f.json()["daily"]
        
        lines = [f"📅{name} 7天预报"]
        for i in range(len(fd["time"])):
            lines.append(
                f"\n📆{fd['time'][i]} "
                f"🌡️{fd['temperature_2m_min'][i]}~{fd['temperature_2m_max'][i]}°C"
            )
        return "\n".join(lines)

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
