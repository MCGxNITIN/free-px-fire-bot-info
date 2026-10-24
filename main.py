import os
import threading
from flask import Flask
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

# --- Render Web Server (Keep Alive) ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running healthy!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

# --- Discord Bot Setup ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print(f"Logged in as {bot.user}")
    except Exception as e:
        print(f"Sync error: {e}")

@bot.tree.command(name="playerinfo", description="Get Free Fire player details")
@app_commands.describe(uid="Player UID", region="Region (IND, BD, SG)")
async def playerinfo(interaction: discord.Interaction, uid: str, region: str = "IND"):
    await interaction.response.defer()
    
    url = f"https://mani272api.xyz/api/info?uid={uid}&region={region.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=12) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                    except Exception:
                        await interaction.followup.send("⚠️ API returned invalid data (Cloudflare block). Try again later.")
                        return

                    basic = data.get("basic_info", data)
                    nickname = basic.get("nickname", basic.get("name", "Unknown"))
                    level = basic.get("level", "N/A")
                    likes = basic.get("likes", "N/A")
                    br_rank = basic.get("br_rank", "N/A")
                    cs_rank = basic.get("cs_rank", "N/A")

                    embed = discord.Embed(title=f"🎮 Player: {nickname}", color=0x00FFCC)
                    embed.add_field(name="UID", value=uid, inline=True)
                    embed.add_field(name="Region", value=region.upper(), inline=True)
                    embed.add_field(name="Level", value=str(level), inline=True)
                    embed.add_field(name="Likes", value=str(likes), inline=True)
                    embed.add_field(name="BR Rank", value=str(br_rank), inline=True)
                    embed.add_field(name="CS Rank", value=str(cs_rank), inline=True)
                    embed.set_footer(text="DEVELOPED BY PERSISTX")

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"⚠️ API Error (Status {response.status}). UID check karein.")
    except Exception as err:
        await interaction.followup.send(f"⚠️ Error: `{str(err)}`")

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("CRITICAL: DISCORD_TOKEN is missing in Environment Variables!")
