# Windows community 7.5 — icons, smaller downloads, cooperative exit

[Download the recommended portable folder ZIP](https://github.com/lins58308/Unbound-editor-device-customizer/releases/download/community-v7.5/SpeedEditorCustomizer-v7.5-Windows-Portable.zip), extract the entire folder, then run `SpeedEditorCustomizer.exe`. Keep `_internal` alongside it. This edition avoids temporary runtime extraction and deletion on every launch/exit. Its launcher is 6.55 MB and its companion runtime is 73.23 MB.

[A standalone 33.69 MB EXE](https://github.com/lins58308/Unbound-editor-device-customizer/releases/download/community-v7.5/SpeedEditorCustomizer-v7.5-Windows.exe) is also available, down 28.35% from 7.4's 47.02 MB. Both editions have the same functionality and require no Python installation. Preserve your own `config.json` when updating; replace the whole `_internal` directory when updating the folder edition.

## Changes

The executable, main window, floating window and tray share a new controller icon at nine native sizes. Windows application icons request their display size and recover alpha from black/white rendering, including older AND-mask icons with zero alpha. GDI bitmaps, DCs and HICONs are released after extraction. Windows' size-selection API is documented in [SHDefExtractIconW](https://learn.microsoft.com/windows/win32/api/shlobj_core/nf-shlobj_core-shdefextracticonw).

Full exit signals the HID loop, foreground monitor, OBS helper and discovery worker, then polls their completion through Qt. The GUI never joins those threads. Device reads poll at 100 ms; the reconnect wait wakes on the stop event. Existing unsaved-edit confirmation and close-to-tray behavior are retained. The input-release worker releases held keys and mouse state before Qt exits.

The package excludes unused software OpenGL, Qt PDF image support and Pythonwin MFC UI files after a retained-binary dependency audit. All retained payloads are identical after decompression except the deliberately replaced HID reconnect loop; the rest of the original main dispatcher is retained. No control actions, application templates, language catalogs or saved preferences are removed.

The two packaging modes use the original bootloader and the documented [PyInstaller contents directory option](https://pyinstaller.org/en/stable/usage.html). A language rewrite was not needed for this reduction.

## Rebuild the exact reviewed executable

Use Windows x64 with **Python 3.12** and Pillow. Download the public [7.4 standalone EXE](https://github.com/lins58308/Unbound-editor-device-customizer/releases/download/community-v7.4/SpeedEditorCustomizer-v7.4-Windows.exe). Its SHA256 must be `933dd971567782bf16aa99244310f628df2548738e3d39a3f4f00d250e6f40e4`.

```sh
python build_performance.py --baseline path/to/verified-v7.4.exe --output path/to/v7.5.exe
python build_folder_v75.py --exe path/to/v7.5.exe --out path/to/portable-folder
```

The builder reuses Qt from the verified package to render deterministic icons; no private installation is needed. `validation.json` records output hashes. Earlier UI and localization additions remain in [windows-7.4](../windows-7.4) and [windows-7.2](../windows-7.2). These extensions are not yet integrated into the inherited upstream source entry point or build workflow.

## Validation

All 107 prior-control, 42 background and 161 language checks pass. The final packaged executable also passes 161 native language checks and 14 native icon/HID cases. The native fixtures use isolated configuration and inert hardware/output/OBS doubles. The icon cases include legacy zero-alpha transparency, deterministic rendering and GDI handle ownership. The exact packaged reconnect-loop code is checked for immediate cancellation.

The deliberate slow-worker fixture compares a 7.4 baseline with the final single and folder editions. Both 7.5 editions return promptly from the close request, keep Qt heartbeat events running while waiting, and finish every tracked worker before process exit. These are controlled fixture timings, not a promise about every computer's complete process lifetime.

Manual Windows acceptance checks real installed-program discovery, native application icons, existing OBS templates, hiding the floating keyboard, close to tray, restoration and full exit through the production tray menu. Physical hardware and every third-party application's shortcuts have not all been manually tested; macOS is untested.

Run the isolated native fixtures in a disposable folder, never beside your real configuration:

```sh
python tests/make_desktop_acceptance.py --main native_acceptance_v75.py --exe path/to/v7.5.exe --out isolated-languages --name "Language Checks.exe"
python tests/make_desktop_acceptance.py --main native_icon_hid_v75.py --exe path/to/v7.5.exe --out isolated-icons --name "Icon Checks.exe"
python tests/make_desktop_acceptance.py --main native_performance_probe.py --exe path/to/v7.5.exe --out isolated-exit --name "Exit Checks.exe"
```

Run each generated EXE from its disposable directory to write its report. The harness substitutes only the main entry and test guards while retaining real packaged production modules. Public downloads contain no private configuration, account data or logs.

Original author: [PuzzleEmptyM](https://github.com/PuzzleEmptyM/Unbound-editor-device-customizer). HID authentication algorithm: [Sylvain Munaut](https://github.com/smunaut), Apache 2.0. Official upstream integration remains subject to the author's review.
