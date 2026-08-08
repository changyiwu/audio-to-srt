---
name: audio-to-srt
description: 音訊/影片檔自動生成乾淨 SRT 字幕檔。當使用者要「把音訊轉字幕」「做 SRT」「語音轉文字 + 時間碼」「影片上字幕」時請一定要使用此技能。預設走 Groq Whisper-large-v3-turbo（雲端、word-level 時間碼），備援本地 Whisper medium。Claude 逐段清字並嚴守時間碼對齊。
---

# audio-to-srt：音訊 → 乾淨 SRT

## 何時觸發
使用者提供音訊/影片檔（mp3/wav/m4a/mp4/mov/mkv）並要求：
- 轉字幕、生成 SRT、上字幕
- 語音轉文字且要有時間碼
- 字幕清洗、修錯字、潤斷句

## 兩條路線

| 路線 | 模型 | 時間碼粒度 | 速度 | 隱私 | 適用 |
|------|------|------------|------|------|------|
| **A. Groq（預設）** | whisper-large-v3-turbo | **word-level** | 快 | 上雲 | 一般情境，要快要準 |
| B. 本地 Whisper | medium | segment-level | 慢 | 完全本地 | 敏感內容、無網路 |

走 Groq 才能用 `resegment.py` 做精準斷句。本地 Whisper 只能保留原 segment。

## 核心原則（最重要，違反即失敗）

1. **時間碼神聖不可侵犯**：清字過程 SRT 每塊的 `HH:MM:SS,mmm --> HH:MM:SS,mmm` 那一行**完全不准改動**
2. **段落邊界不可動**：清字階段不得合併兩段、不得拆分一段、不得新增或刪除段落（resegment 階段才能切，且以 word-level 時間碼為準）
3. **只改文字，不改語意**：修錯字、加標點、順語感，但不得增刪內容

---

## 路線 A：Groq 流程（預設）

### Step 1：環境檢查
```bash
# Groq API Key（擇一）
echo $GROQ_API_KEY                # 環境變數
ls ~/.groq_api_key                # 或本地 key 檔
```
若兩者皆無 → 提示使用者設定，並中止。

ffmpeg 確認（大檔降取樣、靜音偵測會用到）：
```bash
ffmpeg -version 2>&1 | head -1
```

Python 需 **3.9 以上**（腳本用到 `tuple[...]` 型別註記）：
```bash
python --version
```

### Step 2：準備工作目錄
在音訊檔同層建立 `_subtitles/` 存放中間產物。

### Step 3：大檔自動壓縮（已內建）
Groq 上限 25 MB，超過會吐 **502 Bad Gateway**（Cloudflare 擋掉）。
`transcribe_groq.py` 在偵測到檔案 > 24 MB 時，**自動**用 ffmpeg 壓成 16kHz / mono / 32kbps 暫存檔上傳，完成後刪除——使用端無感。78 分鐘片實測從 75 MB → 18 MB，辨識品質仍佳。

若壓縮後仍 > 24 MB（罕見），腳本會中止並提示。屆時手動切段處理。

### Step 4：Groq STT，產出 word-level JSON
```bash
python "%USERPROFILE%/.claude/skills/audio-to-srt/scripts/transcribe_groq.py" \
  "輸入檔.mp3" \
  --out _subtitles/輸入檔.groq.json
```
產出 verbose_json，含 `segments` 與 `words`（每個字都有 start/end）。

`--initial_prompt` 由 `references/vocabulary.md` 的條列詞彙自動組成（略過「誤判對照」「使用方式」兩節）。
要讓 Whisper 認得新的專有名詞，改那份檔案即可；prompt 上限約 224 token，腳本抓 200 字，
超過會從清單尾端截掉並印警告——重要的詞放前面。也可用 `--prompt` 直接覆寫。

### Step 5：依 word-level 時間碼重新斷句 → raw SRT
```bash
python ".../scripts/resegment.py" \
  _subtitles/輸入檔.groq.json \
  --audio "輸入檔.mp3" \
  --out _subtitles/輸入檔.raw.srt
```
切點優先序：強標點 `。！？` > segment 邊界 > 弱標點 `，、` > 硬切（往回找標點）。
參數：`MAX_DUR=3.0s`、`MAX_CHARS=15`、`MIN_DUR=0.6s`。

`--audio` 會在斷句後呼叫 `ffmpeg silencedetect` 偵測真實靜音（預設 -35 dB、0.25 s），
把**跨越段落邊界**的靜音拿來留白：該段 end 縮到靜音起點、下一段 start 延到靜音終點。
不傳 `--audio` 時不做這步（Groq word timestamps 本身無靜音間隔）。

**只認邊界靜音，段落內部的停頓一律忽略**——講者說到一半換氣是常態，
若照著截 end，字幕會在人還在講的時候就消失。判準是靜音要延續到本段結尾附近。
end 只會被縮短不會延長：文字何時被說出以 word-level 時間碼為準，靜音偵測只用來製造留白。

### Step 6：套用詞彙修正（機械式替換）
```bash
python ".../scripts/apply_vocab.py" \
  _subtitles/輸入檔.raw.srt \
  --out _subtitles/輸入檔.vocab.srt
```
規則放在 `references/replacements.md`（**不寫死在程式裡**，Markdown 表格，直接編輯即可），依序執行：
- **GPT-Codex 變體**（含 DexDex/Dex Dex → Codex）：必須最先處理，避免 Cloud→Claude 後誤判
- **Antigravity、Netlify、clasp、Apps Script** 等工具名
- **Claude 生態**：ClockCode/CloudCode/ClawCode → Claude Code、克勞德 → Claude
- **Cloud → Claude**（放最後，避免先動到 Cloud Code）
- **NotebookLM、GPT-Image 2** 等其他 AI 工具
- **常見錯字**：斷考→段考、翻例→範例 等

