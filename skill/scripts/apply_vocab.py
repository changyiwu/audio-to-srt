#!/usr/bin/env python3
"""對 SRT 做機械式詞彙替換（只動文字行，時間碼與段號原封不動）。

規則放在 ../references/replacements.md，不寫死在程式裡：
  - 「保護詞」那節的 `- 條目` → 替換前遮蔽、跑完還原
  - 其餘表格的每一列 → 一條替換規則（第 1 欄=聽成、第 2 欄=正確、第 3 欄=邊界）
使用者自己的規則放 ~/.audio-to-srt/replacements.md，會先於內建規則執行。

需要 Python 3.9+。

用法：
  python apply_vocab.py <in.srt> --out <out.srt>
  python apply_vocab.py <in.srt> --out <out.srt> --rules my_rules.md
  python apply_vocab.py <in.srt> --out <out.srt> --no-user-rules
"""
import argparse
import re
import sys
from pathlib import Path

DEFAULT_RULES = Path(__file__).resolve().parent.parent / "references" / "replacements.md"
USER_RULES = Path.home() / ".audio-to-srt" / "replacements.md"

PROTECT_HEADING = "保護詞"
# 表格分隔列：|---|:---:|---|
SEPARATOR_RE = re.compile(r"^\|[\s:|-]+\|$")
# 「否」「no」「false」「n」都當成關閉邊界
BOUNDARY_OFF = {"否", "no", "false", "n", "off", "0"}

# 詞邊界：頭尾是英數字時，要求前後不是英數字。
# 中文沒有詞邊界可言，所以中文字頭尾不加守衛。
BOUNDARY_PREFIX = r"(?<![0-9A-Za-z])"
BOUNDARY_SUFFIX = r"(?![0-9A-Za-z])"


def _is_alnum_ascii(ch: str) -> bool:
    return ch.isascii() and ch.isalnum()


def compile_rule(frm: str, boundary: bool) -> "re.Pattern[str]":
    """把替換來源編成 regex，視情況加上詞邊界守衛。"""
    pattern = re.escape(frm)
    if boundary and frm:
        if _is_alnum_ascii(frm[0]):
            pattern = BOUNDARY_PREFIX + pattern
        if _is_alnum_ascii(frm[-1]):
            pattern = pattern + BOUNDARY_SUFFIX
    return re.compile(pattern)


def clean_cell(cell: str) -> str:
    """去掉表格儲存格的裝飾：外圍空白、`` ` `` 包覆，並還原跳脫的 `|`。"""
    cell = cell.strip()
    if len(cell) >= 2 and cell.startswith("`") and cell.endswith("`"):
        cell = cell[1:-1]        # 反引號內的空白保留
    return cell.replace(r"\|", "|")


def parse_rules(text: str, source: Path) -> tuple[list, list]:
    """解析 Markdown 規則檔。

    回傳 (protect_list, [(compiled_pattern, replacement, from_text), ...])。

    - `## 保護詞` 那節底下的 `- 條目` → 保護詞
    - 任何表格的資料列 → 替換規則（表頭列與分隔列會跳過）
    """
    protect, rules = [], []
    in_protect_section = False
    in_table = False

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()

        if line.startswith("#"):
            in_protect_section = PROTECT_HEADING in line.lstrip("#").strip()
            in_table = False
            continue

        if SEPARATOR_RE.match(line):
            in_table = True          # 上一列是表頭，從下一列開始收
            continue

        if not line.startswith("|"):
            in_table = False
            if in_protect_section and line.startswith("- "):
                term = clean_cell(line[2:])
                if term:
                    protect.append(term)
            continue

        if not in_table:
            continue                 # 表頭列，還沒遇到分隔列

        cells = [clean_cell(c) for c in line.strip("|").split("|")]
        if len(cells) < 2 or not cells[0]:
            continue                 # 空列或缺欄，跳過
        frm, to = cells[0], cells[1]
        boundary = True
        if len(cells) >= 3 and cells[2].strip().lower() in BOUNDARY_OFF:
            boundary = False
        if frm == to:
            print(f"[WARN] {source}:{lineno} 左右相同，這條沒有作用：{frm}")
            continue
        rules.append((compile_rule(frm, boundary), to, frm))

    if not rules:
        sys.exit(f"[ERR] {source} 沒有解析到任何替換規則，格式是不是壞了？")
    return protect, rules


def load_rules(rules_path: Path, use_user_rules: bool) -> tuple[list, list]:
    """載入內建規則，並把使用者規則排在前面（可覆蓋內建行為）。"""
    if not rules_path.exists():
        sys.exit(f"[ERR] 找不到規則檔：{rules_path}")
    protect, rules = parse_rules(rules_path.read_text(encoding="utf-8"), rules_path)

    if use_user_rules and USER_RULES.exists():
        u_protect, u_rules = parse_rules(
            USER_RULES.read_text(encoding="utf-8"), USER_RULES
        )
        protect = u_protect + protect
        rules = u_rules + rules       # 使用者規則先跑
        print(f"[INFO] 併入使用者規則 {USER_RULES}（{len(u_rules)} 條）")

    # 長的先遮蔽，避免短字串先吃掉長詞的一部分
    protect = sorted(set(protect), key=len, reverse=True)
    return protect, rules


def apply(text: str, protect: list, rules: list) -> str:
    """遮蔽保護詞 → 依序替換 → 還原保護詞。"""
    masked = {}
    for i, term in enumerate(protect):
        if term and term in text:
            token = f"\x00{i}\x00"
            masked[token] = term
            text = text.replace(term, token)

    for pattern, to, _frm in rules:
        # 用 lambda 回傳字面值，避免 replacement 裡的 \1 之類被當成反向參照
        text = pattern.sub(lambda _m, _to=to: _to, text)

    for token, term in masked.items():
        text = text.replace(token, term)
    return text


def process_srt(src: Path, dst: Path, protect: list, rules: list) -> None:
    content = src.read_text(encoding="utf-8-sig")
    blocks = re.split(r"(\r?\n\r?\n)", content)  # 保留分隔符
    out = []
    n_replaced = 0
    for seg in blocks:
        if not seg.strip() or seg.isspace() or "-->" not in seg:
            out.append(seg)
            continue
        lines = seg.splitlines(keepends=False)
        # 第 0 行段號、第 1 行時間碼 → 不動
        # 第 2 行起 → 清字
        if len(lines) < 3:
            out.append(seg)
            continue
        header = "\n".join(lines[:2])
        body_before = "\n".join(lines[2:])
        body_after = apply(body_before, protect, rules)
        if body_after != body_before:
            n_replaced += 1
        out.append(header + "\n" + body_after)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("".join(out), encoding="utf-8")
    print(f"[OK] 輸出 {dst}")
    print(f"     {n_replaced} 段有替換")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--rules", type=Path, default=DEFAULT_RULES,
                    help=f"替換規則 markdown（預設 {DEFAULT_RULES}）")
    ap.add_argument("--no-user-rules", action="store_true",
                    help=f"不要併入 {USER_RULES}")
    args = ap.parse_args()

    if not args.src.exists():
        sys.exit(f"[ERR] 找不到輸入檔：{args.src}")

    protect, rules = load_rules(args.rules, not args.no_user_rules)
    print(f"[INFO] 規則 {len(rules)} 條，保護詞 {len(protect)} 個")
    process_srt(args.src, args.out, protect, rules)
    return 0


if __name__ == "__main__":
    sys.exit(main())
