import discord
import asyncio

from utils.config import Config
from utils.punishments.punishment_check import Punishment_Check
from discord.ext import commands

conf = Config()
config = conf.get_config()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="..", intents=intents, app_commands=True)

#tedeezet_bot = commands.Bot(command_prefix="2", intents=intents, app_commands=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}\n-------')
    synced = await bot.tree.sync()
    print(f'Synced  {len(synced)} commands')

async def load_cogs():
    await bot.load_extension(f'cogs._commands_admin')
    await bot.load_extension(f'cogs._commands_xp')
    await bot.load_extension(f'cogs._commands_roleplay')
    await bot.load_extension(f'cogs._commands_settings')

async def start_bot():
    await load_cogs()
    await bot.start(config["TEST_TOKEN"])
    
# async def start_teedezet_bot():
    # await tedeezet_bot.load_extension(f"tedeezet.teedeezet_cog")
    # await tedeezet_bot.start(config["TZ_TOKEN"])

async def main():
    print("We start main")
    a = Punishment_Check(bot=bot)
    bot_task = asyncio.create_task(start_bot())
    punishment_check_task = asyncio.create_task(a.start_infinite_check())
    #tedeezet_bot_task = asyncio.create_task(start_teedezet_bot())
    await asyncio.gather(bot_task, punishment_check_task)


if __name__ == "__main__":
    asyncio.run(main())
