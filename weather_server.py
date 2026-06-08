import httpx
import os
from fastmcp import FastMCP

mcp = FastMCP("Weather")

async def fetch(url, params):
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(url, params=params)
        if r.status_code != 200:
            return None
        try:
            return r.json()
        except:
            return None

@mcp.tool
async def get_weather(city: str) -> str:
    """查询城市实时天气"""
    # 1. 地理编码
    geo = await fetch("https://geocoding-api.open-meteo.com/v1/search",
        {"name": city, "count": 1, "language": "zh"})
    if not geo or "results" not in geo or not geo["results"]:
        return f"找不到城市：{city}"
    
    loc = geo["results"][0]
    lat, lon, name = loc["latitude"], loc["longitude"], loc.get("name", city)
    
    # 2. 天气
    w = await fetch("https://api.open-meteo.com/v1/forecast",
        {"latitude": lat, "longitude": lon,
         "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
         "timezone": "auto"})
    
    if not w or "current" not in w:
        return f"获取 {name} 天气失败，请重试"
    
    c = w["current"]
    wcode = {0:"晴",1:"大部晴",2:"多云",3:"阴",45:"雾",51:"小雨",61:"中雨",63:"大雨",71:"小雪",73:"大雪",95:"雷暴"}
    weather_text = wcode.get(c.get("weather_code", 0), "未知")
    
    return f"📍{name}\n🌡️{c['temperature_2m']}°C\n☁️{weather_text}\n💧湿度{c['relative_humidity_2m']}%\n🌬️风速{c['wind_speed_10m']}km/h"

@mcp.tool
async def get_forecast(city: str) -> str:
    """查询城市7天预报"""
    geo = await fetch("https://geocoding-api.open-meteo.com/v1/search",
        {"name": city, "count": 1, "language": "zh"})
    if not geo or "results" not in geo or not geo["results"]:
        return f"找不到城市：{city}"
    
    loc = geo["results"][0]
    lat, lon, name = loc["latitude"], loc["longitude"], loc.get("name", city)
    
    f = await fetch("https://api.open-meteo.com/v1/forecast",
        {"latitude": lat, "longitude": lon,
         "daily": "temperature_2m_max,temperature_2m_min,weather_code",
         "timezone": "auto", "forecast_days": 7})
    
    if not f or "daily" not in f:
        return f"获取 {name} 预报失败"
    
    d = f["daily"]
    wcode = {0:"晴",1:"大部晴",2:"多云",3:"阴",45:"雾",51:"小雨",61:"中雨",63:"大雨",71:"小雪",73:"大雪",95:"雷暴"}
    
    lines = [f"📅{name} 7天预报"]
    for i in range(len(d["time"])):
        wc = d["weather_code"][i] if "weather_code" in d else 0
        lines.append(f"\n📆{d['time'][i]} 🌡️{d['temperature_2m_min'][i]}~{d['temperature_2m_max'][i]}°C ☁️{wcode.get(wc,'未知')}")
    return "\n".join(lines)

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
