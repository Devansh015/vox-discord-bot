# Discord Voice Chat Summarizer Bot

A Discord bot that can join voice channels, record conversations, and transcribe them using OpenAI's Whisper.

## Features

- 🔊 Join and leave voice channels
- 🎤 Record voice chat conversations  
- 📝 Transcribe audio using Whisper AI
- 💾 Save recordings for later transcription
- 🤖 Easy-to-use Discord commands

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Create a `.env` file with:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   OPENAI_API_KEY=your_openai_api_key  # Optional, only needed for OpenAI Whisper API
   ```

3. **Discord Bot Setup**
   - Create a Discord application at https://discord.com/developers/applications
   - Create a bot and copy the token
   - Enable the following bot permissions:
     - Send Messages
     - Use Voice Activity
     - Connect (Voice)
     - Speak (Voice)
   - Invite the bot to your server

4. **Run the Bot**
   ```bash
   python bot.py
   ```

## Commands

- `!join` - Bot joins your current voice channel
- `!leave` - Bot leaves the voice channel
- `!record` - Start recording voice chat
- `!stop` - Stop recording and save audio file
- `!transcribe_last` - Transcribe the last recording
- `!transcribe` - Transcribe sample audio (for testing)
- `!help_bot` - Show all available commands

## How to Use

1. Join a voice channel in Discord
2. Use `!join` to invite the bot to your channel
3. Use `!record` to start recording the conversation
4. Talk or have others talk in the voice channel
5. Use `!stop` to stop recording
6. Use `!transcribe_last` to get the transcription

## Technical Notes

- Uses OpenAI's Whisper for local transcription (no API calls required)
- Recordings are saved as WAV files in the `recordings/` folder
- The bot uses discord.py's voice functionality
- Audio is processed using PyDub and Whisper

## Troubleshooting

### Bot Won't Join Voice Channel
- Make sure the bot has "Connect" and "Speak" permissions
- Ensure you're in a voice channel when using `!join`

### Audio Recording Issues
- Discord audio recording is complex - the current implementation is a simplified version
- For production use, you might need more sophisticated audio processing

### Transcription Not Working
- Make sure Whisper is properly installed: `pip install openai-whisper`
- First run will download the Whisper model (this may take time)
- Check that audio files exist in the recordings folder

### Dependencies
- Python 3.8+
- discord.py[voice]
- openai-whisper  
- PyNaCl (for Discord voice)
- python-dotenv
- pydub

## File Structure

```
discord-vc-summarizer-bot/
├── bot.py                 # Main bot script
├── config.py             # Configuration loading
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── audio/
│   ├── recorder.py       # Voice recording functionality
│   └── audio_utils.py    # Audio processing utilities
├── transcription/
│   └── whisper_api.py    # Whisper transcription
└── recordings/           # Saved audio files
    └── sample.wav        # Sample audio for testing
```

## Important Notes

- This is a basic implementation for educational purposes
- Discord's audio API is complex, and real-time recording requires more sophisticated handling
- Always respect privacy and get consent before recording conversations
- Be mindful of Discord's Terms of Service regarding bots and audio recording

## Future Improvements

- [ ] Real-time audio streaming and processing
- [ ] Multi-user audio separation
- [ ] Audio quality improvements
- [ ] Database storage for transcriptions
- [ ] Web interface for managing recordings
- [ ] Support for different Whisper models
