"""مولّد أكواد التفعيل (Kivy) — للمالك فقط، لا تضعه داخل التطبيق.

التشغيل:
    python keygen_kivy.py
(ويمكن استخدامه من سطر الأوامر:)
    python keygen_kivy.py <DEVICE-ID> <DAYS>
"""
import os
import sys
import hmac
import hashlib

SECRET_KEY = b"CHANGE-THIS-SECRET-KEY-BEFORE-RELEASE"   # يجب أن يطابق rate_kivy.py


def make_code(device_id, days):
    msg = f"{device_id.strip().upper()}|{int(days):04d}".encode()
    sig = hmac.new(SECRET_KEY, msg, hashlib.sha256).hexdigest()[:12].upper()
    return f"{int(days):04d}-{sig[0:4]}-{sig[4:8]}-{sig[8:12]}"


# ---------------------------------------------------------------- CLI mode
if len(sys.argv) == 3:
    print(make_code(sys.argv[1], sys.argv[2]))
    sys.exit(0)

# ---------------------------------------------------------------- GUI mode
from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import platform

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def ar(text):
        return get_display(arabic_reshaper.reshape(text))
except ImportError:          # pip install arabic-reshaper python-bidi
    def ar(text):
        return text

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "Roboto"
_sahel = os.path.join(HERE, "Sahel.ttf")
if os.path.exists(_sahel):
    LabelBase.register(name="Sahel", fn_regular=_sahel)
    FONT = "Sahel"

# ------------------------------------------------------------- palette
BG = (0.05, 0.06, 0.09, 1)
CARD = (0.10, 0.12, 0.17, 1)
FIELD = (0.14, 0.17, 0.24, 1)
ACCENT = (0.25, 0.52, 0.98, 1)
ACCENT2 = (0.55, 0.38, 0.98, 1)
GREEN = (0.20, 0.78, 0.52, 1)
RED = (0.96, 0.38, 0.42, 1)
TEXT = (0.93, 0.95, 1, 1)
MUTED = (0.62, 0.67, 0.78, 1)


