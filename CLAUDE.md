@agents.md

<!--
  本檔是「橋接檔」：Claude Code 只讀 CLAUDE.md，不讀 agents.md，
  所以用第一行的 @agents.md 把跨 Agent 專案藍圖 import 進來。
  專案內容一律寫進 agents.md，這裡只放 Claude Code 專屬規範，避免兩份分叉。
-->

## Claude Code 專屬

- 本專案是「技能的原始檔」，`skill/` 的內容會被複製到 `~/.claude/skills/audio-to-srt` 當安裝副本。**一律改這裡的原始檔**，改完說「同步技能」交給 `sync-skills` 覆蓋安裝副本，不要直接編輯技能目錄裡的副本
