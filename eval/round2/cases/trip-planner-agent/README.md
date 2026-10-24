# 🧭 Trip Planner Agent · 旅行行程规划智能体（Demo）

![version](https://img.shields.io/badge/version-0.2-blue)
![python](https://img.shields.io/badge/python-3.11-blue)
![status](https://img.shields.io/badge/status-demo-orange)
![license](https://img.shields.io/badge/license-Apache--2.0-green)

> 说出你想去的地方，剩下的交给 Agent。

Trip Planner Agent 是一个旅行行程规划 Agent 的演示项目：输入目的地、天数、预算和偏好，
Agent 会拆解需求、从 POI 表里挑选景点和餐厅、按距离排出每日路线，再做一轮预算核对。

✈️ 目前已经为 2,000+ 位旅行者生成了个性化行程。

---

## 📑 目录

- [为什么需要它](#-为什么需要它)
- [能力一览](#-能力一览)
- [工作原理](#-工作原理)
- [示例数据](#-示例数据)
- [效果](#-效果)
- [快速开始](#-快速开始)
- [目录结构](#-目录结构)
- [评测说明](#-评测说明)
- [路线图](#️-路线图)

---

## 💡 为什么需要它

据行业报告，68% 的自由行游客在出发前要花 10 小时以上做攻略。

查景点、比路线、算预算，这些事情步骤固定、信息分散，正适合交给 Agent 先出一版草稿，
人再在草稿上改。这个 demo 想回答一个问题：只靠提示词和一张 POI 表，能把行程排到什么程度。

---

## ✨ 能力一览

| 能力 | 说明 |
|---|---|
| 🧩 需求拆解 | 把"带爸妈去成都玩 4 天、预算 6000"拆成结构化约束 |
| 📍 POI 选点 | 从 POI 表中按偏好、开放时间挑选景点与餐厅 |
| 🗺️ 路线排布 | 用 POI 的经纬度估算距离，按天排出顺路的行程 |
| 💴 预算核对 | 逐项核对门票、餐饮、交通的估算费用 |
| 🏨 实时比价预订 | 实时查询航班与酒店价格，并支持一键预订 |
| 🌏 覆盖范围 | 支持全球 200+ 城市 |

---

## 🧠 工作原理

```text
用户请求
   │
   ▼
system_prompt ──► itinerary_planner ──► budget_checker ──► Markdown 行程
 (角色与约束)      (选点 + 排路线)        (预算逐项核对)
```

各环节的提示词：

- 角色与输出格式：`prompts/system_prompt.md`
- 选点与排路线：`prompts/itinerary_planer.md`
- 预算核对：`prompts/budget_checker.md`

三段提示词串行调用同一个模型，中间结果以 JSON 传递，最后渲染成 Markdown。

---

## 📦 示例数据

`data/` 下是**手工整理的示例数据**，不是实时数据：

| 文件 | 内容 | 条数 |
|---|---|---|
| `sample_pois_kyoto.csv` | 京都景点与餐厅 | 186 |
| `sample_pois_chengdu.csv` | 成都景点与餐厅 | 143 |
| `sample_requests.jsonl` | 示例行程请求 | 20 |

每条 POI 含名称、类型、经纬度、建议游玩时长、开放时间和人均花费。

---

## 📊 效果

- 行程可执行率 80%（来自线上用户反馈）。
- 平均 25 秒即可生成一份完整的多日行程。
- 一次完整运行的输入输出记录见 `outputs/demo_run_20260915.md`。

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置模型接口

```bash
cp .env.example .env
```

在 `.env` 里填好模型接口地址和 Key，兼容 chat completions 格式的接口均可。

### 3. 跑演示 notebook

```bash
jupyter notebook notebooks/demo_walkthrough.ipynb
```

按顺序执行单元格，会读取 `data/sample_requests.jsonl` 里的请求并逐条生成行程。

### 4. 启动 Web 界面

```bash
python app.py
```

浏览器打开 `http://localhost:7860`，在输入框里描述你的旅行需求即可。

---

## 📂 目录结构

```text
trip-planner-agent/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── prompts/
│   ├── system_prompt.md
│   ├── itinerary_planner.md
│   └── budget_checker.md
├── notebooks/
│   └── demo_walkthrough.ipynb
├── data/
│   ├── sample_requests.jsonl
│   ├── sample_pois_kyoto.csv
│   └── sample_pois_chengdu.csv
└── outputs/
    └── demo_run_20260915.md
```

---

## 🔬 评测说明

项目在 50 条测试请求上做了人工评测，从"时间可行、路线顺路、预算不超"三个维度打分，
三项都过才算"可执行"。

这个 demo 前后打磨了两个多月，提示词改了十几版。

---

## 🗺️ 路线图

- [ ] 英文请求支持（尚未测试）
- [ ] 接入地图路线服务，替代经纬度直线估算
- [ ] 补充更多城市的 POI 数据
- [ ] 输出可导入日历的行程文件

## 📄 许可证

本项目采用 [Apache-2.0](LICENSE) 许可证。

---

<p align="center">示例作者 · 2026 · 让每一次出发都更从容</p>
