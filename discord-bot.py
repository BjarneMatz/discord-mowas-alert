"""
Main file of the Discord bot.
"""
import asyncio
import discord
from database.database import Database as DB
from Logger.logger import Logger
import data_handle as data

import discord.ext.commands as commands

# set up databases and logger
secret_db = DB("secrets")
logger = Logger("Discord Bot")

# get secret bot token from database
TOKEN = secret_db.get_value("bot_token")

# temporary channel id to test the bot
CHANNEL_ID = '1162846390980972605'

# bot permissions
intents = discord.Intents.all()
intents.messages = True

# main bot object
bot = commands.Bot(command_prefix='!', intents=intents)


async def warning_worker():
    """
    Request warnings and post if there are any new ones.
    """
    await bot.wait_until_ready()
    channel = bot.get_channel(int(CHANNEL_ID))

    while not bot.is_closed(): # run until bot is closed
        # fetch new warnings
        warnings = data.call()
        for warning in warnings:
            embed = discord.Embed(
                title=warning["title"],
                description=warning["description"],
                color=discord.Color.red(),
                timestamp=warning["time"]
            )

            # add logo to embed
            embed.set_thumbnail(url=warning["logo"])

            embed.set_footer(text=warning["location"])
            
            embed.set_author(name=warning["author"])
            
            

            # finally post to channel
            await channel.send(embed=embed)
            logger.log("Posted new entry to channel", 3)
            data.set_status(warning["id"], "seen")
        await asyncio.sleep(60) # wait 60 seconds to test again

@bot.event
async def on_ready():
    """
    The function is called when the bot is ready to start working.
    It executes the main function of the bot.
    """
    logger.log(f'Logged in as {bot.user.name}', 3)
    bot.loop.create_task(warning_worker()) # start the rss feed checker
    
bot.run(TOKEN)
