# 自訂詞彙表

`transcribe_groq.py` 會讀本檔，把各節的 `- ` 條目組成 Whisper 的 `--initial_prompt`
（「Whisper 常見誤判對照」與「使用方式」兩節會略過）；清字階段也拿本檔當錯字修正參考。

**加自己的詞彙就直接改這裡。** Whisper 的 prompt 上限約 224 token，
腳本抓 200 字為保守值，超過會從清單尾端截掉並印出警告——把最重要的詞放前面。

## AI 工具
- Claude
- Claude Code
- Anthropic
- ChatGPT
- OpenAI
- GPT Codex / GPT-Codex（OpenAI 的 agent 產品）
- Gemini
- Groq
- Whisper
- Typeless

## 開發工具
- GitHub
- Git
- Obsidian
- Firebase
- Python
- JavaScript
- HTML
- API key
- ffmpeg

## 教育相關
- 康軒
- 翰林
- 南一
- 段考
- 雙向細目表
- 會考
- 素養題

## Whisper 常見誤判對照

| Whisper 聽成 | 正確 |
|---|---|
| claw code / 克勞 code | Claude Code |
| 克勞德 | Claude |
| block / 巴洛克 | Groq |
| 威士帕 / whisper | Whisper |
| 傑米奈 / Gemini | Gemini |
| 泰普勒斯 | Typeless |
| 歐布西迪安 | Obsidian |
| 法亞貝斯 | Firebase |

## 使用方式

1. **Whisper 階段**：`transcribe_groq.py` 讀本檔自動組成 `--initial_prompt`
2. **清字階段**：Claude 讀本檔，遇到相近音的詞自動替換為正確名稱

> 上面「Whisper 常見誤判對照」是給清字階段看的**參考**，不會自動生效。
> 要讓它變成自動替換，得寫進 `replacements.md`（或你自己的 `~/.audio-to-srt/replacements.md`）。
