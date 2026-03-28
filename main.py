"""
AstrBot 热点榜单插件 v3.0.1
作者：星落云
仓库：https://github.com/qdie1546-source/astrbot_plugin_hotboard
支持多平台热榜获取、定时推送、合并转发等功能
"""
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Optional

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import logger
import astrbot.api.message_components as Comp


class HotboardPlugin(Star):
    """热点榜单插件主类"""
    
    # 平台名称映射（硬编码，避免配置不支持dict类型）
    PLATFORM_NAMES = {
        "bilibili": "哔哩哔哩",
        "acfun": "A站",
        "weibo": "微博热搜",
        "zhihu": "知乎热榜",
        "zhihu-daily": "知乎日报",
        "douyin": "抖音",
        "kuaishou": "快手",
        "douban-movie": "豆瓣电影",
        "douban-group": "豆瓣小组",
        "tieba": "百度贴吧",
        "hupu": "虎扑",
        "ngabbs": "NGA论坛",
        "v2ex": "V2EX",
        "52pojie": "吾爱破解",
        "hostloc": "全球主机交流",
        "coolapk": "酷安",
        "baidu": "百度热搜",
        "thepaper": "澎湃新闻",
        "toutiao": "今日头条",
        "qq-news": "腾讯新闻",
        "sina": "新浪热搜",
        "sina-news": "新浪新闻",
        "netease-news": "网易新闻",
        "huxiu": "虎嗅",
        "ifanr": "爱范儿",
        "sspai": "少数派",
        "ithome": "IT之家",
        "ithome-xijiayi": "IT之家喜加一",
        "juejin": "掘金",
        "jianshu": "简书",
        "guokr": "果壳",
        "36kr": "36氪",
        "51cto": "51CTO",
        "csdn": "CSDN",
        "nodeseek": "NodeSeek",
        "hellogithub": "HelloGitHub",
        "lol": "英雄联盟",
        "genshin": "原神",
        "honkai": "崩坏3",
        "starrail": "星穹铁道",
        "netease-music": "网易云音乐热歌榜",
        "qq-music": "QQ音乐热歌榜",
        "weread": "微信读书",
        "weatheralarm": "天气预警",
        "earthquake": "地震速报",
        "history": "历史上的今天"
    }
    
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.platform_names = self.PLATFORM_NAMES
        self.default_platforms = config.get("default_platforms", ["weibo"])
        self.api_key = config.get("api_key", "uapi-zrvbf3gaVhkhUfPrKrzOHpYA5ZU2ij3pz5kM3nNs")
        self.top_count = config.get("top_count", 10)
        self.merge_forward = config.get("merge_forward", True)  # 改为合并转发
        self.enable_schedule = config.get("enable_schedule", True)
        self.schedule_time = config.get("schedule_time", "08:00")
        self.target_groups = config.get("target_groups", [])
        self.schedule_task = None
        
    async def terminate(self):
        """插件卸载时清理定时任务"""
        if self.schedule_task:
            self.schedule_task.cancel()
            try:
                await self.schedule_task
            except asyncio.CancelledError:
                pass
    
    @filter.on_astrbot_loaded()
    async def on_astrbot_loaded(self):
        """Bot加载完成后启动定时任务"""
        if self.enable_schedule and self.schedule_time:
            logger.info(f"[Hotboard] 启动定时任务，每日 {self.schedule_time} 发送热榜")
            self.schedule_task = asyncio.create_task(self._schedule_loop())
    
    async def _schedule_loop(self):
        """定时任务循环"""
        while True:
            try:
                now = datetime.now()
                target_time = datetime.strptime(self.schedule_time, "%H:%M")
                target = now.replace(hour=target_time.hour, minute=target_time.minute, second=0, microsecond=0)
                
                if target < now:
                    target = target.replace(day=target.day + 1)
                
                wait_seconds = (target - now).total_seconds()
                logger.debug(f"[Hotboard] 下次发送时间: {target}, 等待 {wait_seconds} 秒")
                
                await asyncio.sleep(wait_seconds)
                
                # 执行定时发送
                await self._scheduled_send()
                
                # 等待60秒避免重复触发
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Hotboard] 定时任务异常: {e}")
                await asyncio.sleep(60)
    
    async def _scheduled_send(self):
        """执行定时发送"""
        if not self.default_platforms:
            logger.warning("[Hotboard] 未设置默认平台，跳过定时发送")
            return
            
        try:
            results = await self._fetch_multiple_platforms(self.default_platforms)
            if not results:
                return
            
            # 构建合并转发消息
            nodes = self._build_forward_nodes(results)
            
            logger.info(f"[Hotboard] 定时发送热榜到 {len(self.target_groups) if self.target_groups else '配置的目标'}")
            
            # 如果有指定目标群组，发送到指定群组
            if self.target_groups:
                for target in self.target_groups:
                    try:
                        if isinstance(target, str) and ":" in target:
                            umo = target
                        else:
                            logger.warning(f"[Hotboard] 目标格式不正确: {target}")
                            continue
                        
                        # 发送合并转发消息
                        await self.context.send_message(umo, nodes)
                            
                    except Exception as e:
                        logger.error(f"[Hotboard] 发送到 {target} 失败: {e}")
            
        except Exception as e:
            logger.error(f"[Hotboard] 定时发送失败: {e}")
    
    async def _fetch_hotboard(self, platform_type: str) -> Optional[Dict]:
        """获取单个平台的热榜数据"""
        url = f"https://uapis.cn/api/v1/misc/hotboard?type={platform_type}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=30) as resp:
                    if resp.status != 200:
                        logger.error(f"[Hotboard] API请求失败: {resp.status}")
                        return None
                    
                    data = await resp.json()
                    
                    if not data or "list" not in data:
                        logger.warning(f"[Hotboard] {platform_type} 返回数据为空")
                        return None
                    
                    return {
                        "type": platform_type,
                        "name": self.platform_names.get(platform_type, platform_type),
                        "update_time": data.get("update_time", ""),
                        "list": data.get("list", [])[:self.top_count]
                    }
                    
        except Exception as e:
            logger.error(f"[Hotboard] 获取 {platform_type} 热榜失败: {e}")
            return None
    
    async def _fetch_multiple_platforms(self, platforms: List[str]) -> List[Dict]:
        """并发获取多个平台的热榜"""
        tasks = [self._fetch_hotboard(p) for p in platforms]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result:
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"[Hotboard] 获取异常: {result}")
        
        return valid_results
    
    def _build_forward_nodes(self, results: List[Dict]) -> List[Comp.Node]:
        """
        构建合并转发节点列表
        
        格式：
        title&热度hot_value
        [pic]
        url
        title&热度hot_value
        [pic]
        url
        ...
        """
        nodes = []
        
        for result in results:
            platform_name = result["name"]
            update_time = result.get("update_time", "")
            
            # 为每个平台创建一个转发节点
            node_content = []
            
            # 平台标题
            header = f"📌 {platform_name}"
            if update_time:
                header += f" 更新于 {update_time}"
            node_content.append(Comp.Plain(header + "\n" + "="*30 + "\n"))
            
            # 热榜条目 - 新格式
            for item in result["list"]:
                # title&热度
                title = item.get("title", "")
                hot_value = item.get("hot_value", "")
                
                if hot_value:
                    title_line = f"{title}&热度{hot_value}"
                else:
                    title_line = title
                
                node_content.append(Comp.Plain(title_line + "\n"))
                
                # 封面图
                cover = item.get("cover") or item.get("pic")
                if cover:
                    node_content.append(Comp.Image.fromURL(cover))
                
                # url
                url = item.get("url", "")
                if url:
                    node_content.append(Comp.Plain(url + "\n"))
                
                # 分隔行
                node_content.append(Comp.Plain("\n"))
            
            # 创建转发节点
            node = Comp.Node(
                uin=0,  # 使用默认值
                name=f"{platform_name}热榜",
                content=node_content
            )
            nodes.append(node)
        
        return nodes
    
    def _build_normal_message(self, results: List[Dict]) -> List[List]:
        """构建普通消息链列表（不使用合并转发）"""
        messages = []
        
        for result in results:
            chain = []
            platform_name = result["name"]
            update_time = result.get("update_time", "")
            
            # 平台标题
            header = f"📌 {platform_name}"
            if update_time:
                header += f" 更新于 {update_time}"
            chain.append(Comp.Plain(header + "\n" + "="*30 + "\n\n"))
            
            # 热榜条目
            for item in result["list"]:
                # title&热度
                title = item.get("title", "")
                hot_value = item.get("hot_value", "")
                
                if hot_value:
                    title_line = f"{title}&热度{hot_value}"
                else:
                    title_line = title
                
                chain.append(Comp.Plain(title_line + "\n"))
                
                # 封面图
                cover = item.get("cover") or item.get("pic")
                if cover:
                    chain.append(Comp.Image.fromURL(cover))
                
                # url
                url = item.get("url", "")
                if url:
                    chain.append(Comp.Plain(url + "\n"))
                
                chain.append(Comp.Plain("\n"))
            
            messages.append(chain)
        
        return messages
    
    @filter.command("今日热点")
    async def today_hot(self, event: AstrMessageEvent, platform: str = None):
        """
        查询今日热点榜单
        用法：
        /今日热点 - 使用默认平台查询
        /今日热点 抖音 - 查询指定平台（如抖音、微博等）
        """
        # 确定要查询的平台
        if platform:
            target_platforms = []
            
            # 直接匹配type
            if platform in self.platform_names:
                target_platforms = [platform]
            else:
                # 尝试匹配中文名
                found = False
                for p_type, p_name in self.platform_names.items():
                    if p_name == platform or platform in p_name:
                        target_platforms = [p_type]
                        found = True
                        break
                
                if not found:
                    yield event.plain_result(f"❌ 未知平台：{platform}\n💡 请使用 /热点平台 查看所有支持的平台")
                    return
        else:
            # 使用默认平台
            if not self.default_platforms:
                yield event.plain_result("⚠️ 未设置默认平台，请使用 /今日热点 <平台名> 指定平台\n💡 示例：/今日热点 weibo")
                return
            target_platforms = self.default_platforms
        
        # 发送等待提示
        yield event.plain_result("🔍 正在获取热榜数据，请稍候...")
        
        try:
            # 获取数据
            results = await self._fetch_multiple_platforms(target_platforms)
            
            if not results:
                yield event.plain_result("❌ 获取热榜数据失败，请稍后重试")
                return
            
            # 根据设置选择发送方式
            if self.merge_forward:
                # 使用合并转发
                nodes = self._build_forward_nodes(results)
                
                # 合并转发需要包装在列表中
                yield event.chain_result(nodes)
            else:
                # 普通发送
                messages = self._build_normal_message(results)
                for chain in messages:
                    yield event.chain_result(chain)
                
                # 如果多平台，提示来源
                if len(results) > 1:
                    platform_list = "、".join([r["name"] for r in results])
                    yield event.plain_result(f"✅ 以上来自：{platform_list}")
                
        except Exception as e:
            logger.error(f"[Hotboard] 指令执行异常: {e}")
            yield event.plain_result(f"❌ 获取热榜失败：{str(e)}")
    
    @filter.command("热点平台")
    async def list_platforms(self, event: AstrMessageEvent):
        """
        查看支持的热点平台列表
        用法：/热点平台
        """
        msg = "📋 支持的热榜平台（使用 /今日热点 <平台代码> 查询）：\n\n"
        
        # 按分类显示
        categories = {
            "社交": ["weibo", "zhihu", "zhihu-daily", "tieba", "v2ex", "ngabbs", "hupu"],
            "视频": ["bilibili", "acfun", "douyin", "kuaishou"],
            "新闻": ["thepaper", "toutiao", "qq-news", "sina", "sina-news", "netease-news", "baidu"],
            "科技": ["ithome", "ithome-xijiayi", "juejin", "csdn", "51cto", "nodeseek", "hellogithub", "sspai", "huxiu", "ifanr", "jianshu", "guokr", "36kr"],
            "娱乐": ["douban-movie", "douban-group", "netease-music", "qq-music", "weread"],
            "游戏": ["lol", "genshin", "honkai", "starrail"],
            "工具": ["weatheralarm", "earthquake", "history", "52pojie", "hostloc", "coolapk"]
        }
        
        for cat_name, platforms in categories.items():
            msg += f"【{cat_name}】"
            items = []
            for p in platforms:
                if p in self.platform_names:
                    items.append(f"{self.platform_names[p]}({p})")
            msg += " | ".join(items) + "\n"
        
        msg += f"\n💡 当前默认平台：{', '.join([self.platform_names.get(p, p) for p in self.default_platforms])}\n"
        msg += "💡 发送格式：/今日热点 weibo 或 /今日热点 微博热搜"
        
        yield event.plain_result(msg)