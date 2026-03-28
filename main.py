import httpx
import asyncio
from astrbot.api.star import Star, register
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api import logger

API_URL = "https://uapis.cn/api/v1/misc/hotboard"
DEFAULT_API_KEY = "uapi-zrvbf3gaVhkhUfPrKrzOHpYA5ZU2ij3pz5kM3nNs"

@register("astrbot_plugin_hotboard", "星落云", "热点榜单插件", "2.0.6")
class HotBoardPlugin(Star):

    def __init__(self, context):
        super().__init__(context)
        self.config = context.config  # ⚠️ 兼容 v4.22
        asyncio.create_task(self.loop_push())

    async def fetch(self, type_):
        headers = {"Authorization": f"Bearer {DEFAULT_API_KEY}"}
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(API_URL, headers=headers, params={"type": type_})
            return r.json()

    async def build_forward(self, types):
        nodes = []
        for t in types:
            try:
                data = await self.fetch(t)
                nodes.append({"type": "node", "data": {"name": "热点榜单", "uin": "10000", "content": f"【{t}】"}})
                for i in data.get("list", []):
                    nodes.append({
                        "type": "node",
                        "data": {"name": "热点榜单", "uin": "10000", "content": f"{i['title']}（{i['hot_value']}）\n{i['url']}"}
                    })
            except Exception as e:
                logger.error(f"{t} 获取失败: {e}")
        return nodes

    @filter.command("今日热点")
    async def hot(self, event: AstrMessageEvent, type_: str = None):
        types = [type_] if type_ else self.config.get("default_types", ["weibo"])
        if self.config.get("use_forward", True):
            msg = await self.build_forward(types)
            yield event.chain_result(msg)
        else:
            text = ""
            for t in types:
                data = await self.fetch(t)
                text += f"\n【{t}】\n"
                for i in data.get("list", []):
                    text += f"{i['title']}（{i['hot_value']}）\n{i['url']}\n\n"
            yield event.plain_result(text)

    async def loop_push(self):
        await asyncio.sleep(10)
        while True:
            try:
                if self.config.get("push_enabled", True):
                    types = self.config.get("default_types", ["weibo"])
                    msg = await self.build_forward(types)
                    await self.context.send_all(msg)
            except Exception as e:
                logger.error(f"定时任务错误: {e}")
            await asyncio.sleep(self.config.get("interval", 1800))