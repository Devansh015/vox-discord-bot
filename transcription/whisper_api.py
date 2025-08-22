import whisper

model = whisper.load_model("base")  # You can use "tiny", "base", "small", "medium", "large"

def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]
