# Flappy Bird — Kivy

A Flappy Bird clone built with [Kivy](https://kivy.org/). Features persistent high score, coin bank, and a bird & pipe skin shop. Runs on PC (Windows / macOS / Linux) and Android.

## Requirements

- Python 3.8+
- pip

## Run Locally (macOS / Linux / Windows)

### 1. Clone the repo

```bash
git clone https://github.com/vincent-capistrano/flappy-bird-kivy.git
cd flappy-bird-kivy
```

### 2. Create and activate a virtual environment

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> On macOS you may also need the SDL2 libraries. Install them via Homebrew:
> ```bash
> brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer
> ```

### 4. Run the game

```bash
python main.py
```

## Controls

| Action | Input |
|--------|-------|
| Flap | Left-click / tap / Space bar |
| Navigate menus | Mouse / touch |

## Build for Android

Requires Ubuntu / WSL with Buildozer installed.

```bash
buildozer android debug deploy run
```

See `build_wsl.sh` for a helper script and `buildozer.spec` for build configuration.
