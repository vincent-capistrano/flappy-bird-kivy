#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# build_wsl.sh  –  Build Flappy Bird APK inside WSL2 / Ubuntu
# Run:  bash build_wsl.sh
#
# NOTE: builds from ~/flappybird_build/ to avoid the spaces in
#       "Flapy bird" breaking python-for-android's storage-dir.
# ──────────────────────────────────────────────────────────────
set -e

PROJECT_WIN="/mnt/c/Users/errol/OneDrive/Documents/Flapy bird"
BUILD_DIR="$HOME/flappybird_build"

echo ""
echo "=== Step 1: System packages ==="
sudo apt update -qq
sudo apt install -y \
    git zip unzip openjdk-17-jdk python3-pip python3-venv python3-full \
    autoconf libtool pkg-config zlib1g-dev \
    libncurses-dev libtinfo6 \
    cmake libffi-dev libssl-dev

echo ""
echo "=== Step 2: Create Python virtual environment ==="
VENV="$HOME/buildozer-venv"
python3 -m venv "$VENV"
source "$VENV/bin/activate"
pip install --upgrade pip

echo ""
echo "=== Step 3: Install build tools into venv ==="
pip install buildozer cython==0.29.37

echo ""
echo "=== Step 4: Copy source to no-spaces build directory ==="
mkdir -p "$BUILD_DIR"
cp "$PROJECT_WIN/main.py"       "$BUILD_DIR/"
cp "$PROJECT_WIN/buildozer.spec" "$BUILD_DIR/"

echo ""
echo "=== Step 5: Build debug APK ==="
cd "$BUILD_DIR"
buildozer android debug

echo ""
echo "=== Done! ==="
APK=$(ls "$BUILD_DIR/bin/"*.apk 2>/dev/null | head -1)
if [ -n "$APK" ]; then
    cp "$APK" "$PROJECT_WIN/"
    echo "APK copied to: $PROJECT_WIN/$(basename $APK)"
else
    echo "No APK found — check the output above for errors."
fi
