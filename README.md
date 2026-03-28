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
```
# 克隆仓库
```
git clone https://github.com/qdie1546-source/astrbot_plugin_hotboard.git
```
# 重启 AstrBot



**指令格式**：`/今日热点 <平台代码>`

**支持格式**：
- 英文代码（如 `weibo`）
- 中文名称（如 `微博热搜`）

**使用示例**：
指令：/今日热点 <平台代码> 支持：英文代码（weibo）或中文名称（微博热搜）
示例：  /今日热点 weibo  /今日热点 抖音  /今日热点 bilibili

__💡 配置提示：__在后台 WebUI 配置时，请使用括号内的英文标识（如 `weibo`、`douyin`）

## 📋 平台标识速查表

### 热门 常用平台

| 标识 | 平台名称 | 标识 | 平台名称 |
| --- | --- | --- | --- |
| 标识 | 平台名称 | 标识 | 平台名称 |
| weibo | 微博热搜 | douyin | 抖音 |
| bilibili | 哔哩哔哩 | zhihu | 知乎热榜 |
| kuaishou | 快手 | tieba | 百度贴吧 |
| baidu | 百度热搜 | toutiao | 今日头条 |

### 社交 社交资讯

| 标识 | 平台名称 | 标识 | 平台名称 |
| --- | --- | --- | --- |
| 标识 | 平台名称 | 标识 | 平台名称 |
| zhihu-daily | 知乎日报 | v2ex | V2EX |
| ngabbs | NGA论坛 | hupu | 虎扑 |
| douban-movie | 豆瓣电影 | douban-group | 豆瓣小组 |

### 新闻 新闻媒体

| 标识 | 平台名称 | 标识 | 平台名称 |
| --- | --- | --- | --- |
| 标识 | 平台名称 | 标识 | 平台名称 |
| thepaper | 澎湃新闻 | qq-news | 腾讯新闻 |
| sina | 新浪热搜 | sina-news | 新浪新闻 |
| netease-news | 网易新闻 | huxiu | 虎嗅 |

### 科技 科技数码

| 标识 | 平台名称 | 标识 | 平台名称 |
| --- | --- | --- | --- |
| 标识 | 平台名称 | 标识 | 平台名称 |
| ithome | IT之家 | ithome-xijiayi | IT之家喜加一 |
| juejin | 掘金 | csdn | CSDN |
| sspai | 少数派 | 36kr | 36氪 |
| nodeseek | NodeSeek | hellogithub | HelloGitHub |

### 娱乐 娱乐影音

| 标识 | 平台名称 | 标识 | 平台名称 |
| --- | --- | --- | --- |
| 标识 | 平台名称 | 标识 | 平台名称 |
| netease-music | 网易云音乐热歌榜 | qq-music | QQ音乐热歌榜 |
| weread | 微信读书 | acfun | A站 |

### 游戏 游戏

| 标识 | 平台名称 | 标识 | 平台名称 |
| --- | --- | --- | --- |
| 标识 | 平台名称 | 标识 | 平台名称 |
| lol | 英雄联盟 | genshin | 原神 |
| honkai | 崩坏3 | starrail | 星穹铁道 |

### 工具 实用工具

| 标识 | 平台名称 | 标识 | 平台名称 |
| --- | --- | --- | --- |
| 标识 | 平台名称 | 标识 | 平台名称 |
| weatheralarm | 天气预警 | earthquake | 地震速报 |
| history | 历史上的今天 | 52pojie | 吾爱破解 |

## 📱 指令使用

查询默认平台（后台配置）

`/今日热点`

查询指定平台（支持英文标识或中文名）

`/今日热点 weibo`  
`/今日热点 抖音`

查看所有支持的平台

`/热点平台`

## ⚙️ 后台配置说明

### 默认平台配置

在 WebUI → 插件 → 热点榜单 → __默认热榜平台__ 中填写：

```
["weibo", "douyin", "bilibili"]
```

__常用组合推荐：__

*   综合资讯：`["weibo", "zhihu", "baidu"]`
*   短视频：`["douyin", "kuaishou"]`
*   科技数码：`["ithome", "juejin", "sspai"]`
*   游戏：`["lol", "genshin", "starrail"]`

### 其他配置项

| 配置项 | 说明 | 示例 |
| --- | --- | --- |
| 配置项 | 说明 | 示例 |
| schedule_time | 定时发送时间（24小时制） | "08:00" |
| merge_forward | 使用合并转发（QQ聊天记录样式） | true / false |
| top_count | 每个平台显示条数（1-50） | 10 |
| target_groups | 定时发送目标群组ID列表 | ["aiocqhttp:GroupMessage:123456"] |

__📌 提示：__发送 `/热点平台` 指令可在聊天中查看完整平台列表

仓库地址：[https://github.com/qdie1546-source/astrbot\_plugin\_hotboard](https://github.com/qdie1546-source/astrbot_plugin_hotboard)

版本：v3.0.1 | 作者：星落云 | 适配 AstrBot >= v4.22.0