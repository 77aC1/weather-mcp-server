import httpx
import os
from fastmcp import FastMCP

mcp = FastMCP("Weather")

API_KEY = os.getenv("QWEATHER_KEY", "")

async def fetch_json(url, params):
    """安全获取 JSON，出错返回 None"""
    async with httpx.AsyncClient(timeout=10) as c:
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
    if not API_KEY:
        return "请先设置 API Key"
    
    data = await fetch_json("https://geoapi.qweather.com/v2/city/lookup",
        {"location": city, "key": API_KEY})
    if not data or data.get("code") != "200":
        return f"找不到城市：{city}"
    
    cid = data["location"][0]["id"]
    w = await fetch_json("https://devapi.qweather.com/v7/weather/now",
        {"location": cid, "key": API_KEY})
    if not w or w.get("code") != "200":
        return "获取天气失败"
    
    now = w["now"]
    return f"📍{city}\n🌡️{now['temp']}°C 体感{now['feelsLike']}°C\n☁️{now['text']}\n💧湿度{now['humidity']}%\n🌬️{now['windDir']}{now['windSpeed']}km/h"

@mcp.tool
async def get_forecast(city: str) -> str:
    """查询城市3天预报"""
    if not API_KEY:
        return "请先设置 API Key"
    
    data = await fetch_json("https://geoapi.qweather.com/v2/city/lookup",
        {"location": city, "key": API_KEY})
    if not data or data.get("code") != "200":
        return f"找不到城市：{city}"
    
    cid = data["location"][0]["id"]
    f = await fetch_json("https://devapi.qweather.com/v7/weather/3d",
        {"location": cid, "key": API_KEY})
    if not f or f.get("code") != "200":
        return "获取预报失败"
    
    lines = [f"📅{city} 3天预报"]
    for day in f["daily"]:
        lines.append(f"\n📆{day['fxDate']} {day['tempMin']}~{day['tempMax']}°C {day['textDay']}")
    return "\n".join(lines)

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
