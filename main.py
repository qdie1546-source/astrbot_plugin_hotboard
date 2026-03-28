"""
AstrBot 热点榜单插件 v3.0.1
作者：星落云
仓库：https://github.com/qdie1546-source/astrbot_plugin_hotboard
支持多平台热榜获取、定时推送、合并发送等功能
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
    
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.platform_names = config.get("platform_names", {})
        self.default_platforms = config.get("default_platforms", ["weibo"])
        self.api_key = config.get("api_key", "uapi-zrvbf3gaVhkhUfPrKrzOHpYA5ZU2ij3pz5kM3nNs")
        self.top_count = config.get("top_count", 10)
        self.merge_message = config.get("merge_message", True)
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
                
            # 构建消息
            message_chains = self._build_messages(results)
            
            # 发送到目标群组或所有群组
            logger.info(f"[Hotboard] 定时发送热榜到 {len(self.target_groups) if self.target_groups else '配置的目标'}")
            
            # 如果有指定目标群组，发送到指定群组
            if self.target_groups:
                for target in self.target_groups:
                    try:
                        # 解析目标格式：platform:type:id
                        if isinstance(target, str) and ":" in target:
                            parts = target.split(":")
                            if len(parts) >= 3:
                                umo = target
                            else:
                                logger.warning(f"[Hotboard] 目标格式不正确: {target}")
                                continue
                        else:
                            logger.warning(f"[Hotboard] 目标格式不正确: {target}")
                            continue
                        
                        # 发送消息
                        for chain in message_chains:
                            await self.context.send_message(umo, chain)
                            await asyncio.sleep(1)  # 避免发送过快
                            
                    except Exception as e:
                        logger.error(f"[Hotboard] 发送到 {target} 失败: {e}")
            
        except Exception as e:
            logger.error(f"[Hotboard] 定时发送失败: {e}")
    
    async def _fetch_hotboard(self, platform_type: str) -> Optional[Dict]:
        """
        获取单个平台的热榜数据
        
        Args:
            platform_type: 平台类型标识
            
        Returns:
            解析后的JSON数据或None
        """
        url = f"https://uapis.cn/api/v1/misc/hotboard?type={platform_type}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
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
        """
        并发获取多个平台的热榜
        
        Args:
            platforms: 平台类型列表
            
        Returns:
            热榜数据列表
        """
        tasks = [self._fetch_hotboard(p) for p in platforms]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result:
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"[Hotboard] 获取异常: {result}")
        
        return valid_results
    
    def _format_single_item(self, item: Dict, platform_name: str) -> List:
        """
        格式化单条热榜条目为消息组件
        
        模板：
        title&hot_value
        [pic]
        url
        
        Args:
            item: 热榜条目数据
            platform_name: 平台名称
            
        Returns:
            消息组件列表
        """
        chain = []
        
        # 标题和热度
        title = item.get("title", "")
        hot_value = item.get("hot_value", "")
        
        if hot_value:
            text = f"{title}&{hot_value}"
        else:
            text = title
            
        chain.append(Comp.Plain(text))
        
        # 封面图（如果有）
        cover = item.get("cover") or item.get("pic")
        if cover:
            chain.append(Comp.Image.fromURL(cover))
        
        # URL
        url = item.get("url", "")
        if url:
            chain.append(Comp.Plain(url))
        
        return chain
    
    def _build_messages(self, results: List[Dict]) -> List[List]:
        """
        构建消息链列表
        
        Args:
            results: 热榜数据列表
            
        Returns:
            如果是合并模式，返回包含一个大消息链的列表；
            如果是分开模式，返回多个消息链的列表
        """
        if not results:
            return []
        
        if self.merge_message:
            # 合并模式：所有平台合并为一条消息
            merged_chain = []
            
            for idx, result in enumerate(results):
                if idx > 0:
                    merged_chain.append(Comp.Plain("\n" + "="*20 + "\n"))
                
                # 平台标题
                platform_title = f"【{result['name']}】"
                if result.get("update_time"):
                    platform_title += f" 更新于 {result['update_time']}"
                merged_chain.append(Comp.Plain(platform_title + "\n"))
                
                # 热榜条目
                for i, item in enumerate(result["list"], 1):
                    merged_chain.append(Comp.Plain(f"\n{i}. "))
                    item_chain = self._format_single_item(item, result["name"])
                    merged_chain.extend(item_chain)
                    merged_chain.append(Comp.Plain("\n"))
            
            return [merged_chain]
        else:
            # 分开模式：每个平台单独发送
            messages = []
            
            for result in results:
                chain = []
                
                # 平台标题
                platform_title = f"【{result['name']}】"
                if result.get("update_time"):
                    platform_title += f" 更新于 {result['update_time']}"
                chain.append(Comp.Plain(platform_title + "\n"))
                
                # 热榜条目
                for i, item in enumerate(result["list"], 1):
                    chain.append(Comp.Plain(f"\n{i}. "))
                    item_chain = self._format_single_item(item, result["name"])
                    chain.extend(item_chain)
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
            # 检查是否是有效的平台类型（支持中文名或英文名）
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
                    yield event.plain_result(f"未知平台：{platform}。请使用有效的平台名称，如：微博热搜、抖音、bilibili等")
                    return
        else:
            # 使用默认平台
            if not self.default_platforms:
                yield event.plain_result("未设置默认平台，请使用 /今日热点 <平台名> 指定平台")
                return
            target_platforms = self.default_platforms
        
        # 发送等待提示
        await event.send(event.plain_result("🔍 正在获取热榜数据..."))
        
        try:
            # 获取数据
            results = await self._fetch_multiple_platforms(target_platforms)
            
            if not results:
                yield event.plain_result("❌ 获取热榜数据失败，请稍后重试")
                return
            
            # 构建并发送消息
            messages = self._build_messages(results)
            
            for chain in messages:
                yield event.chain_result(chain)
                
            # 如果不是合并模式，添加平台提示
            if not self.merge_message and len(results) > 1:
                platform_list = "、".join([r["name"] for r in results])
                yield event.plain_result(f"\n✅ 以上来自：{platform_list}")
                
        except Exception as e:
            logger.error(f"[Hotboard] 指令执行异常: {e}")
            yield event.plain_result(f"❌ 获取热榜失败：{str(e)}")
    
    @filter.command("热点平台")
    async def list_platforms(self, event: AstrMessageEvent):
        """
        查看支持的热点平台列表
        
        用法：/热点平台
        """
        msg = "📋 支持的热榜平台（使用 /今日热点 <平台名> 查询）：\n\n"
        
        # 分组显示，每行4个
        platforms = list(self.platform_names.items())
        for i in range(0, len(platforms), 4):
            row = platforms[i:i+4]
            line = " | ".join([f"{name}({type})" for type, name in row])
            msg += line + "\n"
        
        msg += f"\n💡 默认平台：{', '.join([self.platform_names.get(p, p) for p in self.default_platforms])}"
        
        yield event.plain_result(msg)