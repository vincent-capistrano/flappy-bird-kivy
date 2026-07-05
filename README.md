# Flappy Bird — Kivy

A Flappy Bird clone built with [Kivy](https://kivy.org/). Features persistent high score, coin bank, and a bird & pipe skin shop. Runs on PC (Windows / macOS / Linux) and Android.

---

## Running on Windows

### Prerequisites
- [Python 3.8+](https://www.python.org/downloads/) — during install, check **"Add Python to PATH"**
- Git (optional, for cloning)

### Steps

**1. Clone or download the repo**
```powershell
git clone https://github.com/vincent-capistrano/flappy-bird-kivy.git
cd flappy-bird-kivy
```

**2. Create a virtual environment**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
> If you get an execution policy error, run this first:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> ```

**3. Install dependencies**
```powershell
pip install -r requirements.txt
```

**4. Run the game**
```powershell
python main.py
```

---

## Running on macOS / Linux

### Prerequisites
- Python 3.8+
- pip

### Steps

**1. Clone the repo**
```bash
git clone https://github.com/vincent-capistrano/flappy-bird-kivy.git
cd flappy-bird-kivy
```

**2. Create a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

> On macOS, if you hit SDL2 errors install via Homebrew:
> ```bash
> brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer
> ```

**4. Run the game**
```bash
python main.py
```

---

## Running on Android

### Option A — Install the pre-built APK (easiest)

1. Download the latest `.apk` from the [Releases](https://github.com/vincent-capistrano/flappy-bird-kivy/releases) page (or from the repo root).
2. Transfer it to your Android device.
3. Enable **Install from unknown sources** in your device settings.
4. Tap the APK to install and launch.

### Option B — Build from source with Buildozer (WSL / Ubuntu)

> Requires Windows Subsystem for Linux (WSL) or a native Ubuntu machine.

**1. Install Buildozer inside WSL/Ubuntu**
```bash
pip install buildozer
sudo apt install -y git zip unzip python3-pip \
    libffi-dev libssl-dev libbz2-dev libsqlite3-dev
```

**2. Build the debug APK**
```bash
buildozer android debug
```
Or use the helper script included in the repo:
```bash
bash build_wsl.sh
```

**3. Deploy to a connected device**
```bash
buildozer android debug deploy run
```

The APK is output to the `bin/` directory. Build config is in `buildozer.spec` (targets Android API 33, min API 21, arm64-v8a + armeabi-v7a).

---

## Controls

| Action | Input |
|--------|-------|
| Flap | Left-click / tap / Space bar |
| Navigate menus | Mouse / touch |
