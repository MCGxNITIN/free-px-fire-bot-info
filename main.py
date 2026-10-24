import os
import threading
from flask import Flask
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

# Render ke liye chota web server
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

# Discord Bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="playerinfo", description="Get Free Fire player details")
@app_commands.describe(uid="Player UID", region="Region (IND, BD, SG)")
async def playerinfo(interaction: discord.Interaction, uid: str, region: str = "IND"):
    await interaction.response.defer()
    url = f"https://mani272api.xyz/api/info?uid={uid}&region={region.upper()}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    basic = data.get("basic_info", data)
                    
                    nickname = basic.get("nickname", basic.get("name", "Unknown"))
                    level = basic.get("level", "N/A")
                    likes = basic.get("likes", "N/A")
                    br_rank = basic.get("br_rank", "N/A")
                    cs_rank = basic.get("cs_rank", "N/A")
                    
                    embed = discord.Embed(title=f"Player: {nickname}", color=0x00FFCC)
                    embed.add_field(name="UID", value=uid, inline=True)
                    embed.add_field(name="Region", value=region.upper(), inline=True)
                    embed.add_field(name="Level", value=str(level), inline=True)
                    embed.add_field(name="Likes", value=str(likes), inline=True)
                    embed.add_field(name="BR Rank", value=str(br_rank), inline=True)
                    embed.add_field(name="CS Rank", value=str(cs_rank), inline=True)
                    embed.set_footer(text="DEVELOPED BY PERSISTX")
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Player data nahi mila. UID check karein.")
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("DISCORD_TOKEN nahi mila!")
