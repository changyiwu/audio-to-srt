#!/usr/bin/env python3
"""對 SRT 做機械式詞彙替換（只動文字行，時間碼與段號原封不動）。

替換清單內建於此腳本（日後可外移成 JSON）。
用法：
  python apply_vocab.py <in.srt> --out <out.srt>
"""
import argparse
import re
import sys
from pathlib import Path

# 順序重要：先替換長詞，避免短詞先吃掉
REPLACEMENTS = [
    # GPT Codex（必須在 Cloud→Claude 之前處理，避免「Cloud X」「Claude X」誤判）
    ("GPT-ClaudeX", "GPT-Codex"),
    ("GPT ClaudeX", "GPT Codex"),
    ("GPT-CloudX", "GPT-Codex"),
    ("GPT CloudX", "GPT Codex"),
    ("GPT-Cloud X", "GPT-Codex"),
    ("GPT Cloud X", "GPT Codex"),
    ("ClaudeX", "Codex"),
    ("CloudX", "Codex"),
    ("Cloud X", "Codex"),
    ("Claude X", "Codex"),
    ("CodeX", "Codex"),
    ("Code X", "Codex"),
    ("DexDex", "Codex"),
    ("Dex Dex", "Codex"),
    ("dex dex", "Codex"),
    ("Code x", "Codex"),
    ("code x", "Codex"),
    # Antigravity（Google AI IDE）
    ("Anti-Gravity", "Antigravity"),
    ("Anti Gravity", "Antigravity"),
    ("AntiGravity", "Antigravity"),
    ("Antiquity", "Antigravity"),
    ("Antiguity", "Antigravity"),
    ("Antiqueity", "Antigravity"),
    ("anti-gravity", "Antigravity"),
    ("Antigrate ID", "Antigravity IDE"),
    ("AntiGraphy2", "Antigravity 2"),
    ("AntiGraphy 2", "Antigravity 2"),
    ("AntiGraphy", "Antigravity"),
    ("Antigrate", "Antigravity"),
    ("Antigrity", "Antigravity"),
    ("Antigua提", "Antigravity 提"),
    ("安定iquity", "Antigravity"),
    # 部署/工具專有名詞（三師爸研習常用）
    ("Netify", "Netlify"),
    ("Netfly", "Netlify"),
    ("Netfile", "Netlify"),
    ("Netflix", "Netlify"),
    ("NetFi", "Netlify"),
    ("Pellet", "Padlet"),
    ("Pell et", "Padlet"),
    ("Paylet", "Padlet"),
    ("Google She et", "Google Sheet"),
    ("Google Shirt", "Google Sheet"),
    ("Google size", "Google Sites"),
    ("Cla.S.P", "clasp"),
    ("Cla.S", "clasp"),
    ("DLSP", "clasp"),
    ("CLSP", "clasp"),
    ("Clasp", "clasp"),
    ("AppSquid", "Apps Script"),
    ("Appsquiz", "Apps Script"),
    ("App ScriptAppSquid", "Apps Script"),
    ("Assess Token", "Access Token"),
    ("aging setting", "Agent Settings"),
    ("Aging Settings", "Agent Settings"),
    ("Agin Setting", "Agent Settings"),
    ("Agen setting", "Agent Settings"),
    ("bookLM的MCP", "NotebookLM 的 MCP"),
    ("生徒技能", "生圖技能"),
    ("生徒", "生圖"),
    ("第二大堂", "第二大腦"),
    ("詹音", "噪音"),
    ("栏位", "欄位"),
    ("四傳表", "試算表"),
    # OpenCode 系列
    ("OpenGo", "OpenCode Go"),
    ("Open Go", "OpenCode Go"),
    ("路板", "陸版"),
    ("Sense4AI", "生成式AI"),
    ("Sense 4 AI", "生成式AI"),
    ("克勞德X", "Codex"),
    ("克勞X", "Codex"),
    # Claude 生態
    ("ClockCode", "Claude Code"),
    ("Clock Code", "Claude Code"),
    ("Cloud Code", "Claude Code"),
    ("cloud code", "Claude Code"),
    ("CloudCode", "Claude Code"),
    ("ClawCode", "Claude Code"),
    ("claw code", "Claude Code"),
    ("Claw code", "Claude Code"),
    ("Cloud design", "Claude Design"),
    ("cloud design", "Claude Design"),
    ("Cloud Design", "Claude Design"),
    ("克勞德", "Claude"),
    ("克勞", "Claude"),
    # 注意：Cloud 單字替換放後面（避免先動到 Cloud Code）
    ("Cloud", "Claude"),
    ("cloud", "Claude"),
    # 其他 AI 工具
    ("Notebook AM", "NotebookLM"),
    ("notebook AM", "NotebookLM"),
    ("Notebook LM", "NotebookLM"),
    ("notebook LM", "NotebookLM"),
    ("NotebookAM", "NotebookLM"),
    ("notebookLM", "NotebookLM"),
    ("ImageR", "Image 2"),
    ("Image R", "Image 2"),
    ("GPT Image 2", "GPT-Image 2"),
    ("GPT-Image2", "GPT-Image 2"),
    # 錯字
    ("斷考", "段考"),
    ("Signard型", "三角形"),
    ("Signard 型", "三角形"),
    ("翻例", "範例"),
    ("原始黑體", "思源黑體"),
    ("烤卷", "考卷"),
    ("三十八", "三師爸"),
    ("宋瑞玮", "宋睿瑋"),
    ("小課", "小克"),
    ("用字按鈕", "用一個按鈕"),
    ("五文字", "無文字"),
    ("全然登地", "飛天遁地"),
    ("飛天遁地啊", "飛天遁地"),
    ("生成師", "生成式"),
    ("進乎無限", "近乎無限"),
    ("進乎", "近乎"),
]


def apply(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def process_srt(src: Path, dst: Path) -> None:
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
        body_after = apply(body_before)
        if body_after != body_before:
            n_replaced += 1
        out.append(header + "\n" + body_after)
    dst.write_text("".join(out), encoding="utf-8")
    print(f"[OK] 輸出 {dst}")
    print(f"     {n_replaced} 段有替換")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    process_srt(args.src, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
