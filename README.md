# Windows 社群版 7.5 / Windows community edition

**[⬇ 直接下載精簡版 EXE · 33.7 MB](https://github.com/lins58308/Unbound-editor-device-customizer/releases/download/community-v7.5/SpeedEditorCustomizer-v7.5-Windows.exe)**

**[⬇ 建議使用：可攜資料夾 ZIP（啟閉免重複解壓）](https://github.com/lins58308/Unbound-editor-device-customizer/releases/download/community-v7.5/SpeedEditorCustomizer-v7.5-Windows-Portable.zip)** · [新版內容與全部下載](https://github.com/lins58308/Unbound-editor-device-customizer/releases/tag/community-v7.5)

7.5 修正 Windows 應用程式圖示的透明度、黑底及尺寸處理，主視窗、浮動鍵盤、EXE 與系統匣使用一致的新圖示。完整退出改為先通知背景工作與裝置停止，再完成清理；介面不再同步等待背景執行緒。

單檔 EXE 從 **47.02 MB 縮小至 33.69 MB（減少 28.35%）**。資料夾版 EXE 為 6.55 MB，搭配 73.23 MB 執行元件，**請保留旁邊的 `_internal` 資料夾**；兩個版本功能相同，都不用安裝 Python。更新時保留自己的 `config.json`，資料夾版需一併更新整個 `_internal`。

保留 12 種離線語言、固定滑鼠操作、自動應用程式配置、毛玻璃浮動鍵盤、可調顏色、滑鼠穿透及背景系統匣。到「語言 / Language」切換語言；主視窗、浮動鍵盤、使用說明與系統匣選單立即更新。關閉視窗可在系統匣繼續運作；右鍵選「結束程式」才完整退出。

**English:** Both downloads preserve all 7.4 features. The standalone EXE is 28.35% smaller; the recommended folder edition avoids repeated temporary extraction. Keep `_internal` beside its EXE. Icons and cooperative full exit are fixed. Downloads contain no private configuration or account data.

原始碼、精確重建步驟與驗證紀錄：[community/windows-7.5](community/windows-7.5)。原有操作、背景及語言檢查全部通過，並完成 Windows 原生圖示、裝置停止及實際系統匣還原／退出驗證。早期擴充在 [windows-7.4](community/windows-7.4) 和 [windows-7.2](community/windows-7.2)；繼承的上游建構流程仍只建構上游入口。

這是 lins58308 維護的非官方社群版本。原作者：[PuzzleEmptyM](https://github.com/PuzzleEmptyM/Unbound-editor-device-customizer)。[上游回饋 #4](https://github.com/PuzzleEmptyM/Unbound-editor-device-customizer/issues/4) · [待審核整合 PR #5](https://github.com/PuzzleEmptyM/Unbound-editor-device-customizer/pull/5)。正式整合由原作者審核。

---

## Original upstream README

# Unbound — Editor Device Customizer

A desktop app for remapping the buttons on a compatible editor controller to anything you want, without needing any host software open.

## Download

**[Download the latest build](https://github.com/PuzzleEmptyM/blackmagic-speed-editor-customizer/releases/tag/latest)**

| Platform | File |
|----------|------|
| Windows | `UnboundCustomizer-Windows.zip` — extract and run `UnboundCustomizer.exe` |
| macOS — Apple Silicon | `UnboundCustomizer-macOS-AppleSilicon.zip` — extract and open `UnboundCustomizer.app` |
| macOS — Intel (macOS 13+) | `UnboundCustomizer-macOS-Intel.zip` — extract and open `UnboundCustomizer.app` |

> Builds are updated automatically whenever the main branch changes.

---

## Quick Feature Update: March 15, 2025

- **Jog wheel / dial customization** - map left and right turns for each dial mode (Jog, Shuttle, Scroll) to any hotkey, with adjustable sensitivity (threshold)
- **Dial mode buttons** - assign a button to temporarily override the dial to control system volume, per-app volume, or screen brightness; press again to toggle off
- **App Launch action** - launch any app from a button press; includes a searchable Start Menu picker and support for `.lnk` shortcuts and URI schemes (e.g. `spotify:`)
- **Categorized action selector** - button actions are now organized into categories (Keyboard, Application, OBS, Layer, Dial) instead of a single flat list
- **Dial settings tab** - dial hotkey and sensitivity settings moved into their own tab

---

## Features

**Button actions**

- **Hotkey** - tap a key combination (e.g. `ctrl+shift+s`)
- **Hold Key** - hold a modifier key (e.g. alt, shift, delete, etc.) down for as long as the device button is physically held
- **Toggle Hold** - latch a modifier key down on first press, release it on second press
- **App Switch** - bring any open window to focus by title substring
- **App Launch** - launch an application by path, Start Menu shortcut, or URI
- **OBS: Switch Scene** - switch to a named OBS scene
- **OBS: Toggle Stream / Record / Mute Mic** - toggle OBS outputs
- **Dial: System Volume** - while active, the dial controls master volume (with native Windows OSD)
- **Dial: App Volume** - while active, the dial controls volume for a specific app
- **Dial: Brightness** - while active, the dial controls screen brightness
- **Dial: Reset** - return the dial to its normal hotkey mode

**Dial / jog wheel**

The jog wheel has three physical modes: Jog (relative), Shuttle (absolute position), and Scroll (relative). Each mode can have its own left and right hotkey assigned. A **Threshold** setting controls how many ticks must accumulate before an action fires, so you can tune sensitivity per mode.

Dial mode buttons (System Volume, App Volume, Brightness) are toggles: press once to activate, press the same button again to deactivate, or press a different dial mode button to switch directly.

**Layer system**

Layers are like menus. Each layer has its own set of button mappings and dial settings. You can map a button to "Layer: Push" to switch all bindings to another layer, and the same button is automatically assigned as "Layer: Back" on the target layer so you can never get stuck.

Layers appear as tabs at the top of the Buttons view. The active layer is marked with an arrow. When the physical device switches layers, the app follows automatically.

**Device connection**

The app connects to the device over Bluetooth or USB without any host software running. It handles the proprietary challenge-response authentication on its own and re-authenticates automatically before the session times out.

If the device is not available at startup, the app retries every 3 seconds in the background. The status bar shows the current connection state.

## Requirements

- Windows 10 or 11
- macOS 13 or higher
- Python 3.12
- Compatible editor controller connected over Bluetooth or USB

## Setup (Windows)

Create a virtual environment and install dependencies:

```
python -m venv .venv
.venv\Scripts\pip install PyQt6 hidapi pynput pywin32 obsws-python pycaw screen-brightness-control
```

Then run:

```
.venv\Scripts\python main.py
```

## Running from source (Mac)

<a name="running-from-source-mac"></a>

Requires Python 3.12 and [Homebrew](https://brew.sh).

```
brew install python@3.12
python3.12 -m venv .venv
.venv/bin/pip install PyQt6 hidapi pynput obsws-python screen-brightness-control
```

Then run:

```
.venv/bin/python main.py
```

> Screen brightness control on macOS may require granting Accessibility permissions in System Settings → Privacy & Security.

## Using Toggle Hold for modifier+scroll

1. Map a button to **Toggle Hold** and enter `alt` (or `ctrl`, `shift`, etc.)
2. Press the button once to latch the modifier key down
3. Scroll your mouse wheel in any app
4. Press the button again to release the modifier

To verify the latch is active before testing scroll, press Tab on your physical keyboard. If Alt+Tab triggers, the modifier is held correctly.

## File structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point, HID thread, layer stack, dial override state |
| `app.py` | PyQt6 GUI, action panel, layer tabs, button grid, dial config |
| `config.py` | Load/save config.json, layer/dial management helpers |
| `hid_layer.py` | Editor device HID abstraction and authentication |
| `actions/hotkey.py` | Keyboard event sending via pynput and win32api |
| `actions/app_switch.py` | Window focus via pywin32 |
| `actions/obs.py` | OBS WebSocket client via obsws-python |
| `actions/system.py` | Master volume, per-app volume, screen brightness |
| `config.json` | Your saved button mappings |

## Authentication

The device requires a challenge-response handshake before it sends input events. The algorithm was reverse-engineered by Sylvain Munaut (Apache 2.0) and is reproduced in `hid_layer.py`. The app authenticates on connect and schedules a re-auth timer before the session expires.

## Credits

HID authentication algorithm by [Sylvain Munaut](https://github.com/smunaut) (Apache 2.0).
Claude Code used for styling, debugging, and documentation.

