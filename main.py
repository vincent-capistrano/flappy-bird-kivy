"""
Flappy Bird Clone — Kivy
Persistent high score · coin bank · bird & pipe skin shop.
Runs on PC (Windows / macOS / Linux) and Android.
"""
import array
import io
import json
import math
import os
import random
import wave
from collections import deque

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import (
    Color, Rectangle, Ellipse, Triangle,
    PushMatrix, PopMatrix, Rotate, Translate,
)
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.metrics import dp

# ── Desktop window size (ignored on Android / iOS) ─────────────
if platform not in ('android', 'ios'):
    Window.size = (400, 600)

# ── Game tuning ─────────────────────────────────────────────────
PIPE_INTERVAL    = 2.0   # seconds between pipe spawns
SEASON_THRESHOLD = 20    # score points before season advances

# ═══════════════════════════════════════════════════════════════
# Season definitions  (cycles every SEASON_THRESHOLD × 5 points)
# ═══════════════════════════════════════════════════════════════
SEASONS = [
    dict(name='Spring',
         sky=(0.38, 0.68, 0.94), ground=(0.56, 0.40, 0.18),
         grass=(0.30, 0.74, 0.18), stripe=(0.24, 0.62, 0.14),
         cloud=(1.0, 1.0, 1.0, 0.82),
         ambient=(0.0, 0.0, 0.0, 0.0), stars=False),
    dict(name='Summer',
         sky=(0.20, 0.50, 0.92), ground=(0.45, 0.30, 0.10),
         grass=(0.18, 0.65, 0.08), stripe=(0.13, 0.52, 0.05),
         cloud=(1.0, 0.98, 0.84, 0.78),
         ambient=(1.0, 0.90, 0.45, 0.07), stars=False),
    dict(name='Autumn',
         sky=(0.65, 0.42, 0.18), ground=(0.42, 0.25, 0.08),
         grass=(0.62, 0.32, 0.06), stripe=(0.52, 0.22, 0.04),
         cloud=(1.0, 0.72, 0.38, 0.82),
         ambient=(0.85, 0.45, 0.10, 0.10), stars=False),
    dict(name='Winter',
         sky=(0.52, 0.65, 0.80), ground=(0.80, 0.86, 0.90),
         grass=(0.88, 0.92, 0.96), stripe=(0.75, 0.82, 0.88),
         cloud=(0.96, 0.98, 1.0, 0.88),
         ambient=(0.60, 0.80, 1.0, 0.06), stars=False),
    dict(name='Night',
         sky=(0.04, 0.05, 0.16), ground=(0.14, 0.10, 0.06),
         grass=(0.06, 0.18, 0.04), stripe=(0.04, 0.12, 0.02),
         cloud=(0.55, 0.55, 0.68, 0.50),
         ambient=(0.00, 0.00, 0.12, 0.18), stars=True),
]

# ═══════════════════════════════════════════════════════════════
# Skin catalogue
# ═══════════════════════════════════════════════════════════════
BIRD_SKINS = [
    dict(id='bird_classic', name='Classic',  price=0,
         body=(1.0, 0.84, 0.0),   belly=(1.0, 0.95, 0.65),
         wing=(0.88, 0.65, 0.0),  beak=(1.0, 0.50, 0.0)),
    dict(id='bird_red',     name='Crimson',  price=50,
         body=(0.90, 0.15, 0.15), belly=(1.0, 0.60, 0.60),
         wing=(0.70, 0.08, 0.08), beak=(1.0, 0.45, 0.0)),
    dict(id='bird_blue',    name='Ocean',    price=50,
         body=(0.15, 0.45, 0.95), belly=(0.65, 0.82, 1.0),
         wing=(0.08, 0.28, 0.75), beak=(1.0, 0.55, 0.0)),
    dict(id='bird_white',   name='Ghost',    price=75,
         body=(0.92, 0.92, 0.92), belly=(1.0, 1.0, 1.0),
         wing=(0.72, 0.72, 0.72), beak=(1.0, 0.55, 0.10)),
    dict(id='bird_green',   name='Forest',   price=75,
         body=(0.15, 0.72, 0.20), belly=(0.68, 0.95, 0.55),
         wing=(0.08, 0.52, 0.12), beak=(1.0, 0.70, 0.0)),
    dict(id='bird_purple',  name='Royal',    price=100,
         body=(0.55, 0.15, 0.85), belly=(0.85, 0.65, 1.0),
         wing=(0.38, 0.08, 0.65), beak=(1.0, 0.55, 0.10)),
]

PIPE_SKINS = [
    dict(id='pipe_classic', name='Classic', price=0,
         body=(0.22, 0.68, 0.22), cap=(0.17, 0.56, 0.17), hi=(0.42, 0.85, 0.42)),
    dict(id='pipe_steel',   name='Steel',   price=50,
         body=(0.35, 0.45, 0.60), cap=(0.22, 0.32, 0.48), hi=(0.65, 0.75, 0.88)),
    dict(id='pipe_sunset',  name='Sunset',  price=50,
         body=(0.90, 0.45, 0.10), cap=(0.75, 0.28, 0.05), hi=(1.0,  0.70, 0.40)),
    dict(id='pipe_neon',    name='Neon',    price=75,
         body=(0.55, 0.10, 0.80), cap=(0.38, 0.05, 0.60), hi=(0.80, 0.50, 1.0)),
    dict(id='pipe_ice',     name='Ice',     price=100,
         body=(0.55, 0.88, 0.98), cap=(0.35, 0.70, 0.88), hi=(0.82, 0.96, 1.0)),
]

# Trail skins  (body = swatch colour used in shop card)
TRAIL_SKINS = [
    dict(id='trail_none',    name='None',       price=0,
         body=(0.28, 0.28, 0.30)),
    dict(id='trail_sparkle', name='Sparkle',    price=30,
         body=(1.00, 0.80, 0.20)),
    dict(id='trail_rainbow', name='Rainbow',    price=60,
         body=(1.00, 0.30, 0.75)),
    dict(id='trail_fire',    name='Fire',        price=75,
         body=(1.00, 0.32, 0.04)),
    dict(id='trail_ice',     name='Ice',         price=75,
         body=(0.45, 0.80, 1.00)),
    dict(id='trail_comet',   name='Comet',       price=100,
         body=(0.85, 0.65, 1.00)),
    dict(id='trail_stars',   name='Stars',       price=80,
         body=(1.00, 0.95, 0.25)),
    dict(id='trail_bubble',  name='Bubbles',     price=60,
         body=(0.55, 0.90, 1.00)),
    dict(id='trail_hearts',  name='Hearts',      price=50,
         body=(1.00, 0.30, 0.45)),
    dict(id='trail_birds',   name='Mini Birds',  price=120,
         body=(0.30, 0.75, 0.30)),
]

