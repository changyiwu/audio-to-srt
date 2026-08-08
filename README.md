# 🎬 audio-to-srt — 音訊/影片自動生成乾淨 SRT 字幕

> 把上課錄音、教學影片丟給 AI Agent，自動產出**時間碼精準、贅字清乾淨**的 SRT 字幕檔。
> 預設走 Groq Whisper（雲端、免費額度、word-level 時間碼），無金鑰時備援本地 Whisper。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 這是什麼

一個給 Claude Code / OpenCode / Codex 等 AI Agent 用的字幕技能：

| 步驟 | 內容 |
|------|------|
| 1. 轉檔 | 影片自動抽音軌（ffmpeg） |
| 2. 轉錄 | Groq `whisper-large-v3-turbo`（word-level 時間碼）；無金鑰則本地 Whisper medium |
| 3. 清字 | AI 逐段移除語助詞、修同音錯字、統一術語（規則在 `skill/references/`） |
| 4. 驗證 | 腳本檢查時間碼對齊與格式（`skill/scripts/validate_srt.py`） |

## 安裝方式

**Claude Code**（下載 ZIP 或 clone 後）：
```powershell
# 把 skill/ 的內容複製到技能資料夾
Copy-Item -Recurse skill "$env:USERPROFILE\.claude\skills\audio-to-srt"
```

**OpenCode**：目標改為 `~/.config/opencode/skills/audio-to-srt`。

## 需求

- **ffmpeg**：`winget install Gyan.FFmpeg`
- **Groq API Key（建議，免費）**：到 [console.groq.com](https://console.groq.com) 註冊取得，
  存成環境變數 `GROQ_API_KEY` 或寫入 `~/.groq_api_key` 檔
- 沒有 key 也能用：會改走本地 Whisper（較慢，需要 `pip install openai-whisper`）

## 怎麼觸發

對你的 Agent 說：「把這個錄音轉字幕」「幫這支影片做 SRT」「語音轉文字加時間碼」。

## 授權

MIT — 歡迎老師們自由使用與改作。
