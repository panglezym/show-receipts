#!/usr/bin/env python3
"""show-receipts 机械检查：脚本能确定的事不交给模型猜。

用法：
  python3 check.py DOC.md --root 仓库目录      # 用真实目录当文件清单
  python3 check.py DOC.md --tree 文件清单.txt  # 每行一个相对路径（git ls-files 的输出就行）
  python3 check.py DOC.md --root . --json      # 输出 JSON，给模型接着判

查三样：
  1. 路径：行内代码、目录树、相对链接、命令依赖的文件、许可证。找不到就记「无据」。
  2. 信号词：演示数据、没有出处、往大里说、能力越界四类的可疑说法。只列候选，判不判由模型和人决定。
  3. 前后数字：同一个「数字＋量词＋名词」在文中出现了不同的数，列出来供核对。

退出码：有「无据」的路径时为 1，否则为 0。只用 Python 标准库。
"""
import argparse, json, os, re, sys
from urllib.parse import unquote

# ---------- 文件清单 ----------

def load_tree(root=None, tree=None):
    files = set()
    if tree:
        for line in open(tree, encoding="utf-8"):
            p = line.strip().strip('"')
            if p:
                files.add(p.lstrip("./"))
    elif root:
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if x not in (".git", "node_modules", "__pycache__")]
            for f in fs:
                files.add(os.path.relpath(os.path.join(d, f), root))
    dirs = set()
    for f in files:
        parts = f.split("/")
        for i in range(1, len(parts)):
            dirs.add("/".join(parts[:i]))
    return files, dirs


def exists(path, files, dirs):
    p = path.strip().lstrip("./").rstrip("/")
    if not p:
        return True
    if p in files or p in dirs:
        return True
    base = p.split("/")[-1]
    # 目录树里常只写文件名，不写完整路径：按文件名或目录名在任意层级找
    return any(f.split("/")[-1] == base for f in files) or any(d.split("/")[-1] == base for d in dirs)


# ---------- 拆文档 ----------

