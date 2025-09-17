from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
import requests
import pygame
import arabic_reshaper
from kivy.clock import Clock

FONT_PATH = "/system/fonts/NotoNaskhArabic-Regular.ttf"

def fix_farsi_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return reshaped[::-1]

HINT_TEXT = fix_farsi_text("متن خود را وارد کنید")
BUTTON_TEXT = fix_farsi_text("تبدیل به گفتار")
STATUS_DEFAULT = fix_farsi_text("وضعیت")

KV = f"""
BoxLayout:
    orientation: 'vertical'
    spacing: dp(10)
    padding: dp(10)

    MDTextField:
        id: input_text
        hint_text: "{HINT_TEXT}"
        font_name: "{FONT_PATH}"
        multiline: True
        halign: "left"
        size_hint_y: 0.6

    MDRaisedButton:
        id: convert_button
        text: "{BUTTON_TEXT}"
        font_name: "{FONT_PATH}"
        size_hint_y: 0.15
        pos_hint: {{"center_x": 0.5}}

    MDLabel:
        id: status_label
        text: "{STATUS_DEFAULT}"
        font_name: "{FONT_PATH}"
        size_hint_y: 0.25
        halign: "center"
"""

class TextToSpeechApp(MDApp):
    def build(self):
        self.root_widget = Builder.load_string(KV)
        self.root_widget.ids.convert_button.bind(on_press=self.convert_and_play)
        return self.root_widget

    def convert_and_play(self, instance):
        text = self.root_widget.ids.input_text.text.strip()
        if not text:
            self.root_widget.ids.status_label.text = fix_farsi_text("متنی وارد نشده")
            return

        self.root_widget.ids.status_label.text = fix_farsi_text("در حال ارسال به سرور...")
        try:
            url = f"https://hakhamanesh-bot.ir/api/voice?text={text}"
            response = requests.get(url)
            data = response.json()

            if data.get("ok"):
                audio_url = data["audio_url"]
                audio_file = "output.mp3"

                audio_response = requests.get(audio_url)
                with open(audio_file, "wb") as f:
                    f.write(audio_response.content)

                
                Clock.schedule_once(lambda dt: self.update_label(text))

                
                pygame.mixer.quit()
                pygame.mixer.init()
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

            else:
                self.root_widget.ids.status_label.text = fix_farsi_text("خطا در پاسخ سرور")

        except Exception as e:
            self.root_widget.ids.status_label.text = fix_farsi_text(f"خطا: {e}")

    def update_label(self, text):
        self.root_widget.ids.status_label.text = fix_farsi_text(text)

if __name__ == "__main__":
    TextToSpeechApp().run()
