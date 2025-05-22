import whisper

model = whisper.load_model("base")
result = model.transcribe("recordings/sample.wav")
print("Transcription:")
print(result["text"])
