# audio-to-srt（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。
> Claude Code 不讀 `agents.md`，改由 `CLAUDE.md` 的 `@agents.md` import 本檔；Claude 專屬規範寫在 `CLAUDE.md`。

## 專案簡介

一個開源（MIT）的 AI Agent 技能包：把上課錄音、教學影片丟給 Agent，自動產出時間碼精準、贅字清乾淨的 SRT 字幕檔與純文字稿。預設走 Groq `whisper-large-v3-turbo`（雲端、word-level 時間碼），無金鑰時備援本地 Whisper medium。適用於 Claude Code、OpenCode、Codex 等讀 SKILL.md 的 Agent。

## 關鍵時程

<!-- 尚未設定；有發佈或分享時程再補 -->

## 目標與路線圖

- [x] 階段一：推上 GitHub 公開 repo，讓其他老師可 clone／下載 ZIP 安裝
- [ ] 階段二：安裝到本機技能目錄（`~/.claude/skills/audio-to-srt`）實測整條流水線
- [x] 階段三：精簡 `vocabulary.md` 至 prompt 上限內（現 26 詞全數生效，198/200）
- [ ] 階段四：補使用範例（實際音檔 → SRT 的前後對照）與疑難排解章節

## 資料夾結構

```
audio-to-srt/
├── agents.md                     # 本檔：跨 Agent 專案藍圖
├── handoff.md                    # 交接檔（不進 git，走雲端硬碟同步）
├── CLAUDE.md                     # 橋接檔（@agents.md）
├── README.md                     # 對外說明：這是什麼、怎麼安裝、怎麼觸發
├── LICENSE                       # MIT
├── .gitignore
├── .gitattributes
└── skill/                        # ← 要複製到技能目錄的內容
    ├── SKILL.md                  # 技能主文件：觸發條件、兩條路線、10 步 SOP
    ├── scripts/
    │   ├── transcribe_groq.py    # Groq STT，產 word-level JSON；>24MB 自動壓縮
    │   ├── resegment.py          # 依 word-level 時間碼重新斷句＋靜音偵測
    │   ├── apply_vocab.py        # 詞彙機械替換（只動文字行）
    │   ├── srt_to_txt.py         # SRT → 純文字稿
    │   └── validate_srt.py       # 段數與時間碼驗證
    └── references/
        ├── cleanup_rules.md      # 清字規則（逐段不跨段）
        ├── vocabulary.md         # 詞彙表 → 自動組成 Whisper initial prompt
        └── replacements.md       # 機械替換規則＋保護詞（使用者可覆寫）
```

## 專案專屬規則

### 時間碼不變式（本專案的核心，違反即失敗）

1. **時間碼行完全不准改動**：清字過程中每塊的 `HH:MM:SS,mmm --> HH:MM:SS,mmm` 那一行原樣保留
2. **段落邊界不可動**：清字階段不得合併、拆分、新增或刪除段落（只有 resegment 階段能切，且以 word-level 時間碼為準）
3. **只改文字，不改語意**：修錯字、加標點、順語感，但不得增刪內容
4. 每次清字後一律跑 `validate_srt.py` 驗證，不靠肉眼

### 發佈與隱私

- 本 repo **公開**。任何改動推送前確認沒有 API key、真實絕對路徑、學生或個人資料
- Groq API Key 一律從環境變數 `GROQ_API_KEY` 或 `~/.groq_api_key` 讀取，**不得寫死在腳本裡**
- `vocabulary.md` 若加入新詞彙，注意不要放進未公開的人名或校內資訊

### 相容性

- **Python 3.9+**，且**不得引入第三方套件**——老師的電腦不一定裝得起來，標準庫寫得出來就用標準庫
- 目標平台以 **Windows** 為主：本地 Whisper 路線一律加 `PYTHONUTF8=1` 與 `-X utf8`，否則 cp950 寫不了繁中
- 中文檔名上傳 Groq 會壞編碼，`transcribe_groq.py` 內部一律改用 `audio.<ext>` 上傳
- `replacements.md` 的規則**順序有意義**：先 GPT-Codex 變體 → 再 Claude 生態 → 最後 Cloud→Claude。新增規則時務必確認插入位置
- **機械替換只處理確定性的一對一映射**。需要語境判斷的（中文同音字、可能是正常語句的字串）一律留給清字階段——寫進 `replacements.md` 就會誤傷
- 新增英文規則靠**詞邊界**自動防護；多字詞（`Google Cloud`）擋不住的，加進〈保護詞〉那節
- 靜音修正只認**跨越段落邊界**的靜音，段內換氣必須忽略，且 end 只能縮短不能延長
- `vocabulary.md` 有 prompt 長度上限（約 224 token，腳本抓 200 字），**重要的詞放前面**——超出的會從尾端截掉，只印警告不報錯。額度目前幾乎用滿，**加新詞前先決定拿掉哪一個**；`A / B` 這種寫法會被拆成兩個詞條，佔兩個名額

### 安裝與同步

- 安裝副本在 `~/.claude/skills/audio-to-srt`。複製的是 `skill/` 的**內容**：
  `Copy-Item -Recurse -Force skill\* "$env:USERPROFILE\.claude\skills\audio-to-srt\"`
  寫成 `Copy-Item -Recurse skill "...\audio-to-srt"` 在目標已存在時會變成巢狀的 `audio-to-srt\skill\`，技能就讀不到
- 一律改本專案的原始檔，不要直接編輯安裝副本

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md`（不進 git，只走雲端硬碟）＋`CLAUDE.md`（橋接） | 每個 session |
| L2 | GitHub | [changyiwu/audio-to-srt](https://github.com/changyiwu/audio-to-srt)（**公開**） | 指定時 |
| L3 | Obsidian | `audio-to-srt/專案工作流程.md` | 有需要時 |

## 三個檔案的職責（依「時效性」分家，不是依「詳細程度」）

| 檔案 | 時效 | 寫入方式 | 放什麼 |
|------|------|---------|--------|
| `handoff.md` | **只對下一個 session 有效**，過期即丟 | 每次收工**整份重寫** | 做到哪、下一步、**這次**的暫時 workaround |
| `agents.md`（本檔） | **長期有效**，每個 session 都適用 | 只有規則本身變了才改 | 目標、路線圖、常設規則、結構 |
| Obsidian（L3）／`git log` | **歷史**：發生過什麼、為什麼 | 只增不刪 | 決策紀錄、踩坑完整版、逐次進度 |

驗收標準：**`handoff.md` 整份刪掉，不應損失任何長期資訊**——會的話代表該升級進本檔卻沒升級。

**本檔不要出現的東西**（會無限膨脹，且開工每次都要重讀）：
- ❌ `## 最近進度`／逐次工作紀錄 → 有 L3 寫 Obsidian「🗓️ 最近更動紀錄」；沒有就靠 `git log`（所以 commit 訊息要寫「做什麼＋為什麼」）
- ❌ 決策記錄、取捨理由、踩坑經過的完整版 → Obsidian「決策紀錄」「🕳️ 踩坑筆記」
- ✅ 只留「結論式的規則」：踩過的坑收斂成一條**祈使句**寫進〈工作約定〉或〈專案專屬規則〉，理由那一大段留在 Obsidian

## 工作約定
- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- `handoff.md` **不進 git**（含真實電腦名與本機絕對路徑），已列入 `.gitignore`，跨電腦靠雲端硬碟同步——不要把它加回版控
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
