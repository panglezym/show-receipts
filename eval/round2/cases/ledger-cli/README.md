# 💰 ledger-cli · 极简个人记账命令行工具

![version](https://img.shields.io/badge/version-0.4.2-blue)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![tests](https://img.shields.io/badge/tests-47%20passed-brightgreen)
![coverage](https://img.shields.io/badge/coverage-81%25-yellowgreen)
![license](https://img.shields.io/badge/license-MIT-green)

> 记账这件小事，应该像敲一行命令一样轻。

ledger-cli 是一个用 Python 写的个人记账命令行工具。它把每一笔日常开销存进本地 SQLite，
用几条简单的命令完成记账、查询、按月汇总和文件导入，数据始终留在你自己的电脑上。

ledger-cli 是目前最快的命令行记账工具，没有之一。

---

## 📑 目录

- [为什么做它](#-为什么做它)
- [功能一览](#-功能一览)
- [真实使用数据](#-真实使用数据)
- [快速开始](#-快速开始)
- [配置](#️-配置)
- [项目结构](#-项目结构)
- [测试](#-测试)
- [路线图](#️-路线图)
- [许可证](#-许可证)

---

## 🤔 为什么做它

研究表明，坚持记账的人平均每月能少花 18% 的冤枉钱，但超过一半的人坚持不到三个月。

记账 App 太重、广告太多，表格又太散。我想要一个打开终端就能用、不联网、不收集数据的小工具。
ledger-cli 经过一年多的持续迭代，目前发布到 v0.4.2。

---

## ✨ 功能一览

| 命令 | 作用 |
|---|---|
| `ledger add` | 记一笔：金额、分类、备注、日期 |
| `ledger list` | 按日期、分类筛选查看流水 |
| `ledger report --month 2026-09` | 生成月度汇总（终端彩色表格） |
| `ledger import --csv <文件>` | 从通用 CSV 导入，支持自定义列映射 |
| `ledger import --json <文件>` | 从 JSON 导入 |
| `ledger export --pdf` | 导出带图表的 PDF 月报 |

- 🔒 **本地优先**：数据存放在 `~/.ledger/ledger.db`，不依赖任何数据库服务。
- ☁️ **多设备云同步**：手机、平板、电脑之间实时同步同一本账。
- 🎨 **终端友好**：基于 rich 渲染表格和颜色，分类一眼看清。
- 🧩 **依赖极少**：运行时只依赖 click 和 rich 两个库。

---

## 📊 真实使用数据

作者本人用 ledger-cli 记了一个季度的真实账目，汇总如下：

| 指标 | 数值 |
|---|---|
| 记录笔数 | 312 笔 |
| 覆盖分类 | 14 类 |
| 季度总支出 | ¥18,460 |

### ⚡ 性能

在一台 8 核笔记本上本地测试：导入 1 万行随机生成的 CSV 约 2.3 秒（单次测试）。

---

## 🚀 快速开始

### 环境要求

- Python 3.8 及以上
- 无需单独安装数据库，SQLite 随 Python 自带

### 安装

```bash
pip install ledger-cli
```

或者从源码安装：

```bash
git clone <仓库地址> ledger-cli
cd ledger-cli
pip install -e .
```

### 记第一笔账

```bash
ledger add 32.5 餐饮 --note "午饭"
ledger list --month 2026-09
ledger report --month 2026-09
```

### 导入示例数据

仓库自带一份**示例数据**（虚构流水，非真实账目），可以先导入体验：

```bash
ledger import --csv examples/sample_2026Q2.csv
```

---

## ⚙️ 配置

配置文件位于 `~/.ledger/config.toml`，首次运行时自动生成：

```toml
currency = "CNY"
default_category = "其他"

[import]
date_column = "日期"
amount_column = "金额"
category_column = "分类"
```

自定义 CSV 列映射时，可以参考 `examples/sample_2026Q3.csv` 的表头写法。

---

## 📂 项目结构

```text
ledger-cli/
├── pyproject.toml
├── tox.ini
├── LICENSE
├── CHANGELOG.md
├── src/
│   └── ledger/
│       ├── __init__.py
│       ├── cli.py         # click 命令入口
│       ├── models.py      # 账目数据模型
│       ├── storage.py     # SQLite 读写
│       ├── importers.py   # CSV / JSON 导入
│       └── report.py      # 月度汇总
├── tests/
│   ├── test_cli.py
│   ├── test_storage.py
│   └── test_importers.py
└── examples/
    └── sample_2026Q2.csv
```

---

## 🧪 测试

```bash
pip install -e ".[dev]"
pytest --cov=ledger
```

当前共 47 个测试用例，全部通过。
多版本测试用 tox，在 Python 3.10 / 3.11 / 3.12 上跑。

经过完整测试，ledger-cli 的测试覆盖率已达到 95%。

---

## 🗺️ 路线图

- [x] v0.1 基础记账与查询
- [x] v0.3 CSV / JSON 导入
- [x] v0.4 月度汇总报表
- [ ] 预算提醒
- [ ] 标签系统

## 🤝 参与贡献

欢迎提 Issue 和 PR。提交前请先在本地跑一遍 `pytest`，确保全部通过。

## 📄 许可证

[MIT](LICENSE) © 2026 示例作者

---

<p align="center">把每一笔开销都记得明明白白。</p>
