# 🎬 audio-to-srt — 音訊/影片自動生成乾淨 SRT 字幕

> 把上課錄音、教學影片丟給 AI Agent，自動產出**時間碼精準、贅字清乾淨**的 SRT 字幕檔。
> 預設走 Groq Whisper（雲端、免費額度、word-level 時間碼），無金鑰時備援本地 Whisper。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 這是什麼

一個給 Claude Code / OpenCode / Codex 等 AI Agent 用的字幕技能：

| 步驟 | 內容 |
|------|------|
| 1. 轉檔 | 影片自動抽音軌；超過 24 MB 自動降取樣（ffmpeg） |
| 2. 轉錄 | Groq `whisper-large-v3-turbo`（word-level 時間碼）；無金鑰則本地 Whisper medium |
| 3. 斷句 | 依字級時間碼重新切段，並在真正的靜音處留白 |
| 4. 清字 | 先機械替換術語，再由 AI 逐段修錯字、刪贅詞（規則在 `skill/references/`） |
| 5. 驗證 | 腳本檢查段數、時間碼對齊與格式（`skill/scripts/validate_srt.py`） |
| 6. 產出 | `.srt` 字幕檔 ＋ `.txt` 純文字稿（可直接當影片描述或貼文） |

## 安裝方式

**Claude Code**（下載 ZIP 或 clone 後，在專案根目錄執行）：

**Windows（PowerShell）**
```powershell
Copy-Item -Recurse -Force skill\* "$env:USERPROFILE\.claude\skills\audio-to-srt\"
```

**macOS / Linux**
```bash
mkdir -p ~/.claude/skills/audio-to-srt && cp -R skill/. ~/.claude/skills/audio-to-srt/
```

> 注意結尾的 `skill\*` 與 `\`：要複製的是 `skill/` 的**內容**。
> 寫成 `Copy-Item -Recurse skill "...\audio-to-srt"` 在目標資料夾已存在時，
> 會變成巢狀的 `audio-to-srt\skill\`，技能就讀不到了。

**OpenCode**：目標改為 `~/.config/opencode/skills/audio-to-srt`。

## 需求

- **Python 3.9 以上**（腳本用到 `tuple[...]` 型別註記；不需要任何第三方套件）
- **ffmpeg**：Windows `winget install Gyan.FFmpeg`，macOS `brew install ffmpeg`
- **Groq API Key（建議，免費）**：到 [console.groq.com](https://console.groq.com) 註冊取得，
  存成環境變數 `GROQ_API_KEY` 或寫入 `~/.groq_api_key` 檔
- 沒有 key 也能用：會改走本地 Whisper（較慢，需要 `pip install openai-whisper`）

## 自訂成你自己的詞彙

兩個檔案，都不需要改程式：

| 想做的事 | 改哪裡 |
|---------|--------|
| 讓 Whisper 認得你的專有名詞 | `skill/references/vocabulary.md`（會自動組成 initial prompt） |
| 固定把某個錯字換成正確寫法 | `skill/references/replacements.md` |

不想動到技能本體（升級會被覆蓋）的話，把自己的替換規則放 `~/.audio-to-srt/replacements.md`，
格式相同，會**先於**內建規則執行。

⚠️ 中文規則要小心：機械替換沒有詞邊界可言，寫「三十八 → 某某」會把「第三十八頁」也改掉。
凡是可能出現在正常語句裡的中文字串，交給清字階段依語境判斷，不要寫進替換規則。

## 怎麼觸發

對你的 Agent 說：「把這個錄音轉字幕」「幫這支影片做 SRT」「語音轉文字加時間碼」。

## 授權

MIT — 歡迎老師們自由使用與改作。
