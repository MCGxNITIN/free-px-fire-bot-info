import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

# Bot Client Setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # Slash commands sync karne ke liye
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Free Fire Info Bot is Ready!")

# Slash Command: /playerinfo
@bot.tree.command(name="playerinfo", description="Get Free Fire player profile details")
@app_commands.describe(
    uid="Player ka Free Fire UID", 
    region="Server Region (e.g., IND, BD, SG, BR, PK, ID, RU)"
)
async def playerinfo(interaction: discord.Interaction, uid: str, region: str = "IND"):
    await interaction.response.defer()
    
    region_code = region.upper()
    url = f"https://mani272api.xyz/api/info?uid={uid}&region={region_code}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # API response se data extract karna
                    basic = data.get("basic_info", data)
                    clan = data.get("clan_info", {})
                    pet = data.get("pet_info", {})
                    
                    nickname = basic.get("nickname", basic.get("name", "Unknown"))
                    level = basic.get("level", "N/A")
                    likes = basic.get("likes", "N/A")
                    exp = basic.get("exp", "N/A")
                    br_rank = basic.get("br_rank", "N/A")
                    cs_rank = basic.get("cs_rank", "N/A")
                    bio = basic.get("bio", basic.get("signature", "No Bio"))
                    created_at = basic.get("created_at", basic.get("create_time", "N/A"))
                    last_login = basic.get("last_login", basic.get("last_login_time", "N/A"))
                    
                    guild_name = clan.get("clan_name", clan.get("name", "No Guild"))
                    guild_level = clan.get("clan_level", clan.get("level", "N/A"))
                    
                    pet_name = pet.get("name", "No Pet")
                    pet_level = pet.get("level", "N/A")
                    
                    # Discord Embed Design
                    embed = discord.Embed(
                        title=f"🎮 Profile Details: {nickname}",
                        color=0x00FFCC
                    )
                    
                    embed.add_field(name="🆔 UID", value=f"`{uid}`", inline=True)
                    embed.add_field(name="🌍 Region", value=f"`{region_code}`", inline=True)
                    embed.add_field(name="⭐ Level", value=f"{level} (EXP: {exp})", inline=True)
                    
                    embed.add_field(name="👍 Likes", value=str(likes), inline=True)
                    embed.add_field(name="🏆 BR Rank", value=str(br_rank), inline=True)
                    embed.add_field(name="⚔️ CS Rank", value=str(cs_rank), inline=True)
                    
                    embed.add_field(name="🛡️ Guild", value=f"{guild_name} (Lvl {guild_level})", inline=True)
                    embed.add_field(name="🐾 Pet", value=f"{pet_name} (Lvl {pet_level})", inline=True)
                    embed.add_field(name="📅 Created", value=str(created_at), inline=True)
                    
                    embed.add_field(name="🕒 Last Login", value=str(last_login), inline=False)
                    embed.add_field(name="📝 Bio", value=f"```{bio}```", inline=False)
                    
                    embed.set_footer(text="DEVELOPED BY PERSISTX")
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("⚠️ Player info fetch nahi ho saki. UID ya Region sahi se check karein.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{str(e)}`")

# Step 3 mein copy kiya hua token yahan paste karein
bot.run("YOUR_DISCORD_BOT_TOKEN_HERE")
