import httpx
import time
import asyncio
from astrbot.api.star import Star, register
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api import logger

API_URL = "https://uapis.cn/api/v1/misc/hotboard"

TYPE_MAP = {
    "抖音": "douyin",
    "微博": "weibo",
    "快手": "kuaishou",
    "知乎": "zhihu",
    "B站": "bilibili",
    "贴吧": "tieba"
}

@register("astrbot_plugin_hotboard", "HotBoard", "热点榜单插件", "2.0.0")
class HotBoardPlugin(Star):

    def __init__(self, context):
        super().__init__(context)
        self.config = self.load_config()
        self.cache = {}

        # 启动定时任务
        asyncio.create_task(self.loop_push())

    # ======================
    # 限流
    # ======================
    def is_rate_limited(self, key):
        now = time.time()
        last = self.cache.get(key, 0)
        if now - last < 60:
            return True
        self.cache[key] = now
        return False

    # ======================
    # API请求
    # ======================
    async def fetch(self, type_):
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}"
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(API_URL, headers=headers, params={"type": type_})
            data = resp.json()

        if "list" not in data:
            raise Exception("API异常")

        return data

    # ======================
    # 格式化
    # ======================
    def format(self, type_, data):
        limit = self.config.get("limit", 5)
        text = f"\n【{type_} 热点】\n"

        for item in data["list"][:limit]:
            text += f"{item['title']}（{item['hot_value']}）\n{item['url']}\n\n"

        return text

    # ======================
    # 主逻辑
    # ======================
    async def get_hotboards(self, types):
        result = ""

        for t in types:
            try:
                if self.is_rate_limited(t):
                    result += f"\n【{t} 请求过快】\n"
                    continue

                data = await self.fetch(t)
                result += self.format(t, data)

            except Exception as e:
                logger.error(f"{t} 获取失败: {e}")
                result += f"\n【{t} 获取失败】\n"

        return result

    # ======================
    # 指令
    # ======================
    @filter.command("今日热点")
    async def hot(self, event: AstrMessageEvent, type_: str = None):

        if type_:
            type_ = TYPE_MAP.get(type_, type_)
            types = [type_]
        else:
            types = self.config.get("default_types", ["weibo"])

        result = await self.get_hotboards(types)

        if self.config.get("use_image", False):
            img = await self.text_to_image(result)
            yield event.image_result(img)
        else:
            yield event.plain_result(result)

    # ======================
    # 手动定时任务（核心替代方案）
    # ======================
    async def loop_push(self):
        await asyncio.sleep(10)  # 等待Bot启动

        while True:
            try:
                if self.config.get("push_enabled", False):

                    types = self.config.get("default_types", ["weibo"])
                    result = await self.get_hotboards(types)

                    await self.context.send_all(result)

            except Exception as e:
                logger.error(f"定时任务错误: {e}")

            # 每30分钟执行一次
            await asyncio.sleep(1800)