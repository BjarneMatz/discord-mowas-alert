import discord
import rss
import asyncio
from database.database import Database as DB
from Logger.logger import Logger

db = DB("secrets")
logger = Logger("Discord Bot")

# get secret bot token from database
TOKEN = db.get_value("bot_token")

# temporary channel id to test the bot
CHANNEL_ID = '1162480178124042250'

# bot permissions
intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)


async def check_rss_feed():
    await client.wait_until_ready()
    channel = client.get_channel(int(CHANNEL_ID))
    
    while not client.is_closed(): # run until bot is closed
        # fetch feed from rss module
        entry, author = rss.external_request("https://warnung.bund.de/api31/mowas/rss/033520000000.rss")
        
        if entry != {}: # if there is a new entry
            embed = discord.Embed(
                title=entry["title"], 
                description=entry["description"],
                color=discord.Color.red(),
                timestamp=entry["date_object"],
                url=entry["link"],
            )

            embed.set_author(
                name=author["name"],
                url=author["url"]
            )
            embed.set_thumbnail(url=author["logo"])

            # finally post to channel
            await channel.send(embed=embed)
            logger.log("Posted new entry to channel", 3)
        await asyncio.sleep(60) # wait 60 seconds to test again


@client.event
async def on_ready():
    logger.log(f'Logged in as {client.user.name}', 3)
    client.loop.create_task(check_rss_feed()) # start the rss feed checker
client.run(TOKEN)
