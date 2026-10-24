import os
import threading
from flask import Flask
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

# --- Flask Server (Render Port Binding) ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
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
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.tree.command(name="bancheck", description="Check Free Fire account ban status")
@app_commands.describe(uid="Player Free Fire UID")
async def bancheck(interaction: discord.Interaction, uid: str):
    await interaction.response.defer()
    url = f"http://ban.mani272api.xyz/check?uid={uid}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    is_banned = data.get("is_banned", False)
                    status_text = "Banned ❌" if is_banned else "Active / Clean ✅"
                    duration = data.get("duration", "N/A")
                    
                    embed = discord.Embed(
                        title="Free Fire Ban Status",
                        color=discord.Color.red() if is_banned else discord.Color.green()
                    )
                    embed.add_field(name="UID", value=uid, inline=True)
                    embed.add_field(name="Status", value=status_text, inline=True)
                    if is_banned:
                        embed.add_field(name="Duration", value=str(duration), inline=False)
                    embed.set_footer(text="DEVELOPED BY PERSISTX")
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("API response error.")
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

@bot.tree.command(name="playerinfo", description="Get Free Fire player profile details")
@app_commands.describe(uid="Player Free Fire UID", region="Server Region (e.g. IND, BD, SG)")
async def playerinfo(interaction: discord.Interaction, uid: str, region: str = "IND"):
    await interaction.response.defer()
    region_code = region.upper()
    url = f"https://mani272api.xyz/api/info?uid={uid}&region={region_code}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    basic = data.get("basic_info", data)
                    nickname = basic.get("nickname", basic.get("name", "Unknown"))
                    level = basic.get("level", "N/A")
                    likes = basic.get("likes", "N/A")
                    exp = basic.get("exp", "N/A")
                    br_rank = basic.get("br_rank", "N/A")
                    cs_rank = basic.get("cs_rank", "N/A")
                    bio = basic.get("bio", basic.get("signature", "No Bio"))
                    
                    embed = discord.Embed(
                        title=f"Player Profile: {nickname}",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="UID", value=uid, inline=True)
                    embed.add_field(name="Region", value=region_code, inline=True)
                    embed.add_field(name="Level", value=str(level), inline=True)
                    embed.add_field(name="Likes", value=str(likes), inline=True)
                    embed.add_field(name="EXP", value=str(exp), inline=True)
                    embed.add_field(name="BR Rank", value=str(br_rank), inline=True)
                    embed.add_field(name="CS Rank", value=str(cs_rank), inline=True)
                    embed.add_field(name="Bio", value=str(bio), inline=False)
                    embed.set_footer(text="DEVELOPED BY PERSISTX")
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Profile fetch failed. Check UID/Region.")
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_TOKEN environment variable not set.")
