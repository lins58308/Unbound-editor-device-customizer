# Windows community 7.4 — offline interface languages and tray mode

Download the **standalone Windows EXE** from [community-v7.4](https://github.com/lins58308/Unbound-editor-device-customizer/releases/tag/community-v7.4). Python is not required to run it. Put it in a writable folder; the first run creates its own configuration. A clean portable ZIP is also available.

Choose **Language → your language → Apply now**. The main window, floating keyboard, guide and tray menu update immediately. The preference survives restart. Languages: Traditional Chinese (default), Simplified Chinese, English, Japanese, Korean, Spanish, French, German, Portuguese, Italian, Russian and Indonesian.

The 7.3 background/tray improvements are included. Close or minimize the main window to keep the controller working in the tray. Right-click the tray icon for the floating panel, click-through toggle, guide or full exit. No Windows autostart entry is created.

## Source and reproducibility

This directory contains the 7.3 background module, 7.4 localization module, eleven embedded target catalogs, reviewed core terms, builders and isolated native acceptance harness. It builds on the verified public community 7.2 executable. All original archive payloads, the original main dispatcher and the original bootloader are retained byte for byte.

These additions are not integrated into the inherited upstream `main.py`. The inherited build workflow builds upstream code only. This directory does not include a baseline executable, private configuration, account data or logs.

With **Python 3.12**, extract `SpeedEditorCustomizer.exe` from the existing [7.2 portable release](https://github.com/lins58308/Unbound-editor-device-customizer/releases/tag/community-v7.2). Its SHA256 must be `104412c6ca47568c95b6e9d0f3e4e72598dd26c6d4a893899b1632fecc92b3d7`.

```sh
python build_background.py path/to/verified-v7.2.exe path/to/v7.3.exe
python build_languages.py --baseline path/to/v7.3.exe --output path/to/v7.4.exe
```

The 7.3 intermediate SHA256 is `12e605d8f568489e033fb25f8ba1d627d0deec8431aecb75fc37c2609e830991`. The final build hash is recorded in `validation.json` and the release `SHA256SUMS.txt`.

## Validation

The validation record distinguishes automated checks and manual Windows operations. Automated fixtures replace HID, cloud, OBS connection and external input with inert doubles while exercising the real packaged widgets and controller callbacks. They check twelve-language switching, persistence, unsaved edits, hardware enum serialization, translated search, dynamic tabs, dialogs, physical floating-keyboard layout and failed saves. The physical hardware and every third-party application's shortcuts have not all been manually tested. macOS is untested.

To reproduce the isolated native language checks, use a disposable folder and the newly built EXE:

```sh
python tests/make_desktop_acceptance.py --main native_acceptance_v74.py --exe path/to/v7.4.exe --out isolated-native-test --name "Language Checks.exe"
```

The harness creates only test configuration next to the test EXE and exits after writing `language-report.json`. Do not run it in the folder containing your real user configuration.

Core control terms were reviewed; extended descriptions use machine-assisted translation. Corrections can be submitted as changes to `locales/<language>.json`. Catalogs contain public interface strings only and are embedded in the EXE; the app never contacts a translation service.

Original author: [PuzzleEmptyM](https://github.com/PuzzleEmptyM/Unbound-editor-device-customizer). HID authentication algorithm: [Sylvain Munaut](https://github.com/smunaut), Apache 2.0. Upstream integration remains subject to author review.
