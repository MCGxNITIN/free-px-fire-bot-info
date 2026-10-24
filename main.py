import os
import threading
from flask import Flask
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

# --- Specific Server & Channel Restrictions ---
ALLOWED_GUILD_ID = 1525181999147388958
ALLOWED_CHANNEL_ID = 1548235918895484958

# --- Render Keep-Alive Server ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot service is alive and healthy!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

# --- Discord Bot Client ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in successfully as: {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) successfully.")
    except Exception as e:
        print(f"Command sync error: {e}")

@bot.tree.command(name="playerinfo", description="Get Free Fire player details")
@app_commands.describe(uid="Player UID", region="Server Region (IND, BD, SG, etc.)")
async def playerinfo(interaction: discord.Interaction, uid: str, region: str = "IND"):
    # 1. Server ID Check
    if interaction.guild_id != ALLOWED_GUILD_ID:
        await interaction.response.send_message(
            "❌ Yeh bot is server ke liye authorized nahi hai!",
            ephemeral=True
        )
        return

    # 2. Channel ID Check
    if interaction.channel_id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(
            f"❌ Yeh command sirf <#{ALLOWED_CHANNEL_ID}> channel me use ki ja sakti hai!",
            ephemeral=True
        )
        return

    await interaction.response.defer()
    
    url = f"https://mani272api.xyz/api/info?uid={uid}&region={region.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as resp:
                text_data = await resp.text()
                
                if "<html" in text_data.lower() or "cloudflare" in text_data.lower():
                    await interaction.followup.send("⚠️ API Server ne request block kar di (Cloudflare Protection). Please thodi der baad try karein.")
                    return

                if resp.status == 200:
                    import json
                    try:
                        data = json.loads(text_data)
                    except Exception:
                        await interaction.followup.send("⚠️ API response ko read karne me issue aaya.")
                        return

                    basic = data.get("basic_info", data)
                    nickname = basic.get("nickname", basic.get("name", "Unknown"))
                    level = basic.get("level", "N/A")
                    likes = basic.get("likes", "N/A")
                    br_rank = basic.get("br_rank", "N/A")
                    cs_rank = basic.get("cs_rank", "N/A")

                    embed = discord.Embed(title=f"🎮 Player Info: {nickname}", color=0x00FFCC)
                    embed.add_field(name="UID", value=str(uid), inline=True)
                    embed.add_field(name="Region", value=region.upper(), inline=True)
                    embed.add_field(name="Level", value=str(level), inline=True)
                    embed.add_field(name="Likes", value=str(likes), inline=True)
                    embed.add_field(name="BR Rank", value=str(br_rank), inline=True)
                    embed.add_field(name="CS Rank", value=str(cs_rank), inline=True)
                    embed.set_footer(text="DEVELOPED BY PERSISTX")
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f"⚠️ API returned status code: {resp.status}")
    except Exception as err:
        await interaction.followup.send(f"⚠️ Request Failed: `{str(err)}`")

# --- Execution Entry Point ---
if __name__ == "__main__":
    keep_alive()
    bot_token = os.environ.get("DISCORD_TOKEN")
    
    if not bot_token:
        print("ERROR: DISCORD_TOKEN environment variable missing!")
    else:
        try:
            bot.run(bot_token)
        except Exception as e:
            print(f"Bot failed to run: {e}")
