import discord
from discord.ext import commands
from transcription.whisper_api import transcribe_audio
from audio.recorder import voice_recorder
from audio.audio_utils import get_audio_duration
from dotenv import load_dotenv
from config import DISCORD_TOKEN
import os
import asyncio
import glob

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 Bot connected as {bot.user}')
    print(f'🆔 Bot ID: {bot.user.id}')
    print(f'📚 Discord.py version: {discord.__version__}')
    print('✅ Ready to record and transcribe voice chats!')

@bot.command()
async def join(ctx):
    """Join the user's voice channel"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            embed = discord.Embed(
                title="🔊 Joined Voice Channel!", 
                description=f"Connected to **{channel.name}**",
                color=0x00ff00
            )
            embed.add_field(name="🎤 Next Step", value="Use `!record` to start recording", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("🔊 Already connected to a voice channel!")
    else:
        await ctx.send("❌ You need to be in a voice channel first.")

@bot.command()
async def leave(ctx):
    """Leave the voice channel"""
    if ctx.voice_client:
        # Stop recording if active
        if voice_recorder.recording:
            voice_recorder.stop_recording()
            await ctx.send("⏹️ Stopped recording and left the channel.")
        else:
            await ctx.send("👋 Left the voice channel.")
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("❌ I'm not in a voice channel.")

@bot.command()
async def record(ctx):
    """Start recording Discord voice chat session"""
    if not ctx.voice_client:
        await ctx.send("❌ I need to be in a voice channel first. Use `!join` to join.")
        return
    
    if voice_recorder.recording:
        await ctx.send("⏸️ Already recording! Use `!stop` to stop recording.")
        return
    
    try:
        # Start recording session
        success = voice_recorder.start_recording(ctx.voice_client)
        
        if success:
            embed = discord.Embed(
                title="🎤 Recording Started!", 
                description="Voice chat recording is now active",
                color=0xff0000
            )
            embed.add_field(name="📢 Status", value="Listening to voice channel", inline=True)
            embed.add_field(name="⏹️ Stop", value="Use `!stop` when finished", inline=True)
            embed.add_field(name="📝 Transcribe", value="Use `!transcribe_last` after stopping", inline=True)
            embed.set_footer(text="🔐 Make sure you have permission to record this conversation!")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to start recording session.")
            
    except Exception as e:
        await ctx.send(f"❌ Error starting recording: {e}")

@bot.command()
async def stop(ctx):
    """Stop recording and process the audio"""
    if not voice_recorder.recording:
        await ctx.send("❌ Not currently recording. Use `!record` to start.")
        return
    
    await ctx.send("⏹️ **Stopping recording and processing...** 🔄")
    
    try:
        # Stop recording
        recording_info = voice_recorder.stop_recording()
        
        # Save the recording
        saved_info = await voice_recorder.save_combined_recording()
        
        if saved_info and saved_info.get('success'):
            # Send success info
            embed = discord.Embed(title="✅ Recording Saved!", color=0x00ff00)
            embed.add_field(name="⏱️ Duration", value=f"{saved_info['duration']:.1f} seconds", inline=True)
            embed.add_field(name="📁 File Size", value=f"{saved_info['file_size']:,} bytes", inline=True)
            embed.add_field(name="📂 Filename", value=os.path.basename(saved_info['filename']), inline=True)
            embed.add_field(name="🎯 Next Step", value="Use `!transcribe_last` to get transcription", inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("⚠️ Recording session completed, but no audio file could be created.")
            
    except Exception as e:
        await ctx.send(f"❌ Error processing recording: {e}")

@bot.command()
async def transcribe_last(ctx):
    """Transcribe the most recent recording and post results in chat"""
    recording_files = glob.glob("recordings/*.wav")
    if not recording_files:
        await ctx.send("❌ No recordings found. Use `!record` and `!stop` to create a recording first.")
        return
    
    latest_file = max(recording_files, key=os.path.getctime)
    
    embed = discord.Embed(
        title="🔄 Transcribing Audio...", 
        description="Processing your recording with AI",
        color=0xffff00
    )
    embed.add_field(name="📁 File", value=os.path.basename(latest_file), inline=True)
    embed.add_field(name="⏳ Status", value="Please wait...", inline=True)
    
    status_msg = await ctx.send(embed=embed)
    
    try:
        result = transcribe_audio(latest_file)
        
        if result and result.strip():
            duration = get_audio_duration(latest_file)
            file_size = os.path.getsize(latest_file)
            
            embed = discord.Embed(title="📝 Voice Chat Transcription", color=0x00ff00)
            embed.add_field(name="⏱️ Duration", value=f"{duration:.1f}s", inline=True)
            embed.add_field(name="📊 File Size", value=f"{file_size:,} bytes", inline=True)
            embed.add_field(name="📁 File", value=os.path.basename(latest_file), inline=True)
            
            if len(result) <= 1024:
                embed.add_field(name="🗣️ Transcription", value=f"```{result}```", inline=False)
            else:
                chunks = [result[i:i+1014] for i in range(0, len(result), 1014)]
                for i, chunk in enumerate(chunks[:3]):
                    field_name = f"🗣️ Transcription (Part {i+1})"
                    if len(chunks) > 3 and i == 2:
                        chunk += "... [truncated]"
                    embed.add_field(name=field_name, value=f"```{chunk}```", inline=False)
            
            await status_msg.edit(embed=embed)
            
        else:
            embed = discord.Embed(
                title="❌ No Speech Detected", 
                description="The AI couldn't find any speech in the recording",
                color=0xff9900
            )
            embed.add_field(
                name="💡 Try Again", 
                value="Record a longer session with clear speech", 
                inline=False
            )
            await status_msg.edit(embed=embed)
                         
    except Exception as e:
        embed = discord.Embed(
            title="❌ Transcription Error", 
            description=f"Something went wrong: {str(e)}",
            color=0xff0000
        )
        await status_msg.edit(embed=embed)

@bot.command()
async def transcribe(ctx):
    """Transcribe the sample audio file for testing"""
    file_path = "recordings/sample.wav"
    
    if not os.path.exists(file_path):
        await ctx.send("❌ Sample audio file not found.")
        return
        
    await ctx.send("🔄 Transcribing sample audio...")
    try:
        result = transcribe_audio(file_path)
        await ctx.send(f"📝 **Sample Transcription:**\n```{result}```")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def help_bot(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🤖 Discord Voice Transcriber Bot", 
        description="Voice channel recording and transcription",
        color=0x00ff00
    )
    
    embed.add_field(name="🔊 `!join`", value="Join your current voice channel", inline=False)
    embed.add_field(name="👋 `!leave`", value="Leave the voice channel", inline=False)
    embed.add_field(name="🎤 `!record`", value="Start recording voice chat", inline=False)
    embed.add_field(name="⏹️ `!stop`", value="Stop recording and save audio", inline=False)
    embed.add_field(name="📝 `!transcribe_last`", value="Transcribe the most recent recording", inline=False)
    embed.add_field(name="🧪 `!transcribe`", value="Transcribe sample audio (testing)", inline=False)
    
    embed.add_field(
        name="📋 **How to Use:**", 
        value="1️⃣ Join voice channel\n2️⃣ `!join`\n3️⃣ `!record`\n4️⃣ Talk\n5️⃣ `!stop`\n6️⃣ `!transcribe_last`", 
        inline=False
    )
    
    embed.set_footer(text="🔐 Always get consent before recording!")
    await ctx.send(embed=embed)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN not found!")
        exit(1)
    
    print("🚀 Starting Discord Voice Transcriber Bot...")
    bot.run(DISCORD_TOKEN)
