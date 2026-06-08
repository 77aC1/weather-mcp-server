import httpx
from fastmcp import FastMCP
import os

mcp = FastMCP("Weather Server", host="0.0.0.0", port=8000)

# 从环境变量读取 API Key（Railway 里设置）
API_KEY = os.getenv("QWEATHER_KEY", "")

@mcp.tool()
async def get_weather(city: str) -> str:
    """查询指定城市的实时天气"""
    if not API_KEY:
        return "请先设置和风天气 API Key"
    
    async with httpx.AsyncClient() as client:
        geo = await client.get(
            "https://geoapi.qweather.com/v2/city/lookup",
            params={"location": city, "key": API_KEY}
        )
        data = geo.json()
        if data["code"] != "200":
            return f"未找到城市：{city}"
        
        city_id = data["location"][0]["id"]
        
        weather = await client.get(
            "https://devapi.qweather.com/v7/weather/now",
            params={"location": city_id, "key": API_KEY}
        )
        w = weather.json()
        if w["code"] != "200":
            return "获取天气失败"
        
        now = w["now"]
        return (
            f"📍 {city} 实时天气\n"
            f"🌡️ 温度：{now['temp']}°C（体感 {now['feelsLike']}°C）\n"
            f"☁️ 天气：{now['text']}\n"
            f"💧 湿度：{now['humidity']}%\n"
            f"🌬️ 风：{now['windDir']} {now['windSpeed']}km/h"
        )

@mcp.tool()
async def get_forecast(city: str) -> str:
    """查询指定城市未来3天天气预报"""
    if not API_KEY:
        return "请先设置和风天气 API Key"
    
    async with httpx.AsyncClient() as client:
        geo = await client.get(
            "https://geoapi.qweather.com/v2/city/lookup",
            params={"location": city, "key": API_KEY}
        )
        data = geo.json()
        if data["code"] != "200":
            return f"未找到城市：{city}"
        
        city_id = data["location"][0]["id"]
        
        fc = await client.get(
            "https://devapi.qweather.com/v7/weather/3d",
            params={"location": city_id, "key": API_KEY}
        )
        f = fc.json()
        if f["code"] != "200":
            return "获取预报失败"
        
        result = [f"📅 {city} 未来3天预报"]
        for day in f["daily"]:
            result.append(
                f"\n📆 {day['fxDate']}"
                f"\n  🌡️ {day['tempMin']}~{day['tempMax']}°C"
                f"\n  ☁️ {day['textDay']} / {day['textNight']}"
            )
        return "\n".join(result)

if __name__ == "__main__":
    mcp.run(transport="sse")
