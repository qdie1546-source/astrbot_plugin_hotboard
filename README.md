<div align="center">

# 🔥 AstrBot 热点榜单插件

[![Version](https://img.shields.io/badge/version-v3.0.1-blue.svg)](https://github.com/qdie1546-source/astrbot_plugin_hotboard)
[![AstrBot](https://img.shields.io/badge/AstrBot->=v4.22.0-green.svg)](https://github.com/AstrBotDevs/AstrBot)
[![Author](https://img.shields.io/badge/author-星落云-orange.svg)](https://github.com/qdie1546-source)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**支持微博、抖音、B站、知乎等 50+ 平台热榜获取，定时推送，智能合并**

[功能特性](#功能特性) • [安装方法](#安装方法) • [使用指南](#使用指南) • [配置说明](#配置说明) • [支持平台](#支持平台)

</div>

---

## 📌 功能特性

- ✅ **多平台支持** - 支持微博、抖音、B站、知乎等 50+ 主流平台热榜
- ✅ **智能查询** - `/今日热点` 查询默认平台，`/今日热点 抖音` 查询指定平台
- ✅ **定时推送** - 后台可设置每日定时自动推送热榜到指定群组
- ✅ **多选默认** - 后台可配置多个默认平台，同时获取多个平台热榜
- ✅ **合并发送** - 支持将多个平台热榜合并为一条消息或分条发送
- ✅ **精美模板** - 标题&热度 + 封面图 + 链接的格式展示
- ✅ **智能匹配** - 支持中文平台名（如"微博热搜"）或英文标识（如"weibo"）
- ✅ **异步并发** - 多平台查询时并发请求，快速响应

---

## 📥 安装方法

### 方法一：通过 AstrBot 插件市场安装（推荐）

1. 打开 AstrBot WebUI
2. 进入 **插件** → **插件市场**
3. 搜索 `astrbot_plugin_hotboard` 或 `热点榜单`
4. 点击安装并重启 AstrBot

### 方法二：手动安装

```bash
# 进入 AstrBot 插件目录
cd AstrBot/data/plugins

# 克隆仓库
git clone https://github.com/qdie1546-source/astrbot_plugin_hotboard.git

# 重启 AstrBot



**指令格式**：`/今日热点 <平台代码>`

**支持格式**：
- 英文代码（如 `weibo`）
- 中文名称（如 `微博热搜`）

**使用示例**：
指令：/今日热点 <平台代码> 支持：英文代码（weibo）或中文名称（微博热搜）
示例：  /今日热点 weibo  /今日热点 抖音  /今日热点 bilibili

## 📋 平台列表（分类展示）

### 社交资讯
- weibo(微博热搜), zhihu(知乎热榜), tieba(百度贴吧), v2ex, ngabbs(NGA论坛), hupu(虎扑)

### 视频娱乐  
- bilibili(哔哩哔哩), acfun(A站), douyin(抖音), kuaishou(快手)

### 新闻媒体
- thepaper(澎湃新闻), toutiao(今日头条), qq-news(腾讯新闻), sina(新浪热搜), baidu(百度热搜)

### 科技数码
- ithome(IT之家), juejin(掘金), csdn, sspai(少数派), huxiu(虎嗅), 36kr(36氪)

### 游戏
- lol(英雄联盟), genshin(原神), honkai(崩坏3), starrail(星穹铁道)

### 实用工具
- weatheralarm(天气预警), earthquake(地震速报), history(历史上的今天)