# Colour palette for rainbow/sparkle effects
_RAINBOW = [
    (1.0, 0.25, 0.25), (1.0, 0.58, 0.05), (1.0, 0.95, 0.10),
    (0.20, 0.85, 0.25), (0.20, 0.50, 1.0), (0.60, 0.20, 1.0), (1.0, 0.25, 0.80),
]

# ═══════════════════════════════════════════════════════════════
# Persistence helpers
# ═══════════════════════════════════════════════════════════════
_SAVE_DEFAULTS = dict(
    high_score=0,
    coins=0,
    purchased=['bird_classic', 'pipe_classic', 'trail_none'],
    bird_skin='bird_classic',
    pipe_skin='pipe_classic',
    trail_skin='trail_none',
)


def _save_path():
    """Return path to the JSON save file (works on desktop and Android)."""
    if platform in ('android', 'ios'):
        return os.path.join(App.get_running_app().user_data_dir, 'save.json')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'save.json')


def load_save():
    """Load save data from disk, filling defaults for any missing keys."""
    try:
        with open(_save_path(), 'r') as f:
            data = json.load(f)
        for k, v in _SAVE_DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(_SAVE_DEFAULTS)


def write_save(data):
    """Persist save data to disk."""
    try:
        with open(_save_path(), 'w') as f:
            json.dump(data, f)
    except Exception:
        pass


def lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB or RGBA colour tuples."""
    return tuple(a + (b - a) * t for a, b in zip(c1, c2))


# ── Sound utilities — generates WAV tones at runtime, no asset files needed ──
_SFX_NOTES = {
    'score':  [(880, 0.07), (1100, 0.09)],
    'die':    [(440, 0.09), (330, 0.09), (220, 0.16)],
    'season': [(523, 0.09), (659, 0.09), (784, 0.13)],
}

def _make_wav(notes, rate=22050, vol=0.55):
    samp = array.array('h')
    for freq, dur in notes:
        n = int(rate * dur)
        for i in range(n):
            att = min(1.0, i / max(1, int(n * 0.05)))
            rel = min(1.0, (n - i) / max(1, int(n * 0.12)))
            v = int(32767 * vol * att * rel * math.sin(2 * math.pi * freq * i / rate))
            samp.append(max(-32767, min(32767, v)))
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(rate)
        wf.writeframes(samp.tobytes())
    return buf.getvalue()

def _ensure_sounds(data_dir):
    paths = {}
    for name, notes in _SFX_NOTES.items():
        p = os.path.join(data_dir, f'sfx_{name}.wav')
        try:
            if not os.path.exists(p):
                with open(p, 'wb') as f:
                    f.write(_make_wav(notes))
            paths[name] = p
        except Exception:
            pass
    return paths


# ═══════════════════════════════════════════════════════════════
# Shop widgets
# ═══════════════════════════════════════════════════════════════

class SkinPreview(Widget):
    """Canvas-drawn preview widget shown inside each shop card."""

    def __init__(self, skin, skin_type, **kw):
        super().__init__(size_hint=(None, 1), width=dp(62), **kw)
        self.skin      = skin
        self.skin_type = skin_type
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        with self.canvas:
            # Dark background
            Color(0.10, 0.13, 0.20, 1)
            Rectangle(pos=(x, y), size=(w, h))
            if self.skin_type == 'bird':
                self._bird(x, y, w, h)
            elif self.skin_type == 'pipe':
                self._pipe(x, y, w, h)
            else:
                self._trail(x, y, w, h)

    # ── Bird preview ────────────────────────────────
    def _bird(self, x, y, w, h):
        sk = self.skin
        cx = x + w * 0.46
        cy = y + h * 0.50
        r  = min(w, h) * 0.30
        Color(0, 0, 0, 0.14)
        Ellipse(pos=(cx - r*0.88, cy - r*1.12), size=(r*1.75, r*0.44))
        Color(*sk['body'])
        Ellipse(pos=(cx - r, cy - r), size=(r*2, r*2))
        Color(*sk['belly'])
        Ellipse(pos=(cx - r*0.20, cy - r*0.65), size=(r*1.05, r*0.82))
        Color(*sk['wing'])
        Ellipse(pos=(cx - r*0.62, cy - r*0.05), size=(r*1.05, r*0.52))
        Color(1, 1, 1)
        Ellipse(pos=(cx + r*0.18, cy + r*0.18), size=(r*0.52, r*0.52))
        Color(0.05, 0.05, 0.35)
        Ellipse(pos=(cx + r*0.30, cy + r*0.26), size=(r*0.26, r*0.26))
        Color(1, 1, 1)
        Ellipse(pos=(cx + r*0.42, cy + r*0.42), size=(r*0.10, r*0.10))
        Color(*sk['beak'])
        Triangle(points=[
            cx + r*0.82, cy + r*0.18,
            cx + r*0.82, cy - r*0.10,
            cx + r*1.28, cy + r*0.04,
        ])

    # ── Pipe preview ────────────────────────────────
    def _pipe(self, x, y, w, h):
        sk  = self.skin
        pw  = w * 0.50
        px  = x + (w - pw) / 2
        ph  = h * 0.28
        gap = h * 0.26
        ch  = h * 0.09
        cp  = pw * 0.12
        hw  = max(2, pw * 0.14)
        bot = y + h * 0.04
        top = bot + ph + gap
        # Bottom pipe
        Color(*sk['body'])
        Rectangle(pos=(px, bot), size=(pw, ph))
        Color(*sk['cap'])
        Rectangle(pos=(px - cp, bot + ph - ch), size=(pw + cp*2, ch))
        Color(sk['hi'][0], sk['hi'][1], sk['hi'][2], 0.55)
        Rectangle(pos=(px + pw*0.12, bot + 2), size=(hw, ph - ch - 2))
        # Top pipe
        Color(*sk['body'])
        Rectangle(pos=(px, top), size=(pw, ph))
        Color(*sk['cap'])
        Rectangle(pos=(px - cp, top), size=(pw + cp*2, ch))
        Color(sk['hi'][0], sk['hi'][1], sk['hi'][2], 0.55)
        Rectangle(pos=(px + pw*0.12, top + ch + 2), size=(hw, ph - ch - 2))

    # ── Trail preview ──────────────────────────────
    def _trail(self, x, y, w, h):
        tid = self.skin['id']
        cy  = y + h * 0.50
        n   = 8
        for i in range(n):
            af = (i + 1) / n
            px = x + (i + 0.5) * w / n
            sz = max(2, h * 0.19 * af)
            if tid == 'trail_none':
                Color(0.5, 0.5, 0.5, 0.35)
                Ellipse(pos=(px - 2, cy - 2), size=(4, 4))
            elif tid == 'trail_sparkle':
                # White/gold glitter stars with y-jitter
                _SPK = [(1.0,1.0,1.0),(1.0,0.95,0.55),(1.0,0.82,0.20),(0.82,0.95,1.0),(1.0,0.80,0.92)]
                jitter = ((i * 7 + 3) % 11 - 5) * h * 0.05
                c = _SPK[i % len(_SPK)]
                Color(c[0], c[1], c[2], af * 0.92)
                if i % 3 == 0:
                    Triangle(points=[px, cy+jitter+sz, px-sz*0.5, cy+jitter-sz*0.35, px+sz*0.5, cy+jitter-sz*0.35])
                    Triangle(points=[px, cy+jitter-sz, px-sz*0.5, cy+jitter+sz*0.35, px+sz*0.5, cy+jitter+sz*0.35])
                else:
                    Ellipse(pos=(px-sz/2, cy+jitter-sz/2), size=(sz, sz))
            elif tid == 'trail_rainbow':
                # Thick smooth colour band with glow
                c = _RAINBOW[i % len(_RAINBOW)]
                Color(c[0], c[1], c[2], af * 0.28)
                Ellipse(pos=(px-sz*0.75, cy-sz*0.75), size=(sz*1.5, sz*1.5))
                Color(c[0], c[1], c[2], af * 0.90)
                Ellipse(pos=(px-sz/2, cy-sz/2), size=(sz, sz))
            elif tid == 'trail_fire':
                drift = (n - i) * h * 0.042
                c = (1.0,0.90,0.20) if af>0.65 else (1.0,0.42,0.06) if af>0.35 else (0.82,0.10,0.02)
                Color(c[0], c[1], c[2], af * 0.88)
                Ellipse(pos=(px - sz/2, cy - sz/2 + drift), size=(sz, sz))
            elif tid == 'trail_ice':
                c = (0.88,0.96,1.0) if af > 0.5 else (0.35,0.72,1.0)
                Color(c[0], c[1], c[2], af * 0.78)
                Ellipse(pos=(px - sz/2, cy - sz/2), size=(sz, sz))
                if af > 0.7:
                    gs = sz * 0.35
                    Color(1, 1, 1, af * 0.5)
                    Ellipse(pos=(px - gs/2 + sz*0.15, cy - gs/2 + sz*0.15), size=(gs, gs))
            elif tid == 'trail_comet':
                Color(0.85, 0.65, 1.0, af * 0.38)
                Ellipse(pos=(px - sz/2, cy - sz/2), size=(sz, sz))
                if af > 0.55:
                    cs = sz * 0.50
                    Color(1.0, 1.0, 0.92, af * 0.72)
                    Ellipse(pos=(px - cs/2, cy - cs/2), size=(cs, cs))
            elif tid == 'trail_stars':
                if i % 2 == 0:
                    Color(1.0, 0.95, 0.28, af * 0.88)
                    Triangle(points=[px, cy+sz, px-sz*0.58, cy-sz*0.38, px+sz*0.58, cy-sz*0.38])
                    Triangle(points=[px, cy-sz, px-sz*0.58, cy+sz*0.38, px+sz*0.58, cy+sz*0.38])
            elif tid == 'trail_bubble':
                drift = (n - i) * h * 0.030
                Color(0.62, 0.90, 1.0, af * 0.30)
                Ellipse(pos=(px - sz/2, cy - sz/2 + drift), size=(sz, sz))
            elif tid == 'trail_hearts':
                hs = sz * 0.65
                Color(1.0, 0.28, 0.45, af * 0.82)
                Ellipse(pos=(px - hs, cy), size=(hs, hs))
                Ellipse(pos=(px,      cy), size=(hs, hs))
                Triangle(points=[px - hs, cy, px + hs, cy, px, cy - hs*1.1])
            elif tid == 'trail_birds':
                # Show 3 tiny birds in formation
                positions = [(0.25, 0.62), (0.50, 0.38), (0.75, 0.55)]
                for fx, fy in positions:
                    br = max(2, h * 0.14)
                    bpx = x + fx * w
                    bpy = y + fy * h
                    Color(0.28, 0.72, 0.28, 0.88)
                    Ellipse(pos=(bpx - br, bpy - br), size=(br*2, br*2))
                    Color(0.68, 0.95, 0.55, 0.88)
                    Ellipse(pos=(bpx - br*0.2, bpy - br*0.65), size=(br*1.0, br*0.80))
                    Color(1, 1, 1, 0.9)
                    Ellipse(pos=(bpx + br*0.18, bpy + br*0.18), size=(br*0.42, br*0.42))


class SkinCard(BoxLayout):
    """One row in the shop list representing a single skin."""

    def __init__(self, skin, skin_type, save_ref, on_update, **kw):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None, height=dp(72),
            padding=[dp(4), dp(3), dp(6), dp(3)],
            spacing=dp(6),
            **kw,
        )
        with self.canvas.before:
            Color(0.18, 0.22, 0.32, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v: setattr(w._bg, 'pos', v))
        self.bind(size=lambda w, v: setattr(w._bg, 'size', v))

        self.skin      = skin
        self.skin_type = skin_type
        self.save_ref  = save_ref
        self.on_update = on_update

        # Live skin preview
        self.add_widget(SkinPreview(skin, skin_type))

        # Name + price info
        info = BoxLayout(orientation='vertical', spacing=dp(1))
        name_lbl = Label(
            text=skin['name'], font_size='16sp', bold=True,
            color=(1, 1, 1, 1), halign='left', valign='bottom',
            size_hint_y=0.55,
        )
        name_lbl.bind(size=name_lbl.setter('text_size'))
        price_text = 'FREE' if skin['price'] == 0 else f"{skin['price']} coins"
        price_lbl = Label(
            text=price_text, font_size='12sp',
            color=(1, 0.88, 0.20, 1), halign='left', valign='top',
            size_hint_y=0.45,
        )
        price_lbl.bind(size=price_lbl.setter('text_size'))
        info.add_widget(name_lbl)
        info.add_widget(price_lbl)
        self.add_widget(info)

        # Action button
        self.btn = Button(
            size_hint=(None, None), size=(dp(78), dp(34)),
            pos_hint={'center_y': 0.5},
            font_size='12sp', bold=True,
            background_normal='',
        )
        self.btn.bind(on_press=self._action)
        self.add_widget(self.btn)
        self._refresh()

    def _refresh(self):
        sid      = self.skin['id']
        if self.skin_type == 'bird':
            sk = 'bird_skin'
        elif self.skin_type == 'pipe':
            sk = 'pipe_skin'
        else:
            sk = 'trail_skin'
        equipped = self.save_ref[sk] == sid
        owned    = sid in self.save_ref['purchased']
        if equipped:
            self.btn.text = 'Equipped'
            self.btn.disabled = True
            self.btn.background_color = (0.18, 0.72, 0.18, 1)
        elif owned:
            self.btn.text = 'Equip'
            self.btn.disabled = False
            self.btn.background_color = (0.28, 0.52, 1.0, 1)
        else:
            can_afford = self.save_ref['coins'] >= self.skin['price']
            self.btn.text = 'Buy'
            self.btn.disabled = not can_afford
            self.btn.background_color = (
                (0.88, 0.62, 0.05, 1) if can_afford else (0.38, 0.38, 0.38, 1)
            )

    def _action(self, *_):
        sid = self.skin['id']
        if self.skin_type == 'bird':
            sk = 'bird_skin'
        elif self.skin_type == 'pipe':
            sk = 'pipe_skin'
        else:
            sk = 'trail_skin'
        if sid not in self.save_ref['purchased']:
            self.save_ref['coins'] -= self.skin['price']
            self.save_ref['purchased'].append(sid)
        self.save_ref[sk] = sid
        write_save(self.save_ref)
        self.on_update()


class ShopOverlay(FloatLayout):
    """Full-screen shop overlay with Bird / Pipe skin tabs."""

    def __init__(self, save_ref, on_close, **kw):
        super().__init__(**kw)
        self.save_ref = save_ref
        self.on_close = on_close
        self._tab     = 'bird'

        # Semi-transparent backdrop
        with self.canvas.before:
            Color(0, 0, 0, 0.72)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v: setattr(w._bg, 'pos', v))
        self.bind(size=lambda w, v: setattr(w._bg, 'size', v))

        # Panel container
        panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.93, 0.88),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=dp(5), padding=dp(8),
        )
        with panel.canvas.before:
            Color(0.10, 0.12, 0.20, 1)
            self._panel_bg = Rectangle(pos=panel.pos, size=panel.size)
        panel.bind(pos=lambda w, v: setattr(self._panel_bg, 'pos', v))
        panel.bind(size=lambda w, v: setattr(self._panel_bg, 'size', v))

        # Header
        header = BoxLayout(orientation='horizontal',
                           size_hint_y=None, height=dp(42))
        header.add_widget(Label(
            text='S H O P', font_size='21sp', bold=True,
            color=(1, 0.88, 0.10, 1),
        ))
        self.coins_lbl = Label(
            text=f"[b]{save_ref['coins']}[/b] coins",
            font_size='15sp', color=(1, 0.88, 0.20, 1), markup=True,
        )
        header.add_widget(self.coins_lbl)
        close_btn = Button(
            text='X', font_size='17sp', bold=True,
            size_hint=(None, None), size=(dp(36), dp(36)),
            pos_hint={'center_y': 0.5},
            background_normal='', background_color=(0.75, 0.15, 0.15, 1),
        )
        close_btn.bind(on_press=lambda *_: self.on_close())
        header.add_widget(close_btn)
        panel.add_widget(header)

        # Tabs  (Birds | Pipes | Trails)
        tabs = BoxLayout(orientation='horizontal',
                         size_hint_y=None, height=dp(36), spacing=dp(3))
        self.tab_bird_btn = Button(
            text='Birds', font_size='13sp', bold=True,
            background_normal='', background_color=(0.28, 0.55, 1.0, 1),
        )
        self.tab_pipe_btn = Button(
            text='Pipes', font_size='13sp', bold=True,
            background_normal='', background_color=(0.20, 0.28, 0.48, 1),
        )
        self.tab_trail_btn = Button(
            text='Trails', font_size='13sp', bold=True,
            background_normal='', background_color=(0.20, 0.28, 0.48, 1),
        )
        self.tab_bird_btn.bind(on_press=lambda *_: self._switch('bird'))
        self.tab_pipe_btn.bind(on_press=lambda *_: self._switch('pipe'))
        self.tab_trail_btn.bind(on_press=lambda *_: self._switch('trail'))
        tabs.add_widget(self.tab_bird_btn)
        tabs.add_widget(self.tab_pipe_btn)
        tabs.add_widget(self.tab_trail_btn)
        panel.add_widget(tabs)

        # Scrollable list
        self.scroll = ScrollView(do_scroll_x=False)
        self.grid   = GridLayout(cols=1, spacing=dp(3), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        panel.add_widget(self.scroll)

        self.add_widget(panel)
        self._build_list()

    def _switch(self, tab):
        self._tab = tab
        active   = (0.28, 0.55, 1.0, 1)
        inactive = (0.20, 0.28, 0.48, 1)
        self.tab_bird_btn.background_color  = active if tab == 'bird'  else inactive
        self.tab_pipe_btn.background_color  = active if tab == 'pipe'  else inactive
        self.tab_trail_btn.background_color = active if tab == 'trail' else inactive
        self._build_list()

    def _build_list(self):
        self.grid.clear_widgets()
        if self._tab == 'bird':
            skins = BIRD_SKINS
        elif self._tab == 'pipe':
            skins = PIPE_SKINS
        else:
            skins = TRAIL_SKINS
        for skin in skins:
            self.grid.add_widget(
                SkinCard(skin, self._tab, self.save_ref, self._on_purchase)
            )

    def _on_purchase(self):
        self.coins_lbl.text = f"[b]{self.save_ref['coins']}[/b] coins"
        self._build_list()


# ═══════════════════════════════════════════════════════════════
class GameScreen(FloatLayout):
    """All game logic and rendering lives here."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ── Load persistent save data ──────────────────────────
        self.save = load_save()

        # game state: idle | playing | dead
        self.state      = 'idle'
        self.score      = 0
        self.best_score = self.save['high_score']

        # bird
        self.bx   = 100.0
        self.by   = 300.0
        self.bvel = 0.0

        # pipes: list of [x, gap_center_y, scored_flag]
        self.pipes      = []
        self.pipe_timer = 0.0

        # scrolling
        self.gnd_scroll   = 0.0
        self.cloud_scroll = 0.0
        self.clouds       = []   # [(cx, cy, radius), ...]

        # ── Season state ──────────────────────────────────────
        self._cur_season   = 0      # index into SEASONS
        self._prev_season  = 0
        self._season_t     = 1.0    # 1.0 = fully in cur_season
        self._season_ann_t = 0.0    # announcement countdown (sec)

        # Pre-seeded star positions (x_frac, y_frac, radius_px)
        _rng = random.Random(42)
        self._stars = [
            (_rng.uniform(0.02, 0.98), _rng.uniform(0.05, 0.90), _rng.uniform(1.5, 3.5))
            for _ in range(55)
        ]

        # ── Trail state ──────────────────────────────────────
        self._trail = deque(maxlen=50)   # deque of (x, y) oldest→newest

        # ── Sound state ──────────────────────────────────────
        self._sounds = {}
        Clock.schedule_once(self._load_sounds, 0.3)

        # responsive sizing defaults (recalculated in _init_scene)
        self._bird_r   = 18.0
        self._pipe_w   = 65.0
        self._pipe_gap = 155.0
        self._ground_h = 70.0
        self._p_speed  = 3.0
        self._flap_vel = 7.5
        self._gravity  = -0.45
        self._max_fall = -10.0
        self._stripe_w = 38.0
        self._cap_h    = 22.0
        self._cap_pad  = 6.0

        # ── UI labels ──────────────────────────────────────────
        self.lbl_score = Label(
            text='', font_size='52sp', bold=True,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'top': 0.96},
            size_hint=(1, None), height='60dp',
        )
        self.lbl_info = Label(
            text='Tap  or  [Space]  to  Start',
            font_size='26sp', bold=True,
            color=(1, 1, 0, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.56},
            size_hint=(1, None), height='90dp',
            halign='center', valign='middle',
        )
        self.lbl_best = Label(
            text=f'Best: {self.best_score}' if self.best_score else '',
            font_size='20sp',
            color=(1, 1, 1, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.48},
            size_hint=(1, None), height='38dp',
            halign='center',
        )
        self.add_widget(self.lbl_score)
        self.add_widget(self.lbl_info)
        self.add_widget(self.lbl_best)

        # ── Season announcement (centre, fades in/out) ─────────
        self.lbl_season = Label(
            text='', font_size='20sp', bold=True,
            color=(1, 0.95, 0.25, 1),
            pos_hint={'center_x': 0.5, 'top': 0.90},
            size_hint=(1, None), height='32dp',
            halign='center',
            opacity=0,
        )
        self.add_widget(self.lbl_season)

        # ── Coins display (bottom-left, idle/dead only) ────────
        self.lbl_coins = Label(
            text=f"Coins: {self.save['coins']}",
            font_size='14sp', bold=True,
            color=(1, 0.90, 0.20, 1),
            pos_hint={'x': 0.03, 'y': 0.004},
            size_hint=(0.45, None), height=dp(28),
            halign='left', valign='middle',
        )
        self.lbl_coins.bind(size=self.lbl_coins.setter('text_size'))
        self.add_widget(self.lbl_coins)

        # ── Shop button (bottom-right, idle/dead only) ─────────
        self.btn_shop = Button(
            text='SHOP', font_size='14sp', bold=True,
            size_hint=(None, None), size=(dp(68), dp(28)),
            pos_hint={'right': 0.97, 'y': 0.004},
            background_normal='',
            background_color=(0.90, 0.62, 0.04, 1),
        )
        self.btn_shop.bind(on_press=self._open_shop)
        self.add_widget(self.btn_shop)

        self._shop = None
        self._update_hud()

        self.bind(size=self._on_layout)
        Window.bind(on_key_down=self._on_key)
        Clock.schedule_once(self._on_layout, 0)
        Clock.schedule_interval(self._tick, 1 / 60.0)

    # ── Layout / scene init ─────────────────────────────────────
    def _on_layout(self, *_):
        self._init_scene()

    def _init_scene(self):
        w = self.width  or 400
        h = self.height or 600

        # ── Responsive sizing (scales to any screen) ───────────
        self._bird_r   = w * 0.058          # bird radius
        self._pipe_w   = w * 0.163          # pipe width
        self._pipe_gap = h * 0.260          # gap between pipes
        self._ground_h = h * 0.117          # ground strip height
        self._p_speed  = w * 0.0075         # pipe/scroll speed px/frame
        self._flap_vel = h * 0.0125         # upward velocity on flap
        self._gravity  = -h * 0.00075       # gravity per frame
        self._max_fall = -h * 0.0167        # terminal velocity
        self._stripe_w = max(20, w * 0.09)  # ground stripe width
        self._cap_h    = max(10, w * 0.055) # pipe cap height
        self._cap_pad  = max(4,  w * 0.015) # pipe cap side padding

        self.bx         = w * 0.25
        self.by         = h * 0.55
        self.bvel       = 0.0
        self.pipes      = []
        self.pipe_timer = 0.0
        self.gnd_scroll = 0.0
        self.cloud_scroll = 0.0
        self.clouds = [
            (random.uniform(0.05, 0.95) * w,
             random.uniform(0.60, 0.90) * h,
             random.uniform(w * 0.07, w * 0.13))
            for _ in range(6)
        ]
        # Reset season to Spring on every new scene
        self._cur_season   = 0
        self._prev_season  = 0
        self._season_t     = 1.0
        self._season_ann_t = 0.0
        self.lbl_season.text    = ''
        self.lbl_season.opacity = 0
        self._trail.clear()
        self._render()

    # ── Input ───────────────────────────────────────────────────
    def _on_key(self, _win, key, *args):
        if key == 32:   # Space bar
            self._flap()

    def on_touch_down(self, touch):
        # Let child widgets (shop button, shop overlay) handle their touch first
        if super().on_touch_down(touch):
            return True
        self._flap()
        return True

    def _flap(self):
        if self.state == 'idle':
            self.state          = 'playing'
            self.score          = 0
            self.lbl_score.text = '0'
            self.lbl_info.text  = ''
            self.lbl_best.text  = ''
            self.bvel           = self._flap_vel
            self._update_hud()
        elif self.state == 'playing':
            self.bvel = self._flap_vel
        elif self.state == 'dead':
            self.state = 'idle'
            self._init_scene()
            self.lbl_info.text = 'Tap  or  [Space]  to  Start'
            self.lbl_best.text = f'Best: {self.best_score}' if self.best_score else ''
            self._update_hud()

    # ── HUD visibility ──────────────────────────────────────────
    def _update_hud(self):
        visible = self.state != 'playing'
        self.btn_shop.opacity  = 1 if visible else 0
        self.btn_shop.disabled = not visible
        self.lbl_coins.opacity = 1 if visible else 0
        self.lbl_coins.text    = f"Coins: {self.save['coins']}"

    # ── Shop ────────────────────────────────────────────────────
    def _open_shop(self, *_):
        if self.state == 'playing' or self._shop:
            return
        self._shop = ShopOverlay(
            self.save,
            on_close=self._close_shop,
            size_hint=(1, 1),
        )
        self.add_widget(self._shop)

    def _close_shop(self):
        if self._shop:
            self.remove_widget(self._shop)
            self._shop = None
        self._update_hud()
        self._render()

    # ── Game loop ───────────────────────────────────────────────
    def _tick(self, dt):
        if self.state == 'playing':
            # Physics
            self.bvel = max(self.bvel + self._gravity, self._max_fall)
            self.by  += self.bvel

            # Scroll offsets
            self.gnd_scroll  = (self.gnd_scroll  + self._p_speed)       % self._stripe_w
            self.cloud_scroll = (self.cloud_scroll + self._p_speed * 0.4) % (self.width + 200)

            # Spawn pipes
            self.pipe_timer += dt
            if self.pipe_timer >= PIPE_INTERVAL:
                self.pipe_timer = 0.0
                h     = self.height
                gap_y = random.randint(
                    int(self._ground_h + self._pipe_gap / 2 + self._pipe_gap * 0.13),
                    int(h - self._pipe_gap / 2 - self._pipe_gap * 0.13),
                )
                self.pipes.append([self.width + self._pipe_w, gap_y, False])

            # Move pipes + scoring
            for p in self.pipes:
                p[0] -= self._p_speed
                if not p[2] and p[0] + self._pipe_w < self.bx:
                    p[2]   = True
                    self.score += 1
                    self.lbl_score.text = str(self.score)
                    self._play('score')

            self.pipes = [p for p in self.pipes if p[0] > -(self._pipe_w + 10)]

            # Scroll existing trail points left with the world, then record current position
            for i in range(len(self._trail)):
                self._trail[i] = (self._trail[i][0] - self._p_speed, self._trail[i][1])
            self._trail.append((self.bx, self.by))

            # ── Season logic ────────────────────────────────────────────
            target = (self.score // SEASON_THRESHOLD) % len(SEASONS)
            if target != self._cur_season and self._season_t >= 1.0:
                self._prev_season  = self._cur_season
                self._cur_season   = target
                self._season_t     = 0.0
                self._season_ann_t = 3.2
                self.lbl_season.text    = SEASONS[target]['name']
                self.lbl_season.opacity = 1.0
                self._play('season')

            if self._season_t < 1.0:
                self._season_t = min(1.0, self._season_t + dt / 1.8)

            if self._season_ann_t > 0:
                self._season_ann_t -= dt
                self.lbl_season.opacity = max(0.0, min(1.0, self._season_ann_t))
                if self._season_ann_t <= 0:
                    self.lbl_season.text    = ''
                    self.lbl_season.opacity = 0

            # Collision
            if self._hit():
                self._die()

        self._render()

    def _die(self):
        """Handle death: award coins, update high score, persist to disk."""
        self.state  = 'dead'
        self._play('die')
        earned      = self.score
        self.save['coins'] += earned
        if self.score > self.save['high_score']:
            self.save['high_score'] = self.score
        self.best_score = self.save['high_score']
        write_save(self.save)
        self.lbl_info.text = f'Game  Over!\n+{earned} coins'
        self.lbl_best.text = f'Best: {self.best_score}    Tap to Restart'
        self._update_hud()

    # ── Collision detection ─────────────────────────────────────
    def _hit(self):
        bx, by = self.bx, self.by
        r = self._bird_r * 0.78     # slightly forgiving hitbox

        # Ground / ceiling
        if by - r <= self._ground_h or by + r >= self.height:
            return True

        # Pipes
        for px, gap_y, _ in self.pipes:
            if bx + r > px and bx - r < px + self._pipe_w:
                if by + r > gap_y + self._pipe_gap / 2 or by - r < gap_y - self._pipe_gap / 2:
                    return True
        return False

    # ── Rendering ───────────────────────────────────────────────
    def _render(self):
        w, h = self.width, self.height
        if not w:
            return

        # Active skins
        bird_skin = next(
            (s for s in BIRD_SKINS if s['id'] == self.save.get('bird_skin')),
            BIRD_SKINS[0],
        )
        pipe_skin = next(
            (s for s in PIPE_SKINS if s['id'] == self.save.get('pipe_skin')),
            PIPE_SKINS[0],
        )

        # ── Interpolated season palette ──────────────────────────
        s1       = SEASONS[self._prev_season]
        s2       = SEASONS[self._cur_season]
        t        = self._season_t
        sky_c    = lerp_color(s1['sky'],     s2['sky'],     t)
        gnd_c    = lerp_color(s1['ground'],  s2['ground'],  t)
        grass_c  = lerp_color(s1['grass'],   s2['grass'],   t)
        stripe_c = lerp_color(s1['stripe'],  s2['stripe'],  t)
        cloud_c  = lerp_color(s1['cloud'],   s2['cloud'],   t)
        amb_c    = lerp_color(s1['ambient'], s2['ambient'], t)
        # Star / moon alpha: fade in entering Night, fade out leaving Night
        if s2['stars']:
            star_alpha = t
        elif s1['stars']:
            star_alpha = 1.0 - t
        else:
            star_alpha = 0.0

        angle  = max(-30.0, min(30.0, self.bvel * 3.5))
        gh     = self._ground_h
        pw     = self._pipe_w
        pg     = self._pipe_gap
        r      = self._bird_r
        cap_h  = self._cap_h
        cap_pd = self._cap_pad
        pb     = pipe_skin['body']
        pc     = pipe_skin['cap']
        phi    = pipe_skin['hi']
        hi_w   = max(4, pw * 0.14)

        self.canvas.before.clear()
        with self.canvas.before:

            # ─── Sky ───────────────────────────────────────────
            Color(*sky_c)
            Rectangle(pos=(0, gh), size=(w, h - gh))

            # ─── Stars & Moon (Night season) ───────────────────
            if star_alpha > 0.01:
                sky_top = h - gh
                for sx_f, sy_f, sz in self._stars:
                    star_x = sx_f * w
                    star_y = gh + sy_f * sky_top * 0.92
                    Color(1.0, 1.0, 0.88, star_alpha * 0.9)
                    Ellipse(pos=(star_x - sz / 2, star_y - sz / 2), size=(sz, sz))
                # Moon
                mr = w * 0.065
                mx, my = w * 0.78, h * 0.82
                Color(1.0, 1.0, 0.72, star_alpha * 0.20)    # soft glow
                Ellipse(pos=(mx - mr * 1.8, my - mr * 1.8), size=(mr * 3.6, mr * 3.6))
                Color(0.97, 0.97, 0.80, star_alpha)          # moon disc
                Ellipse(pos=(mx - mr, my - mr), size=(mr * 2, mr * 2))
                Color(sky_c[0], sky_c[1], sky_c[2], star_alpha * 0.88)  # crescent shadow
                Ellipse(pos=(mx - mr * 0.60, my - mr * 0.95), size=(mr * 1.8, mr * 1.9))

            # ─── Clouds ────────────────────────────────────────
            for cx, cy, cr in self.clouds:
                sx = (cx - self.cloud_scroll) % (w + cr * 3) - cr * 1.5
                Color(*cloud_c)
                Ellipse(pos=(sx - cr,        cy - cr * 0.55), size=(cr * 2,    cr * 1.10))
                Ellipse(pos=(sx - cr * 0.4,  cy - cr * 0.25), size=(cr * 1.40, cr * 0.85))
                Ellipse(pos=(sx + cr * 0.30, cy - cr * 0.45), size=(cr * 1.15, cr * 0.90))

            # ─── Pipes ─────────────────────────────────────────
            for px, gap_y, _ in self.pipes:
                top_y   = gap_y + pg / 2
                bot_top = gh + pw * 0.12
                bot_h   = max(0, (gap_y - pg / 2) - bot_top)

                # Bottom pipe body
                Color(*pb)
                Rectangle(pos=(px, bot_top), size=(pw, bot_h))
                # Bottom pipe cap
                Color(*pc)
                Rectangle(pos=(px - cap_pd, gap_y - pg / 2 - cap_h),
                          size=(pw + cap_pd * 2, cap_h))
                # Bottom pipe highlight
                Color(phi[0], phi[1], phi[2], 0.55)
                Rectangle(pos=(px + pw * 0.12, bot_top + 2), size=(hi_w, max(0, bot_h - 4)))

                # Top pipe body
                Color(*pb)
                Rectangle(pos=(px, top_y), size=(pw, h - top_y))
                # Top pipe cap
                Color(*pc)
                Rectangle(pos=(px - cap_pd, top_y), size=(pw + cap_pd * 2, cap_h))
                # Top pipe highlight
                Color(phi[0], phi[1], phi[2], 0.55)
                Rectangle(pos=(px + pw * 0.12, top_y + cap_h + 2), size=(hi_w, h - top_y - cap_h - 4))

            # ─── Ground ────────────────────────────────────────
            grass_h = max(8, gh * 0.2)
            Color(*gnd_c)
            Rectangle(pos=(0, 0), size=(w, gh))
            Color(*grass_c)
            Rectangle(pos=(0, gh - grass_h * 0.4), size=(w, grass_h))
            # Scrolling grass stripes
            Color(*stripe_c)
            stripe = self._stripe_w
            for i in range(-1, int(w / stripe) + 2):
                sx = i * stripe - (self.gnd_scroll % stripe)
                Rectangle(pos=(sx, gh - grass_h * 0.4), size=(stripe * 0.5, grass_h))

            # ─── Trail ───────────────────────────────────────────
            self._draw_trail(bird_skin, r)

            # ─── Bird ──────────────────────────────────────────
            bx, by = self.bx, self.by

            PushMatrix()
            Translate(bx, by, 0)
            if self.state == 'playing':
                Rotate(angle=angle, axis=(0, 0, 1), origin=(0, 0, 0))

            # Drop shadow
            Color(0, 0, 0, 0.15)
            Ellipse(pos=(-r * 0.9, -r * 1.15), size=(r * 1.8, r * 0.5))
            # Body
            Color(*bird_skin['body'])
            Ellipse(pos=(-r, -r), size=(r * 2, r * 2))
            # Belly
            Color(*bird_skin['belly'])
            Ellipse(pos=(-r * 0.25, -r * 0.70), size=(r * 1.10, r * 0.85))
            # Wing
            wing_dy = r * 0.15 if self.bvel > 0 else -r * 0.12
            Color(*bird_skin['wing'])
            Ellipse(pos=(-r * 0.65, -r * 0.10 + wing_dy), size=(r * 1.10, r * 0.55))
            # Eye white
            Color(1, 1, 1)
            Ellipse(pos=(r * 0.18, r * 0.16), size=(r * 0.58, r * 0.58))
            # Pupil
            Color(0.05, 0.05, 0.35)
            Ellipse(pos=(r * 0.31, r * 0.23), size=(r * 0.32, r * 0.32))
            # Glint
            Color(1, 1, 1)
            Ellipse(pos=(r * 0.42, r * 0.42), size=(r * 0.12, r * 0.12))
            # Beak
            Color(*bird_skin['beak'])
            Triangle(points=[
                r * 0.82,  r * 0.18,
                r * 0.82, -r * 0.10,
                r * 1.30,  r * 0.05,
            ])
            PopMatrix()

            # ─── Seasonal ambient lighting overlay ─────────────
            if amb_c[3] > 0.004:
                Color(amb_c[0], amb_c[1], amb_c[2], amb_c[3])
                Rectangle(pos=(0, 0), size=(w, h))

            # ─── Death red overlay ─────────────────────────────
            if self.state == 'dead':
                Color(1, 0.2, 0.2, 0.12)
                Rectangle(pos=(0, 0), size=(w, h))

    # ── Trail rendering ──────────────────────────────────
    def _draw_trail(self, bird_skin, r):
        tid = self.save.get('trail_skin', 'trail_none')
        if tid == 'trail_none' or len(self._trail) < 3:
            return
        trail = list(self._trail)   # [oldest, ..., newest]
        n = len(trail)

        if tid == 'trail_sparkle':
            # White / gold glitter — scattered stars & dots with y-jitter
            _SPARKLE = [
                (1.0, 1.0, 1.0), (1.0, 0.95, 0.55), (1.0, 0.82, 0.20),
                (0.82, 0.95, 1.0), (1.0, 0.80, 0.92), (0.90, 1.0, 0.72),
            ]
            for i in range(0, n, 2):
                af     = i / max(1, n - 1)
                jitter = ((i * 7 + 3) % 11 - 5) * r * 0.28
                sz     = max(1, r * (0.18 + 0.30 * af) * (0.7 + (i % 3) * 0.18))
                c      = _SPARKLE[i % len(_SPARKLE)]
                tx, ty = trail[i][0], trail[i][1] + jitter
                Color(c[0], c[1], c[2], af * 0.90)
                if i % 4 == 0:   # star shape
                    Triangle(points=[tx, ty+sz, tx-sz*0.50, ty-sz*0.35, tx+sz*0.50, ty-sz*0.35])
                    Triangle(points=[tx, ty-sz, tx-sz*0.50, ty+sz*0.35, tx+sz*0.50, ty+sz*0.35])
                else:             # glitter dot
                    Ellipse(pos=(tx-sz/2, ty-sz/2), size=(sz, sz))

        elif tid == 'trail_rainbow':
            # Smooth full-spectrum ribbon — large overlapping blobs with soft glow
            step = max(1, n // 18)
            for idx, i in enumerate(range(0, n, step)):
                af = i / max(1, n - 1)
                sz = max(2, r * 0.95 * (0.20 + af * 0.80))
                c  = _RAINBOW[idx % len(_RAINBOW)]
                # Outer glow
                Color(c[0], c[1], c[2], af * 0.28)
                Ellipse(pos=(trail[i][0]-sz*0.75, trail[i][1]-sz*0.75), size=(sz*1.5, sz*1.5))
                # Core dot
                Color(c[0], c[1], c[2], af * 0.88)
                Ellipse(pos=(trail[i][0]-sz/2, trail[i][1]-sz/2), size=(sz, sz))

        elif tid == 'trail_fire':
            for i in range(0, n, 2):
                af    = i / max(1, n - 1)
                drift = (n - i) * 1.6
                sz    = max(1, r * (0.14 + af * 0.68))
                c = (1.0,0.90,0.20) if af>0.65 else (1.0,0.42,0.06) if af>0.35 else (0.82,0.10,0.02)
                Color(c[0], c[1], c[2], af * 0.80)
                Ellipse(pos=(trail[i][0]-sz/2, trail[i][1]-sz/2+drift), size=(sz, sz))

        elif tid == 'trail_ice':
            for i in range(0, n, 2):
                af = i / max(1, n - 1)
                sz = max(1, r * (0.14 + af * 0.55))
                c  = (0.88, 0.96, 1.0) if af > 0.5 else (0.35, 0.72, 1.0)
                Color(c[0], c[1], c[2], af * 0.72)
                Ellipse(pos=(trail[i][0]-sz/2, trail[i][1]-sz/2), size=(sz, sz))
                if af > 0.7:
                    gs = sz * 0.35
                    Color(1, 1, 1, af * 0.5)
                    Ellipse(pos=(trail[i][0]-gs/2+sz*0.15, trail[i][1]-gs/2+sz*0.15), size=(gs, gs))

        elif tid == 'trail_comet':
            bc = bird_skin['body']
            for i in range(0, n, 2):
                af = i / max(1, n - 1)
                sz = max(1, r * 1.85 * af)
                Color(bc[0], bc[1], bc[2], af * 0.28)
                Ellipse(pos=(trail[i][0]-sz/2, trail[i][1]-sz/2), size=(sz, sz))
                if af > 0.45:
                    cs = sz * 0.40
                    Color(1.0, 1.0, 0.95, af * 0.65)
                    Ellipse(pos=(trail[i][0]-cs/2, trail[i][1]-cs/2), size=(cs, cs))

        elif tid == 'trail_stars':
            for i in range(0, n, 5):
                af = i / max(1, n - 1)
                sz = max(1, r * 0.55 * af)
                tx, ty = trail[i]
                Color(1.0, 0.95, 0.30, af * 0.85)
                Triangle(points=[tx, ty+sz, tx-sz*0.58, ty-sz*0.38, tx+sz*0.58, ty-sz*0.38])
                Triangle(points=[tx, ty-sz, tx-sz*0.58, ty+sz*0.38, tx+sz*0.58, ty+sz*0.38])

        elif tid == 'trail_bubble':
            for i in range(0, n, 4):
                af    = i / max(1, n - 1)
                drift = (n - i) * 0.65
                sz    = max(1, r * 0.72 * af)
                Color(0.62, 0.90, 1.0, af * 0.22)
                Ellipse(pos=(trail[i][0]-sz/2, trail[i][1]-sz/2+drift), size=(sz, sz))

        elif tid == 'trail_hearts':
            for i in range(0, n, 6):
                af = i / max(1, n - 1)
                sz = max(1, r * 0.55 * af)
                tx, ty = trail[i]
                Color(1.0, 0.28, 0.45, af * 0.78)
                Ellipse(pos=(tx - sz*0.85, ty), size=(sz*0.85, sz*0.85))
                Ellipse(pos=(tx,           ty), size=(sz*0.85, sz*0.85))
                Triangle(points=[tx-sz*0.85, ty, tx+sz*0.85, ty, tx, ty-sz*1.05])

        elif tid == 'trail_birds':
            # Tiny birds fly in formation alongside the main bird (not trailing behind)
            bc    = bird_skin['body']
            belly = bird_skin['belly']
            wing  = bird_skin['wing']
            beak  = bird_skin['beak']
            # (x_offset_mult, y_offset_mult, scale, alpha)
            formation = [
                (-3.8,  2.5, 0.52, 0.88),   # upper-left companion
                (-3.2, -2.2, 0.46, 0.75),   # lower-left companion
                (-6.0,  0.4, 0.36, 0.55),   # far-left companion
            ]
            wing_dy_mult = 0.15 if self.bvel > 0 else -0.12
            for dx_m, dy_m, scale, alpha in formation:
                tx = self.bx + dx_m * r
                ty = self.by + dy_m * r
                mr = r * scale
                wdy = mr * wing_dy_mult
                PushMatrix()
                Translate(tx, ty, 0)
                # Shadow
                Color(0, 0, 0, alpha * 0.10)
                Ellipse(pos=(-mr*0.9, -mr*1.12), size=(mr*1.8, mr*0.45))
                # Body
                Color(bc[0], bc[1], bc[2], alpha)
                Ellipse(pos=(-mr, -mr), size=(mr*2, mr*2))
                # Belly
                Color(belly[0], belly[1], belly[2], alpha)
                Ellipse(pos=(-mr*0.22, -mr*0.68), size=(mr*1.05, mr*0.82))
                # Wing
                Color(wing[0], wing[1], wing[2], alpha)
                Ellipse(pos=(-mr*0.65, -mr*0.10 + wdy), size=(mr*1.10, mr*0.55))
                # Eye
                Color(1, 1, 1, alpha)
                Ellipse(pos=(mr*0.18, mr*0.16), size=(mr*0.52, mr*0.52))
                Color(0.05, 0.05, 0.35, alpha)
                Ellipse(pos=(mr*0.30, mr*0.22), size=(mr*0.28, mr*0.28))
                # Beak
                Color(beak[0], beak[1], beak[2], alpha)
                Triangle(points=[mr*0.80, mr*0.15, mr*0.80, -mr*0.08, mr*1.22, mr*0.04])
                PopMatrix()

    # ── Sound helpers ──────────────────────────────────
    def _load_sounds(self, *_):
        try:
            from kivy.core.audio import SoundLoader
            data_dir = os.path.dirname(_save_path())
            for name, path in _ensure_sounds(data_dir).items():
                snd = SoundLoader.load(path)
                if snd:
                    snd.volume = 0.65
                    self._sounds[name] = snd
        except Exception:
            pass

    def _play(self, name):
        snd = self._sounds.get(name)
        if snd:
            try:
                snd.stop()
                snd.play()
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════
class FlappyApp(App):
    title = 'Flappy Bird'

    def build(self):
        Window.clearcolor = (0.38, 0.68, 0.94, 1)
        return GameScreen()


if __name__ == '__main__':
    FlappyApp().run()
