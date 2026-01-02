# ⚡ SharePoint Downloader (Microsoft Stream / SharePoint Media)

> **Professional Windows GUI app to download Microsoft Stream & SharePoint-hosted media** using `yt-dlp` — with **browser-based login (MFA friendly)**, **cookies import**, **proxy support**, and **automatic FFmpeg recovery**.

![Version](https://img.shields.io/badge/version-v1/3-blue)
![UI](https://img.shields.io/badge/UI-Tkinter-lightgrey)
![Engine](https://img.shields.io/badge/engine-yt--dlp-orange)
![Platform](https://img.shields.io/badge/platform-Windows-0078D4)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📌 Overview

**SharePoint Downloader** is a Windows desktop tool built for organizations that host videos on **Microsoft 365**:

* Microsoft Stream
* SharePoint-hosted video pages ("Stream on SharePoint" / SharePoint media pages)

It focuses on a smooth user experience:

* Authenticate via **Chrome/Edge** (isolated temporary profile)
* Download with **progress / speed / ETA**
* Optional **Audio-only MP3** conversion
* Smart network handling with **Proxy settings**

> ✅ This project is primarily a **media downloader** for SharePoint/Stream pages.
> It is **not** a Graph API document-library downloader.

---

## ✨ Highlights

* 🔐 **Stable Login**: Auto Browser Login (Chrome/Edge) — works well with MFA
* 🍪 **Cookies File Import**: use a Netscape cookies `.txt` file
* 🧰 **Auto FFmpeg Installer**: downloads and extracts FFmpeg automatically if missing
* 🌐 **Proxy Support**: enable/disable + auto detect + connection test
* ⏯️ **Pause / Resume**: freeze/unfreeze download thread safely
* 🧾 **Logs & History**: event log in UI + `download_history.log`
* 🧼 **Clean Temp Profiles**: removes temp browser profile after completion

---

## 🖼️ Screenshots

> Add screenshots to make the repo look premium:

* `docs/screenshots/main.png`
* `docs/screenshots/proxy.png`
* `docs/screenshots/history.png`

---

## ⬇️ Download (EXE)

> I publish ready-to-run builds in **GitHub Releases**.

1. Open the repository
2. Go to **Releases**
3. Download the latest `.exe` file
4. Run the app (no Python required)

**Recommended file naming:**

* `SharePointDownloader_v3.exe`

### ✅ Optional: Verify integrity (SHA256)

When a release is published, I will add a `SHA256SUMS.txt` file.

PowerShell:

```powershell
Get-FileHash ./SharePointDownloader_v14.exe -Algorithm SHA256
```

---

## 🧩 Requirements (Source Run)

* Windows 10/11
* Python 3.10+

Install dependencies:

```bash
pip install -U yt-dlp
```

> `tkinter` is usually included with Python on Windows.

---

## ⚙️ First Run Behavior

On first launch, the app runs a **System Check**:

* If `ffmpeg.exe` is missing, it auto-downloads FFmpeg and saves it in:

```text
%APPDATA%/SharePointDownloader/
```

---

## ▶️ How to Use

1. Open the app
2. Paste the **SharePoint / Stream URL** into **MEDIA SOURCE URL**
3. Choose an access method:

   * **Auto Browser Login** (Recommended)
   * **Import Cookies File**
4. Choose Quality (Best / 1080p / 720p)
5. Optional:

   * **Audio Only (MP3)**
   * **Shutdown on Finish**
6. Click **START DOWNLOAD**

After completion:

* **OPEN FOLDER** to view downloads
* **PLAY FILE** to open the last downloaded file

---

## 🔐 Authentication

### Option A — Auto Browser Login (Recommended)

* Select **Chrome** or **Edge**
* The app launches the browser in an isolated profile folder:

```text
%TEMP%/SharePointDownloader_Profile
```

Then:

* Log in
* Refresh the page
* Close the browser

The app reads cookies from the session and continues downloading.

### Option B — Cookies File

* Provide a cookies file (`.txt`) in Netscape format
* Choose **Import Cookies File** → Browse

---

## 🌐 Proxy & Network

Open **Tools → Proxy Settings**:

* ✅ Enable Proxy
* 🌐 Auto Detect system proxy
* 🧪 Test Connection

Proxy URL format examples:

```text
http://host:port
http://user:pass@host:port
```

---

## 🗂️ Configuration & Storage

The app stores settings and history in:

```text
%APPDATA%/SharePointDownloader/settings.json
%APPDATA%/SharePointDownloader/download_history.log
```

Settings include:

* save_path
* browser
* quality
* auto_paste
* cookie_file
* proxy
* use_proxy

---

## 📦 Build (PyInstaller)

Example:

```bash
pyinstaller --noconsole --onefile --name "SharePointDownloader" main.py
```

Notes:

* The app uses `resource_path()` to support PyInstaller (`_MEIPASS`).
* If you add icons or docs, include them in the build options.

---

## 🧯 Troubleshooting

### Start button is disabled

* Wait for the **System Check** to finish.
* If FFmpeg is installing, you will see progress.

### Login/download fails

* Prefer **Auto Browser Login** (best with MFA)
* Ensure the link opens correctly in your browser

### MP3 doesn’t work

* Confirm FFmpeg was installed successfully

### Proxy issues

* Use **Test Connection**
* Verify credentials and port

---

## 🔐 Security & Compliance

* Do **not** hardcode secrets in the project.
* Cookies are used only to authenticate your session.
* Please comply with your organization’s policies and content rights.

---

## 🧾 Changelog (Suggested)

* **v1** — robust installer (FFmpeg recovery), proxy UI, pause/resume, history logging
* **v2** (planned) — packaging improvements, better error UX, richer reports
* **v3** (planned) — update checker, portable mode, enhanced format selector

---

## 👤 Author

**AbdulRhman AbdulGhaffar**

* GitHub: [https://github.com/AbdulRhmanAbdulGhaffar](https://github.com/AbdulRhmanAbdulGhaffar)