# ------------------------------------------------------------- widgets
class Panel(BoxLayout):
    """BoxLayout with a rounded background."""

    def __init__(self, bg=CARD, radius=16, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self._col = Color(*bg)
            self._rect = RoundedRectangle(radius=[dp(radius)])
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._rect.pos, self._rect.size = self.pos, self.size

    def set_bg(self, rgba):
        self._col.rgba = rgba


class RoundButton(Button):
    def __init__(self, bg=ACCENT, radius=14, **kw):
        kw.setdefault("font_name", FONT)
        kw.setdefault("font_size", "16sp")
        kw.setdefault("bold", True)
        kw.setdefault("color", (1, 1, 1, 1))
        super().__init__(background_normal="", background_down="",
                         background_color=(0, 0, 0, 0), **kw)
        self._bg = bg
        with self.canvas.before:
            self._col = Color(*bg)
            self._rect = RoundedRectangle(radius=[dp(radius)])
        self.bind(pos=self._sync, size=self._sync,
                  state=self._paint, disabled=self._paint)

    def _sync(self, *_):
        self._rect.pos, self._rect.size = self.pos, self.size

    def _paint(self, *_):
        r, g, b, a = self._bg
        if self.disabled:
            self._col.rgba = (r, g, b, 0.30)
            self.color = (1, 1, 1, 0.45)
        elif self.state == "down":
            self._col.rgba = (r * 0.75, g * 0.75, b * 0.75, a)
        else:
            self._col.rgba = self._bg
            self.color = (1, 1, 1, 1)


class Field(Panel):
    """Rounded text field."""

    def __init__(self, hint, input_filter=None, **kw):
        super().__init__(bg=FIELD, radius=12, size_hint_y=None,
                         height=dp(52), padding=(dp(6), 0), **kw)
        self.input = TextInput(
            hint_text=ar(hint), font_name=FONT, font_size="17sp",
            multiline=False, halign="center", write_tab=False,
            background_normal="", background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT, hint_text_color=(*MUTED[:3], 0.55),
            cursor_color=ACCENT, selection_color=(*ACCENT[:3], 0.35),
            padding=(dp(10), dp(15)),
            input_filter=input_filter)
        self.add_widget(self.input)
        self.input.bind(focus=lambda _w, f: self.set_bg(
            (0.18, 0.22, 0.32, 1) if f else FIELD))


def label(text, size="14sp", color=MUTED, h=24, align="right", **kw):
    l = Label(text=ar(text), font_name=FONT, font_size=size, color=color,
              size_hint_y=None, height=dp(h), halign=align, valign="middle", **kw)
    l.bind(size=lambda w, s: setattr(w, "text_size", s))
    return l


# ------------------------------------------------------------- app
class KeygenApp(App):
    title = "Activation Keygen"

    def build(self):
        Window.clearcolor = BG
        if platform in ("win", "linux", "macosx"):
            Window.size = (dp(400), dp(680))

        outer = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(14))

        # ---- header
        header = BoxLayout(orientation="vertical", size_hint_y=None,
                           height=dp(74), spacing=dp(2))
        header.add_widget(label("مولّد أكواد التفعيل", "24sp", TEXT, 40, "center",
                                bold=True))
        header.add_widget(label("لوحة المالك • لا تضعها داخل التطبيق", "12sp",
                                MUTED, 22, "center"))
        outer.add_widget(header)

        # ---- input card
        card = Panel(orientation="vertical", padding=dp(18), spacing=dp(8),
                     size_hint_y=None, height=dp(260))
        card.add_widget(label("معرّف الجهاز (Device ID)", "13sp"))

        row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        self.paste_btn = RoundButton(bg=ACCENT2, text=ar("لصق"),
                                     size_hint=(None, 1), width=dp(84),
                                     font_size="15sp")
        self.paste_btn.bind(on_release=self.paste)
        self.device = Field("A1B2-C3D4-E5F6")
        row.add_widget(self.paste_btn)
        row.add_widget(self.device)
        card.add_widget(row)

        card.add_widget(Widget(size_hint_y=None, height=dp(2)))
        card.add_widget(label("عدد الأيام  (0 = اشتراك دائم)", "13sp"))
        self.days = Field("30", input_filter="int")
        card.add_widget(self.days)

        card.add_widget(Widget(size_hint_y=None, height=dp(6)))
        gen = RoundButton(bg=ACCENT, text=ar("توليد الكود"),
                          size_hint_y=None, height=dp(52))
        gen.bind(on_release=self.generate)
        card.add_widget(gen)
        outer.add_widget(card)

        # ---- result card
        res = Panel(orientation="vertical", padding=dp(18), spacing=dp(6),
                    size_hint_y=None, height=dp(190))
        res.add_widget(label("الكود الناتج", "13sp"))
        self.box = Panel(bg=FIELD, radius=12)
        self.result = Label(text="", font_name="Roboto", font_size="26sp",
                            bold=True, color=GREEN)
        self.box.add_widget(self.result)
        res.add_widget(self.box)
        self.status = label("", "13sp", MUTED, 22, "center")
        res.add_widget(self.status)
        self.copy_btn = RoundButton(bg=GREEN, text=ar("نسخ الكود"),
                                    size_hint_y=None, height=dp(46),
                                    disabled=True)
        self.copy_btn.bind(on_release=self.copy)
        res.add_widget(self.copy_btn)
        outer.add_widget(res)

        outer.add_widget(Widget())  # spacer

        self.device.input.bind(
            on_text_validate=lambda *_: setattr(self.days.input, "focus", True))
        self.days.input.bind(on_text_validate=self.generate)
        return outer

    # ---- helpers
    def say(self, msg, color=MUTED):
        self.status.text = ar(msg)
        self.status.color = color

    def fail(self, msg):
        self.result.text = ""
        self.copy_btn.disabled = True
        self.say(msg, RED)

    # ---- actions
    def paste(self, *_):
        text = (Clipboard.paste() or "").strip()
        if not text:
            return self.say("الحافظة فارغة", RED)
        self.device.input.text = text.splitlines()[0].strip()
        self.say("تم اللصق", GREEN)

    def generate(self, *_):
        dev = self.device.input.text.strip()
        if not dev:
            return self.fail("أدخل معرّف الجهاز")
        try:
            days = int(self.days.input.text or "")
            if not 0 <= days <= 9999:
                raise ValueError
        except ValueError:
            return self.fail("عدد الأيام يجب أن يكون بين 0 و 9999")

        self.result.text = make_code(dev, days)
        self.copy_btn.disabled = False
        self.say("اشتراك دائم" if days == 0 else f"اشتراك لمدة {days} يوماً", MUTED)

    def copy(self, *_):
        if self.result.text:
            Clipboard.copy(self.result.text)
            self.say("تم نسخ الكود", GREEN)


if __name__ == "__main__":
    KeygenApp().run()
