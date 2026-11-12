"""Check the installed American male voice without touching the original film."""
from pathlib import Path
import win32com.client

root = Path(__file__).resolve().parent
voice = win32com.client.Dispatch('SAPI.SpVoice')
tokens = voice.GetVoices()
voice.Voice = next(tokens.Item(i) for i in range(tokens.Count)
                   if 'DAVID' in tokens.Item(i).Id.upper())
voice.Rate = 0
voice.Volume = 95
stream = win32com.client.Dispatch('SAPI.SpFileStream')
stream.Open(str(root/'narration/voice_sample.wav'), 3, False)
voice.AudioOutputStream = stream
try:
    voice.Speak('<pitch absmiddle="2">A short circuit can unleash enormous current! '
                '<silence msec="200"/>Watch how this limiter brings it under control.</pitch>', 8)
finally:
    stream.Close()
print('VOICE_SAMPLE_CREATED', voice.Voice.GetDescription())
