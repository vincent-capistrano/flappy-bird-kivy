[app]

# ── App identity ───────────────────────────────────────────────
title        = Flappy Bird
package.name = flappybird
package.domain = org.example

# ── Source ─────────────────────────────────────────────────────
source.dir          = .
source.include_exts = py,png,jpg,kv,atlas

# ── Version ────────────────────────────────────────────────────
version = 1.4

# ── Icon & presplash ───────────────────────────────────────────
icon.filename     = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/icon.png

# ── Requirements ───────────────────────────────────────────────
requirements = python3,kivy

# ── Orientation & display ──────────────────────────────────────
orientation = portrait
fullscreen  = 1

# ── Android settings ───────────────────────────────────────────
android.api           = 33
android.minapi        = 21
android.ndk           = 28c
android.archs         = arm64-v8a, armeabi-v7a
android.allow_backup  = True
android.release_artifact = apk

# ── iOS settings (optional) ────────────────────────────────────
# ios.kivy_ios_url    = https://github.com/kivy/kivy-ios
# ios.kivy_ios_branch = master

# ── Buildozer log ──────────────────────────────────────────────
[buildozer]
log_level   = 2
warn_on_root = 1
