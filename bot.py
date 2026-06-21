import discord
from discord.ext import commands
import yt_dlp
import os
from dotenv import load_dotenv  # এই লাইনটি আপনার ফাইলে মিসিং আছে

load_dotenv() # এখন এটি কাজ করবে
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True 
bot = commands.Bot(command_prefix='!', intents=intents)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch', 
    'quiet': True,
}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user} অনলাইনে আছে!')

@bot.tree.command(name="play", description="ইউটিউব লিঙ্ক বা নাম থেকে গান বাজান")
async def play(interaction: discord.Interaction, url: str):
    # এটি হলো সেই defer যা কমান্ড প্রসেস করতে সময় দেয়
    await interaction.response.defer()

    if not interaction.user.voice:
        await interaction.followup.send("প্রথমে একটি ভয়েস চ্যানেলে জয়েন করুন!")
        return

    channel = interaction.user.voice.channel
    
    # ভয়েস ক্লায়েন্ট জয়েন লজিক
    try:
        if interaction.guild.voice_client is None:
            voice_client = await channel.connect()
        else:
            voice_client = interaction.guild.voice_client
            await voice_client.move_to(channel)
    except Exception as e:
        await interaction.followup.send(f"ভয়েস চ্যানেলে কানেক্ট হতে সমস্যা হচ্ছে: {str(e)}")
        return

    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info: info = info['entries'][0]
            url2 = info['url']
            
        player = discord.FFmpegPCMAudio(url2, executable="ffmpeg", **ffmpeg_options)
        
        if voice_client.is_playing():
            voice_client.stop()
            
        voice_client.play(player)
        await interaction.followup.send(f'বাজছে: {info.get("title")}')
        
    except Exception as e:
        await interaction.followup.send(f"গান বাজাতে সমস্যা হয়েছে: {str(e)}")

bot.run(TOKEN)