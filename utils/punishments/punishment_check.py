import discord
import asyncio
from utils.config import Config
from datetime import datetime
from utils.webhook_messages import WebhookMessages
from pymongo.mongo_client import MongoClient


config = Config()
conf = config.get_config()


client = MongoClient(conf["MONGO_URI"])
db = client["gameclub-bot"]
collection = db["punishments"]

class Punishment_Check():
    def __init__(self, bot=None):
        self.now_punishments = {}
        self.bot = bot

    async def start_infinite_check(self):
        await self.infinite_check()

    async def infinite_check(self):
        while True:
            self.get_pun_dict()
            await self.check_puns()
            await asyncio.sleep(5) 

    def get_pun_dict(self):
        self.now_punishments = {}
        punishments_data = collection.find()

        try:
            for document in punishments_data:
                id = document.get("ID")
                punishment_end = document.get("PUNISHMENT_END")
                self.now_punishments[id] = punishment_end
        except Exception as a:
            print(a)

    async def check_puns(self):
        members_to_delete = []
        for member in self.now_punishments:
            current_time = datetime.now()
            if current_time <= self.now_punishments[member]:
                data = collection.find_one({"ID": member})

                punishment_actions = {
                    "mute": self.unmute_nocomand,
                    "ban": self.unban_nocomand,
                    "warn": self.unwarn_nocomand,
                }

                punishment_type = data["PUNISHMENT_TYPE"]
                if punishment_type in punishment_actions:
                    await punishment_actions[punishment_type](data["ID"])
                    
                members_to_delete.append(member)
        for member in members_to_delete:
            collection.delete_one({"ID": member})

    async def unban_nocomand(self, member_id):
        guild = self.bot.get_guild(int(conf["SERVER_ID"]))

        if guild is None:
            print("Guild not found")
            return

        banned_user = None
        async for ban in guild.bans():
            if ban.user.id == member_id:
                banned_user = ban.user

        if banned_user is not None:
            await guild.unban(banned_user)
            history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
            webhook = await history_channel.create_webhook(name="GameClub")
            await webhook.send(embed=WebhookMessages.message_unmute_bot(banned_user, "бан"))
            await webhook.delete()
        else:
            print(f"ERROR: No user with ID {member_id} is banned")

    async def unmute_nocomand(self, member_id):
        guild = self.bot.get_guild(int(conf["SERVER_ID"]))
        if guild is None:
            print("Guild not found")
            return

        muted_role = discord.utils.get(guild.roles, name="Muted")
        if muted_role is None:
            print("Muted role not found")
            return

        member = guild.get_member(int(member_id))
        if member is None:
            print("Member not found")
            return

        await member.remove_roles(muted_role)
        try:
            voice_channel = member.voice.channel
            await member.move_to(voice_channel)
        except Exception:
            pass
        history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
        webhook = await history_channel.create_webhook(name="GameClub")
        await webhook.send(embed=WebhookMessages.message_unmute_bot(member, "мут"))
        await webhook.delete()

    async def unwarn_nocomand(self, member_id):
        guild = self.bot.get_guild(int(conf["SERVER_ID"]))
        if guild is None:
            print("Guild not found")
            return

        muted_role = discord.utils.get(guild.roles, name="Warned")
        if muted_role is None:
            print("Muted role not found")
            return

        member = guild.get_member(int(member_id))
        if member is None:
            print("Member not found")
            return

        await member.remove_roles(muted_role)

        history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
        webhook = await history_channel.create_webhook(name="GameClub")
        await webhook.send(embed=WebhookMessages.message_unmute_bot(member, "варн"))
        await webhook.delete()

