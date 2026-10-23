# MaaBH2 · 崩坏学园2 小助手

一个基于 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) 的**资源包（Resource Package）**，遵循 **Project Interface V2** 协议，通过「图像识别 + 模拟点击」自动完成崩坏学园2 的日常刷体力、领奖励等重复操作。

> 本项目**不是一个独立程序**，它是一份给 [MFAAvalonia](https://github.com/MaaXYZ/MFAAvalonia)（简称 MFA）客户端加载的资源包。

## 关于作者

作者是一名**电工**，不是程序员。这个脚本是在 AI 的辅助下、边学边做鼓捣出来的，编程水平有限，代码写得比较粗糙，也谈不上什么规范。

所以：

- 本项目主要**自用**，顺便分享出来给有同样需求的人。
- 如果哪里写得不好、跑不通，**欢迎提意见**，但请别用专业程序员的标准来要求。
- 遇到问题可以先看看下面的「常见问题」，实在不行再联系作者。

> **强烈建议**：请使用 [AUTO-MAS](https://doc.auto-mas.top)（一种游戏托管软件）来挂载本脚本，搭配**雷电9模拟器**一起托管运行。AUTO-MAS 能自动识别带 `interface.json` 的 MaaFramework 项目（MFW 项目），帮你自动开关游戏、定时执行、多账号托管，比自己手动盯着 MFA 客户端省心得多。

---

## 快速部署（推荐）

本项目以 **MFA 资源包** 的形式分发。有两种运行方式：

### 方式一：用 AUTO-MAS 托管（强烈推荐）

[AUTO-MAS](https://doc.auto-mas.top) 是一款游戏托管软件，能直接接入带 `interface.json` 的 MaaFramework 项目（MFW 项目）。用它托管，可以自动开关游戏、定时执行、多账号管理，省心省力。

1. 安装 [AUTO-MAS](https://doc.auto-mas.top) 和**雷电9模拟器**。
2. 在 AUTO-MAS 中添加「MFW 项目」，选中本项目的目录即可自动识别。
3. 绑定雷电9模拟器，配置好任务与计划表，即可托管运行。

> 具体配置可参考 AUTO-MAS 的 [MFW 项目配置方法](https://doc.auto-mas.top/docs/script-guide/maafw.html)。

### 方式二：直接用 MFA 客户端

1. 安装 [MFAAvalonia](https://github.com/MaaXYZ/MFAAvalonia/releases)（MFA 客户端，需 .NET 10 Runtime）。
2. 启动 MFA 客户端。
3. 将本项目的**资源压缩包（zip）直接拖入 MFA 窗口**，确认后即可自动更新并加载资源。

> 资源包内含 `interface.json`、`resource/pipeline/main.json`、`resource/image/` 等全部资源，MFA 会按 Project Interface V2 协议自动识别并加载，无需手动逐个复制文件。

---

## 资源包结构

```
.
├── interface.json              ← 任务与选项定义（Project Interface V2）
└── resource/
    ├── pipeline/
    │   └── main.json           ← 任务流水线（Pipeline）节点
    └── image/                  ← 图像识别模板
```

`resource/model/`（OCR 模型）由 MFA 客户端自带，**无需**包含在本资源包中。

---

## 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows |
| 模拟器 | 雷电模拟器（LDPlayer） |
| 分辨率 | **1280 × 720**（识别区域与点击坐标均基于此分辨率） |
| 游戏 | 崩坏学园2（多服） |
| 客户端 | MFAAvalonia（需 .NET 10 Runtime） |

### 支持渠道

本资源包的「启动游戏」任务支持以下渠道包，可在「启动渠道」选项中指定优先启动的包，失败后自动按顺序轮询：

| 渠道 | 包名 | 兼容状态 |
|------|------|----------|
| 国服（官方） | `com.miHoYo.HSoDv2Original` | 理论支持，未实测 |
| UC 渠道 | `com.miHoYo.HSoDv22144.uc` | ✅ 已实测，正常 |
| 混服 | `com.miHoYo.HSoDv2.mix` | ✅ 已实测，正常 |
| 腾讯服 | `com.miHoYo.HSoDv22144.tencent` | 理论支持，未实测 |
| B 服 | `com.miHoYo.HSoDv2BiliBiliRelease` | 理论支持，未实测 |
| 测试服 | `com.miHoYo.HSoDv2Beta` | 理论支持，未实测 |

> ⚠️ **兼容性说明**：由于作者只有 UC 服和混服有高练度账号，目前**只有这两个渠道经过完整实测、确认正常兼容**。其余渠道（国服、腾讯服、B 服、测试服）的包名与启动流程已按同款逻辑接入，理论上可以运行，但**未经过实测验证**，可能存在识别差异，欢迎有条件的朋友测试反馈。

---

## 配置任务

资源加载后，在 MFA 客户端中：

1. 连接设备（雷电模拟器 / adb），进入游戏主界面。
2. 在任务列表勾选需要的任务（如「日常活动清体力」）。
3. 按需设置选项：
   - **战斗次数**：总共打几场（填 1~99 的整数）。
   - **使用双倍体力**：开启后，体力不足时自动兑换双倍体力继续打。

> 本资源包不含作者本机的设备配置，设备与任务勾选需在 MFA 客户端内自行设置。

---

## 任务说明

内置以下日常任务（对应 `interface.json` 中的 task）：

- 启动游戏
- 进入游戏（自选服务器）
- 清理弹窗
- 社团领取
- 日常活动清体力（刷 BONUS 关卡，支持双倍体力）
- 共鸣屋每日刷新
- 多元裂缝
- 购买零时之种
- 使魔探险
- 每日每周任务奖励领取

---

## 常见问题

**Q：识别不到画面 / 点击错位？**
A：确认模拟器分辨率为 1280 × 720，且游戏画面无缩放（DPI 缩放 100%）。

**Q：双倍体力兑换后打的次数不对？**
A：请在 MFA 客户端刷新（⟳）后重新测试；`战斗次数` 指「总共打几场」，中途兑换体力不额外扣次数。

**Q：某些角色会弹窗导致识别失败？**
A：进地图涉及角色切换，如「菲米莉丝」这类会弹窗的角色，请在游戏内关掉弹窗。

---

## ⚠️ 免责声明

- 本项目仅供**学习交流**，使用可能违反游戏的服务条款，存在账号被处罚的风险。
- 请**自行承担使用风险**，作者不对因使用本项目导致的账号封禁、财产损失等任何后果负责。
- 本项目不涉及任何游戏破解、修改、注入，仅通过图像识别模拟人工点击。

---

## 致谢

- [MaaFramework](https://github.com/MaaXYZ/MaaFramework)（LGPL-3.0）—— 自动化框架
- [MFAAvalonia](https://github.com/MaaXYZ/MFAAvalonia)（GPL-3.0）—— 通用 GUI 客户端
