import discord
from discord.ext import commands
from transcription.whisper_api import transcribe_audio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("Joined the voice channel!")
    else:
        await ctx.send("You need to be in a voice channel first.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command()
async def transcribe(ctx):
    file_path = "recordings/sample.wav"
    await ctx.send("Transcribing...")
    try:
        result = transcribe_audio(file_path)
        await ctx.send(f"📝 Transcription:\n```{result}```")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

bot.run('DISCORD TOKEN')
