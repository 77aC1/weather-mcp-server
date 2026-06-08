import httpx
import os
from fastmcp import FastMCP

mcp = FastMCP("Weather")

API_KEY = os.getenv("QWEATHER_KEY", "")

@mcp.tool
def hello(name: str) -> str:
    """测试工具"""
    return f"Hello {name}! 🎉"

@mcp.tool
async def get_weather(city: str) -> str:
    """查询城市实时天气"""
    if not API_KEY:
        return "请先设置 QWEATHER_KEY"
    async with httpx.AsyncClient() as c:
        r = await c.get("https://geoapi.qweather.com/v2/city/lookup",
            params={"location": city, "key": API_KEY})
        d = r.json()
        if d["code"] != "200":
            return f"找不到城市：{city}"
        cid = d["location"][0]["id"]
        r2 = await c.get("https://devapi.qweather.com/v7/weather/now",
            params={"location": cid, "key": API_KEY})
        w = r2.json()["now"]
        return f"📍{city}\n🌡️{w['temp']}°C 体感{w['feelsLike']}°C\n☁️{w['text']}\n💧湿度{w['humidity']}%\n🌬️{w['windDir']}{w['windSpeed']}km/h"

@mcp.tool
async def get_forecast(city: str) -> str:
    """查询城市3天预报"""
    if not API_KEY:
        return "请先设置 QWEATHER_KEY"
    async with httpx.AsyncClient() as c:
        r = await c.get("https://geoapi.qweather.com/v2/city/lookup",
            params={"location": city, "key": API_KEY})
        d = r.json()
        if d["code"] != "200":
            return f"找不到城市：{city}"
        cid = d["location"][0]["id"]
        r2 = await c.get("https://devapi.qweather.com/v7/weather/3d",
            params={"location": cid, "key": API_KEY})
        lines = [f"📅{city} 3天预报"]
        for day in r2.json()["daily"]:
            lines.append(f"\n📆{day['fxDate']} {day['tempMin']}~{day['tempMax']}°C {day['textDay']}")
        return "\n".join(lines)

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