**只動文字行，時間碼絕不動。**

**兩道防誤傷機制**（沒有這兩層，`Cloud→Claude` 會把 iCloud 改成 iClaude）：

1. **詞邊界**：規則頭尾若是英數字，會要求前後不是英數字 → `iCloud`、`Cloudflare`、`SoundCloud` 都不會被動到
2. **保護詞**（規則檔的〈保護詞〉那節）：詞邊界救不了的多字詞先遮蔽、跑完再還原 → `Google Cloud`、`cloud storage`、`Netflix` 保持原樣

中文規則沒有詞邊界可言，所以**凡是可能出現在正常語句裡的中文字串一律不要寫進規則**
（例如「三十八」是數字、「在」／「再」要看句子才知道哪個對），那類修正交給 Step 7 由 Claude 依語境判斷。

使用者自訂規則放 `~/.audio-to-srt/replacements.md`（同格式），會**先於**內建規則執行，
可覆蓋內建行為；升級技能不會蓋掉它。要暫時停用加 `--no-user-rules`。

### Step 7：Claude 逐段精修
- 用 Read 讀 `輸入檔.vocab.srt`
- 依 `references/cleanup_rules.md` 逐段清理（修標點、刪贅詞）
- 每段只改第 3 行之後的文字
- 產出 `_subtitles/輸入檔.clean.srt`

**清字檢查清單：**
- [ ] 段數是否等於 vocab.srt？（不可增減）
- [ ] 時間碼行是否完全沒動？
- [ ] `references/vocabulary.md` 詞彙是否正確呈現？

### Step 8：驗證
```bash
python ".../scripts/validate_srt.py" \
  --raw _subtitles/輸入檔.vocab.srt \
  --clean _subtitles/輸入檔.clean.srt
```
段數一致、時間碼逐一吻合、單調遞增、文字非空。

### Step 9：產出純文字稿
```bash
python ".../scripts/srt_to_txt.py" \
  _subtitles/輸入檔.clean.srt \
  --out 輸入檔.txt
```
適合：YouTube 描述、IG/FB 貼文、封面金句、後製字稿。

### Step 10：交付
**音訊同層放兩份**：
- `輸入檔.srt` — 字幕檔（複製自 clean.srt）
- `輸入檔.txt` — 純文字稿

`_subtitles/` 中間檔保留供稽核。
回報：總段數、總時長、平均段長、txt 字數、主要修改類型。

---

## 路線 B：本地 Whisper 流程（備援）

當使用者明確要求本地處理、或無 Groq Key 時走此路線。

```bash
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python -X utf8 -m whisper "輸入檔.mp3" \
  --model medium \
  --language zh \
  --output_format srt \
  --output_dir ./_subtitles \
  --initial_prompt "以下為繁體中文。專有名詞：Claude、Claude Code、NotebookLM、Gemini、Groq、Whisper、Obsidian。"
```

`--initial_prompt` 的詞彙比照 `references/vocabulary.md`（本地路線沒有自動組裝，需自行貼上）。

**Windows 踩坑**：
1. `whisper` CLI 不在 PATH → 用 `python -m whisper`
2. cp950 寫不了繁中 → 必須加 `PYTHONUTF8=1` 與 `-X utf8`

產出後跳過 Step 5（resegment 不適用，segment-level 時間碼只能照原樣），直接進 Step 6（apply_vocab）→ Step 7（清字）→ Step 8（驗證）→ Step 9（轉純文字）→ Step 10（交付）。

---

## 檔案結構

```
skills/audio-to-srt/
├── SKILL.md                      # 本檔
├── scripts/
│   ├── transcribe_groq.py        # Groq STT，產 word-level JSON
│   ├── resegment.py              # 依 word-level 時間碼重新斷句
│   ├── apply_vocab.py            # 詞彙機械替換（只動文字行）
│   ├── srt_to_txt.py             # SRT → 純文字稿
│   └── validate_srt.py           # 時間碼驗證
└── references/
    ├── cleanup_rules.md          # 清字規則（逐段不跨段）
    ├── vocabulary.md             # 詞彙表 → 組成 Whisper initial prompt
    └── replacements.md           # 機械替換規則＋保護詞（Markdown 表格）

~/.audio-to-srt/replacements.md   # （選用）使用者自訂規則，先於內建規則執行
```

## 路線選擇決策樹

```
有 GROQ_API_KEY？
├─ 有 → 路線 A（Groq）
│       └─ 檔案 > 25 MB？→ 先 ffmpeg 降至 16k mono 再傳
└─ 無 → 提示使用者設 key；若使用者要求離線 → 路線 B（本地 Whisper）
```

## 踩過的坑

- Whisper 辨識準但斷句差 → Groq word-level + resegment 解決
- 長音訊爆記憶體（本地）→ 改走 Groq；Groq 25 MB 上限 → ffmpeg 降取樣
- Cloud / Claude / Codex 互相誤判 → replacements.md 順序講究：先處理 GPT-Codex 變體（含 DexDex），再 Claude，最後 Cloud→Claude
- 純字串替換會誤傷（iCloud→iClaude、Google Cloud→Google Claude）→ 加詞邊界＋保護詞兩層
- 中文詞規則誤傷正常語句（「三十八」是數字）→ 中文的語境判斷不要交給機械替換，留給 Step 7
- 靜音修正把字幕砍掉（段內換氣被當成句末）→ 只認跨越段落邊界的靜音
- Windows cp950 編碼 → 本地路線一律加 `PYTHONUTF8=1`
- 中文檔名上傳 Groq 編碼壞掉 → transcribe_groq.py 內部改用 `audio.<ext>` 上傳
