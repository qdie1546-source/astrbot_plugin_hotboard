import httpx
import asyncio
from astrbot.api.star import Star, register
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api import logger

API_URL = "https://uapis.cn/api/v1/misc/hotboard"

@register("astrbot_plugin_hotboard", "星落云", "热点榜单插件", "2.0.2")
class HotBoardPlugin(Star):

    def __init__(self, context):
        super().__init__(context)
        self.config = self.load_config()
        asyncio.create_task(self.loop_push())

    async def fetch(self, type_):
        headers = {
            "Authorization": f"Bearer {self.config.get('api_key','')}"
        }

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(API_URL, headers=headers, params={"type": type_})
            return r.json()

    async def build_forward(self, types):
        nodes = []

        for t in types:
            try:
                data = await self.fetch(t)

                nodes.append({
                    "type": "node",
                    "data": {
                        "name": "热点榜单",
                        "uin": "10000",
                        "content": f"【{t}】"
                    }
                })

                for i in data["list"]:
                    nodes.append({
                        "type": "node",
                        "data": {
                            "name": "热点榜单",
                            "uin": "10000",
                            "content": f"{i['title']}（{i['hot_value']}）\n{i['url']}"
                        }
                    })

            except Exception as e:
                logger.error(e)

        return nodes

    @filter.command("今日热点")
    async def hot(self, event: AstrMessageEvent, type_: str = None):

        if type_:
            types = [type_]
        else:
            types = self.config.get("default_types", ["weibo"])

        if self.config.get("use_forward", True):
            msg = await self.build_forward(types)
            yield event.chain_result(msg)
        else:
            yield event.plain_result(str(types))

    async def loop_push(self):
        await asyncio.sleep(10)

        while True:
            try:
                if self.config.get("push_enabled", False):

                    types = self.config.get("default_types", ["weibo"])
                    msg = await self.build_forward(types)

                    await self.context.send_all(msg)

            except Exception as e:
                logger.error(e)

            await asyncio.sleep(self.config.get("interval", 1800))