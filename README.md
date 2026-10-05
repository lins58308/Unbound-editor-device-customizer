# Windows 社群版 7.4 / Windows community edition

**[⬇ 直接下載 Windows EXE（不需安裝 Python）](https://github.com/lins58308/Unbound-editor-device-customizer/releases/download/community-v7.4/SpeedEditorCustomizer-v7.4-Windows.exe)**

[下載可攜 ZIP](https://github.com/lins58308/Unbound-editor-device-customizer/releases/download/community-v7.4/SpeedEditorCustomizer-v7.4-Windows-Portable.zip) · [新版內容與所有下載檔](https://github.com/lins58308/Unbound-editor-device-customizer/releases/tag/community-v7.4)

支援 **12 種離線介面語言**：繁體中文（預設）、簡體中文、英文、日文、韓文、西班牙文、法文、德文、葡萄牙文、義大利文、俄文、印尼文。到「語言 / Language」選擇語言，再按「立即套用 / Apply now」，主視窗、浮動鍵盤、使用說明與系統匣選單會立即更新。原有配置與快捷鍵保持不變。

此版保留固定滑鼠操作、自動應用程式配置、毛玻璃浮動鍵盤、可調顏色與滑鼠穿透。關閉或最小化視窗可在右下角系統匣繼續執行；右鍵圖示選「結束程式」才會完整退出。請把 EXE 放在可寫入資料夾；首次啟動會自動建立設定。更新時保留自己的 `config.json`。

**Standalone EXE available above.** No Python installation is needed to run the Windows community build. It includes twelve offline interface languages, automatic application profiles, consistent mouse controls, a floating physical keyboard guide and background/tray mode. The ZIP and EXE contain no personal configuration or account data. Core control terms are reviewed; some extended descriptions use machine-assisted translation.

Source modules, catalogs, exact-binary rebuild instructions and validation are in [community/windows-7.4](community/windows-7.4). Earlier extensions remain in [community/windows-7.2](community/windows-7.2). These additions are not yet integrated into the inherited upstream Python entry point; the inherited workflow builds upstream code only.

這是 lins58308 維護的非官方社群版本。原作者：[PuzzleEmptyM/Unbound-editor-device-customizer](https://github.com/PuzzleEmptyM/Unbound-editor-device-customizer)。[上游回饋 #4](https://github.com/PuzzleEmptyM/Unbound-editor-device-customizer/issues/4) · [待審核的整合 PR #5](https://github.com/PuzzleEmptyM/Unbound-editor-device-customizer/pull/5)。正式整合由原作者審核。

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
