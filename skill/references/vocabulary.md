# 自訂詞彙表

給 Whisper `--initial_prompt` 使用，也作為清字階段的錯字修正參考。

## 頻道/人物
- 三師爸
- Sense Bar

## AI 工具
- Claude
- Claude Code
- Claude Code Desktop
- Claude.ai
- Anthropic
- ChatGPT
- OpenAI
- GPT Codex / GPT-Codex（OpenAI 的 agent 產品）
- Gemini
- NotebookLM
- Groq
- Whisper
- Typeless
- VoiceType
- NoType

## 開發工具
- GitHub
- Git
- Obsidian
- Firebase
- Supabase
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
| notebook LM | NotebookLM |
| 泰普勒斯 | Typeless |
| 沃伊斯泰普 | VoiceType |
| 諾泰普 | NoType |
| 歐布西迪安 | Obsidian |
| 法亞貝斯 | Firebase |

## 使用方式

1. **Whisper 階段**：由 skill 自動組裝成 `--initial_prompt` 字串
2. **清字階段**：Claude 讀本檔，遇到相近音的詞自動替換為正確名稱
