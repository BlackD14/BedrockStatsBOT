from query import query
from stats import stats
from datetime import datetime
import os, re
try:
    from discord.ext import commands
    from dotenv import load_dotenv
    import discord
except ModuleNotFoundError:
    print('[!] Some modules are missing. Installing...')
    os.system('pip install discord.py')
    os.system('pip install python-dotenv')
    from discord.ext import commands
    from dotenv import load_dotenv
    import discord

load_dotenv()
TOKEN = os.environ['TOKEN']
client = commands.Bot(command_prefix=os.environ['PREFIX'])

def get_status():
    IP = os.environ['IP']; PORT = int(os.environ['PORT']); MAX_SHOW = int(os.environ['MAX_SHOW'])

    with query(IP, port=PORT, timeout=10) as data:
        if len(data.player_name) > MAX_SHOW:
            players = f'```{", ".join(data.player_name[0:MAX_SHOW])}``` + {str(len(data.player_name[MAX_SHOW:len(data.player_name)]))} other(s)'
        elif 0 < len(data.player_name) < MAX_SHOW:
            players = f'```{", ".join(data.player_name)}```'
        else:
            players = '-'
        wl = f"```{data.whitelist}```"

    with stats(IP, port=PORT, timeout=10) as data:
        motd = re.sub(r'§.', '', f"```{data.motd}```")
        version = f"```{data.game_version}```"
        online = f"```{data.num_players}/{data.max_players}```"
    
    return motd, version, online, players, wl
    
    

@client.command()
async def status(ctx):
    thumbnail = str(os.environ['THUMBNAIL'])
    description = str(os.environ['DESCRIPTION'])
    time = datetime.now()
    try:
        motd, version, online, players, wl = get_status()
        data = {"Status": "```Online```", "Player Count": online, "Whitelist": wl, "Version": version, "Motd": motd, "Players": players}
        embed = discord.Embed(title="Server Status", timestamp=time, color=0x00ff00)

        if thumbnail != '':
            embed.set_thumbnail(url=thumbnail)
        else: pass

        if description != '':
            embed.description = description
        else: pass

        for key, value in data.items():
            if key == "Players":
                embed.add_field(name=key, value=value, inline=False)
            else:
                embed.add_field(name=key, value=value, inline=True)

        embed.set_footer(text=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
    except:
        data = {"Status": "```Offline```", "Player Count": "```0/0```", "Whitelist": "```-```", "Version": "```-```", "Motd": "```-```", "Players": "```-```"}
        embed = discord.Embed(title="Server Status", timestamp=time, color=0xff0000)

        if thumbnail != '':
            embed.set_thumbnail(url=thumbnail)
        else: pass
        
        if description != '':
            embed.description = description
        else: pass

        for key, value in data.items():
            if key == "Players":
                embed.add_field(name=key, value=value, inline=False)
            else:
                embed.add_field(name=key, value=value, inline=True)
        
        embed.set_footer(text=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

client.run(TOKEN, bot=True)