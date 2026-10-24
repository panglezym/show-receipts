---
name: show-receipts
description: >
  Audit a document before it goes out — README, proposal, report, product intro, résumé bullets —
  for claims the author's own materials can't back up: demo numbers presented as real results,
  files / commands / features that don't exist, numbers with no source, inflated wording,
  capabilities with no evidence, and figures that contradict each other. Checks every claim
  against the evidence the user provides (repo files, source docs, data), works offline, and
  returns a verdict per claim (backed / unverified / unsupported) plus a toned-down rewrite.
  Use when the user says "check this before I publish", "is anything here made up",
  "do these numbers hold up", or when an AI-drafted document is about to be shared.
  中文触发：发之前帮我查一下、有没有瞎写的、这些数字站得住吗、诚实度检查、核一下 README、拿出证据。
metadata:
  author: 赵永明
  version: 0.1.0
---

# show-receipts · 拿出证据

文档发出去之前，先对一遍账：每个数字、每个「已上线」、每个文件名，都要在作者手里的材料里找得到出处。

这个 skill 只核对**事实层**：说法和证据对不对得上。它不评价文笔，不改语气，也不替作者编新的事实。

## 第 0 步：先拿到证据

核对之前，先确认手里有什么材料：

- **仓库**：文档描述的代码仓库或文件夹，用来查路径、命令、文件。
- **底稿**：PRD、数据表、调研记录、会议纪要，用来查数字和能力。
- **作者的说明**：哪些是原型、哪些是示例数据、哪些是计划。

用户没给材料，就先问一句。如果对方说没有，照样做，但要在报告开头写明：「没有材料可核，以下多数判为存疑」。不要假装核过。

## 流程

1. **先跑脚本**。文档描述的是一个仓库，就跑：

   ```bash
   python3 scripts/check.py <文档> --root <仓库目录>
   ```

   拿不到目录、只有文件清单时，改用 `--tree <清单文件>`。脚本报出的「找不到的路径」默认算无据；只有一种例外：文档明确说了这个路径在仓库外，比如要另外克隆的仓库、读者自己建的文件，这时改判存疑，并写明理由。脚本列出的信号词和前后数字只是候选，进入第 3 步逐条判。

2. **拆主张**。把文档拆成一条条可以核对的说法：数字、状态（已上线、支持、实测）、文件和命令、引用、比较级和最高级。口号、愿景句、纯观点跳过。

3. **逐条找证据、判档**。六类问题的判定细则见 `references/categories.md`，判档只有三档：
   - **有据**：找到了出处，写明文件和行号。
   - **存疑**：材料里找不到，也找不到反证。不联网时，外部事实一律归这一档。
   - **无据**：材料里有反证；或者说的是作者自己的东西，材料里本该有却找不到。

   拿不准就判存疑，不判无据。

4. **给改写**。按 `references/rewrites.md` 降档改写，能降档就不删。每条都写成「原文 → 改成」，由作者决定改不改。

5. **按下面的格式出报告**。

## 报告格式

```markdown
## 结论
可以发／改完再发：无据 N 条，存疑 M 条。（没有材料时在这里写明）

## 必须改（无据）
| # | 位置 | 原文 | 类别 | 证据 | 建议改成 |

## 建议核一下（存疑）
| # | 位置 | 原文 | 类别 | 缺什么证据 | 建议改成 |

## 有据（K 条）
默认只写条数；用户要看时再逐条列出。
```

位置写「第 N 行」；文档没有行号时，写所在小节加原文开头几个字。

## 边界

- 不联网核外部事实。用户明确要求、并且环境能联网时才去查，查到的出处要写进证据栏。
- 不改原文。用户说「直接改」再改，改完重跑一遍第 1 步。
- 不判断好坏。「这个指标定得太低」不归这个 skill 管；它只管「这个指标是不是真的测出来的」。
- 一次报太多会被嫌烦：默认只展开无据和高置信的存疑，其余写个条数就行。
