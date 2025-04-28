from gtts import gTTS
import os

def speak(text):
    tts = gTTS(text)
    tts.save("output.mp3")