def parse(doc):
    """返回 [(行号, 文本, 是否在代码块里, 所在小节)]。小节写成「标题｜加粗小标题」，没有小标题就只有标题。"""
    out, in_code, heading, label = [], False, "", ""
    for i, line in enumerate(open(doc, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            if re.match(r"#{1,6}\s", line):
                heading, label = line.lstrip("#").strip(), ""
            else:
                m = re.match(r"^\s*\*\*(.+?)\*\*[:：]?\s*$", line)
                if m:
                    label = m.group(1).strip()
        out.append((i, line, in_code, heading + ("｜" + label if label else "")))
    return out


EXT = r"(?:html?|md|pdf|docx?|pptx?|xlsx?|csv|json|ya?ml|toml|py|js|ts|tsx|jsx|css|sh|txt|png|jpe?g|gif|svg|ipynb|env(?:\.example)?)"
PATHLIKE = re.compile(rf"^[\w一-鿿.\-/@ ]+(?:/|\.{EXT})$", re.I)
TREE_LINE = re.compile(r"^[\s│|]*[├└]──\s*(.+?)\s*(?:#.*)?$")
NAME = re.compile(r"^[\w一-鿿.\-@+]+/?$")              # 目录树里的一项：一个不带空格的名字
BARE_LINE = re.compile(rf"^\s*([\w一-鿿.\-/@+]+\.{EXT})\s*(?:#.*)?$", re.I)   # 代码块里单独一行的文件名
BARE_FILE = re.compile(r"(?<![\w/.\-])([\w一-鿿\-.]+\.(?:pdf|docx?|pptx?|xlsx?|html?|md|csv|ipynb))(?![\w])", re.I)
MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
INLINE = re.compile(r"`([^`]+)`")
SKIP_SECTION = re.compile(r"roadmap|规划|计划|二期|后续|future|todo", re.I)
CURRENT = re.compile(r"当前|现在|已完成|已上线|MVP|current|done|shipped", re.I)
DONE_ITEM = re.compile(r"^\s*[-*]\s*\[x\]", re.I)


def in_plan(section, text=""):
    """这一行是不是在说计划。打了 [x] 的条目、写着「当前」的小标题下面，都是在说已经做到的事。"""
    if DONE_ITEM.match(text):
        return False
    if not SKIP_SECTION.search(section):
        return False
    label = section.split("｜", 1)[1] if "｜" in section else ""
    return not (label and CURRENT.search(label))


def find_paths(lines, files, dirs):
    hits = []

    def add(n, path, how):
        if not exists(path, files, dirs):
            hits.append({"line": n, "path": path, "how": how})

    for n, text, in_code, section in lines:
        if in_code:
            m = TREE_LINE.match(text)
            if m:
                name = m.group(1).strip()
                if NAME.match(name) and name not in (".", ".."):
                    add(n, name, "目录树")
                continue
            m = BARE_LINE.match(text)
            if m:
                add(n, m.group(1), "代码块里的文件名")
                continue
            for cmd, dep in ((r"\b(?:npm|yarn|pnpm)\s+(?:install|i|run|ci)\b", "package.json"),
                             (r"\bpip3?\s+install\s+-r\s+(\S+)", None),
                             (r"\bcp\s+(\S+)\s+\S+", None),
                             (r"\bpython3?\s+(\S+\.py)\b", None)):
                mm = re.search(cmd, text)
                if mm:
                    add(n, dep or mm.group(1), f"命令依赖（{text.strip()[:40]}）")
            continue
        plain = INLINE.sub(" ", MD_LINK.sub(" ", text))
        for name in BARE_FILE.findall(plain):
            if not re.match(r"^https?:", name) and not in_plan(section, text):
                add(n, name, "正文里的文件名")
        for link in MD_LINK.findall(text):
            if re.match(r"^(https?:|mailto:|#|\.$)", link):
                continue
            add(n, unquote(link.split("#")[0]), "相对链接")
        for code in INLINE.findall(text):
            c = code.strip()
            if " " in c and not re.search(r"[一-鿿]", c):
                continue  # 带空格的英文多半是命令或代码片段，不是路径
            if c.startswith(("http", "--")) or "=" in c or "(" in c:
                continue
            if PATHLIKE.match(c) and not in_plan(section, text):
                add(n, c, "行内代码")
    # 许可证：文中声称了，仓库里却没有 LICENSE 文件
    claims = [n for n, t, c, s in lines
              if not c and not re.match(r"\s*#", t)
              and (re.search(r"\b(?:MIT|Apache|GPL|BSD|MPL)\b", t, re.I) or re.search(r"\bLICENSE\b", t))]
    if claims and not any(re.match(r"(?i)licen[cs]e", f.split("/")[-1]) for f in files):
        hits.append({"line": claims[0], "path": "LICENSE", "how": f"声称了许可证（第 {', '.join(map(str, claims))} 行），仓库里没有 LICENSE 文件"})
    return hits


# ---------- 信号词 ----------

SIGNALS = {
    "演示数据冒充实测": r"^\s*[-*]\s*\[x\]|当前值|实测|已上线|MVP\s*上线|上线|用户规模|日活|月活|✅\s*达标|达标|累计服务|in production|currently|\blive\b|\busers\b",
    "数字和引用没有出处": r"据统计|统计显示|研究表明|调研显示|数据显示|行业均值|行业平均|超过\s*\d+\s*%|according to|studies show",
    "往大里说": r"首个|首款|唯一|领先|全面|彻底|零误差|100\s*%|所有|近百|数十|上千|多年|\bfirst\b|\bonly\b|leading|\bzero\b",
    "能力越界": r"支持|兼容|已接入|接入|对接|集成|实时|自动|\bsupports?\b|integrat|real-?time",
}


def find_signals(lines):
    out = []
    for n, text, in_code, section in lines:
        if in_code or not text.strip():
            continue
        for cat, pat in SIGNALS.items():
            words = sorted(set(m.group(0) for m in re.finditer(pat, text, re.I)))
            if words:
                out.append({"line": n, "category": cat, "words": words,
                            "section": section, "in_plan_section": in_plan(section, text),
                            "text": text.strip()[:120]})
    return out


# ---------- 前后数字 ----------

COUNT = re.compile(r"(\d+(?:\.\d+)?)\s*(个|页|屏|条|张|项|种|类|位|家|款|端|章|节|步|层|大)\s*([一-鿿A-Za-z]{1,4})")


def find_numbers(lines):
    groups = {}
    for n, text, in_code, section in lines:
        if in_code or in_plan(section, text):
            continue
        for num, unit, noun in COUNT.findall(text):
            groups.setdefault(unit + noun, []).append({"line": n, "value": num})
    out = []
    for key, occ in groups.items():
        vals = sorted(set(o["value"] for o in occ), key=float)
        if len(vals) > 1:
            out.append({"key": key, "values": vals, "occurrences": occ})
    return out


# ---------- 输出 ----------

def report_md(doc, nfiles, paths, signals, numbers):
    L = [f"# show-receipts 机械检查", "", f"文档：`{os.path.basename(doc)}` · 文件清单 {nfiles} 个", ""]
    L += [f"## 无据：找不到的路径和文件（{len(paths)}）", ""]
    items, i = [], 0
    while i < len(paths):
        h = paths[i]
        if h["how"] == "目录树":  # 连续的目录树项合成一条，免得刷屏
            j = i
            while j + 1 < len(paths) and paths[j + 1]["how"] == "目录树" and paths[j + 1]["line"] - paths[j]["line"] <= 2:
                j += 1
            names = [p["path"] for p in paths[i:j + 1]]
            span = f"第 {h['line']} 行" if j == i else f"第 {h['line']}–{paths[j]['line']} 行"
            items.append(f"- {span}：目录树里有 {len(names)} 项不存在：" + "、".join(f"`{x}`" for x in names))
            i = j + 1
        else:
            items.append(f"- 第 {h['line']} 行 `{h['path']}`：{h['how']}")
            i += 1
    L += items or ["- 无"]
    L += ["", f"## 待核：信号词（{len(signals)} 处）", "", "只是候选，要逐条对照材料判档。标了「规划段」的通常是在说计划，可以放过。", ""]
    by = {}
    for s in signals:
        by.setdefault(s["category"], []).append(s)
    for cat, items in by.items():
        L.append(f"### {cat}（{len(items)}）")
        L += [f"- 第 {s['line']} 行「{'、'.join(s['words'])}」{'（规划段）' if s['in_plan_section'] else ''}：{s['text']}" for s in items]
        L.append("")
    L += [f"## 待核：前后数字（{len(numbers)} 组）", ""]
    L += [f"- 「{g['key']}」出现了 {'、'.join(g['values'])}：" + "，".join(f"第 {o['line']} 行是 {o['value']}" for o in g["occurrences"]) for g in numbers] or ["- 无"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--root")
    g.add_argument("--tree")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    files, dirs = load_tree(a.root, a.tree)
    if a.root:  # 文档里提到仓库自己的目录名不算缺失
        dirs.add(os.path.basename(os.path.abspath(a.root)))
    lines = parse(a.doc)
    paths, signals, numbers = find_paths(lines, files, dirs), find_signals(lines), find_numbers(lines)
    if a.json:
        print(json.dumps({"doc": a.doc, "files": len(files), "missing_paths": paths,
                          "signals": signals, "number_conflicts": numbers}, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(report_md(a.doc, len(files), paths, signals, numbers))
    sys.exit(1 if paths else 0)


if __name__ == "__main__":
    main()
