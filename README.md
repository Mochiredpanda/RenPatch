# RedPanda RenPatch (RPRP)
<img src="assets/icons/favicon.png" width="250" height="250" align="right" alt="RenPatch Icon">

**Say Bye-Bye to the "Missing Characters" (Tofu ☒) in your Ren'Py games.**

**RedPanda RenPatch (RPRP)** is a surgical font optimization tool. It scans your scripts, finds characters your primary fonts can't handle, and generates a lightweight "patch" font along with ready-to-use `.rpy` scripts.

Deliver perfect CJK (Chinese, Japanese, Korean) support without bundling massive, multi-megabyte font files in your package.

---

**RedPanda RenPatch（RPRP）** 是一个为 Ren'Py 引擎设计的字体修复工具，以解决独立游戏开发中的☒缺字问题。RenPatch可以自动扫描游戏脚本文件、对比字库索引来准提取缺失字符，生成体积极小的补丁字库及配套集成的`.rpy`脚本，供开发者进行字体校准和优化。分发的游戏包无需内置臃肿的完整版字体，即可实现更好的跨语言文字显示。

Current Version: **v0.2** Core Logic / Mannual Mode

**v1.0** GUI App In Development
- App & UI Structure Updated

---

## **Feature** 

### GUI Mode (V1.0 In Development)
1. **Patch Wizard Mode**: Drop in with your scripts and I will take over from there.
2. **(In Future Version) Developer Workbench Mode**: Access more advanced features, including *Font Subsetting Tool*, *Donor Font Caliberation*, *Localization Caliberation*, and more.

### Current Phase: Core Logic

1.  **Scan**: RenPatch reads your game directory to find all characters used in your game and localization `.rpy` scripts.
2.  **Compare**: It checks your "Primary Lite Font" to see what's missing.
3.  **Patch**: It extracts *only* the missing glyphs from a "Donor Font" and make a `patch.ttf`. It also generates a patch report for developers who wants to config mannually.
4.  **Integrate**: It generates a drop-in `font_patch.rpy` script with explicit `FontGroup` mapping for your Ren'Py prioritizes the patch for problematic characters.

---

### **How to Use**

*Currently requires Python installed. (GUI App coming soon!)*

1. Place your game project in a directory.
2. Prepare your primary lite font (e.g., `SourceHanSansLite.ttf`) font. you have your "Lite" font (e.g., `SourceHanSansLite.ttf`).
3. Run the pipeline in `core.py`:
   ```python
   # 1. Scans scripts
   # 2. Compares fonts
   # 3. Generates patch.ttf and reports
   # 4. Generates renpatch_init.rpy
4. Drop `patch.ttf` and `renpatch_init.rpy` into your `game/` folder. Or config `renpatch_init.rpy` mannually in your `options.rpy`.
5. Update your `gui.rpy` and localization scripts to use `renpatch_style` font group.

---

### **Changelog**

#### **v0.2 (Current)** - *Scanner Update*
*   **Accelerated scanning pipeline**. More robust regex scanner for triple-quoted multi-line strings and other escaped quotes; more efficient filtering to strip Ren'Py tags (`{size=30}`), interpolation variables (`[player_name]`), and file paths to prevent ghost chars.
*   **Better Logging**. Generates JSON reports on missing characters and a detailed Ren'Py integration script with Hex/Unicode comments. Ready for future features in Developer Workbench Mode.

#### **v0.1** - *Concept Prototype*
*   Basic script scanning and font subsetting using `fontTools`.
*   Manual patching logic.

---

### **Acknowledgements & License**

*   **License**: MIT License
*   **Libraries Used**:
    *   [`fontTools`](https://github.com/fonttools/fonttools): The backbone of our font analysis and subsetting.
    *   [`Flet`](https://flet.dev): For the GUI version.

---
Copyright (c) 2025 Mochiredpanda / Jiyu He