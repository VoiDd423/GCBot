import discord
import motor.motor_asyncio
import math
import os
import json
from datetime import  timedelta
from utils.webhook_messages import WebhookMessages
from utils.config import Config
from utils.exp.leaders_view import Leaders_View
from utils.exp.blank import Blank
from discord.ext import commands, tasks
from discord import app_commands

config = Config()
conf = config.get_config()

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(conf["MONGO_URI"])
db = mongo_client["gameclub-bot"]
exp_table = db["exp"]

class Commands_XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_members = {}
        self.no_voice_exp = conf["NO_TOP"].split(",")
        self.no_voice_exp = conf["NO_EXP_VOICE"].split(",")

    @app_commands.command(name="delete_from_top", description="Удалить человека из статистики")
    @commands.has_any_role("Supreme", "Tester")
    async def delete_from_statistic(self, interaction : discord.Interaction, member : discord.Member):
        self.not_in_top.append(member.id)
        conf["NO_TOP"] = ",".join(self.not_in_top)
        config.write_config(conf)
        await exp_table.delete_many({'ID': member.id})
        await interaction.response.send_message(f"{member.mention} was deleted from statistic")

    @app_commands.command(name = "set_no_exp_voice", description="Установить войс в котором не будет прибовыляться опыт")
    @commands.has_any_role("Supreme", "Tester")
    async def set_no_exp_voice(self, interaction : discord.Interaction, channel_id : str):
        self.no_voice_exp.append(channel_id)
        conf["NO_EXP_VOICE"].append(channel_id)
        with open("config.json", "w") as f:
            json.dump(conf, f)

    @commands.command(name="leaders")
    async def leaders(self, ctx):
        try: 
            top = await self.get_top()
            max_pages = math.ceil(len(top)/10)
            leaders_view = Leaders_View(1, max_pages, top, ctx.author.id)
            await ctx.send(embed=WebhookMessages.message_leaders(1,max_pages,top), view=leaders_view)
        except Exception as a:
            print(a)

    @commands.command(name="rank")
    async def rank(self, ctx ,member: discord.Member = None):
        try:
            if member == None:
                user_id = ctx.author.id
                username = ctx.author.name
            else:
                user_id = member.id
                username = member.name

            record = await exp_table.find_one({"ID": user_id})
            exp = record.get("EXP")
            lvl = record.get("LVL")
            
            exp_next_lvl = self.xp_for_next_lvl(lvl,exp)[1]
            voice_time = record.get("VOICE_TIME")
            user_top = await self.get_user_rank(username)
        
            user = ctx.author if member == None else member
            Blank.get_avatar(user)
            Blank.make_blank(username, exp, exp_next_lvl,lvl,voice_time, user_top)
    
            file = discord.File(f"pictures/{username}_blank.png")
            await ctx.send(file=file)

            del file
            os.remove(f'pictures/{username}_blank.png')
            os.remove(f"pictures/{username}_avatar.png")
        except Exception as a:
            print(a)

    @commands.Cog.listener()
    async def on_ready(self):
        self._update_experience.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != None: 
            channel_id = before.channel.id
            member_id = member.id

            if (channel_id in self.voice_members) and (member_id in self.voice_members[channel_id]):
                microphone_time = self.voice_members[channel_id][member_id]
                await self.add_exp(member, microphone_time)
                self.voice_members[channel_id][member_id] = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) in conf["EXP_CHANNELS_ID"].split(","):
            exp = 4 if message.channel.id not in [1127270650113970337, 1127269693519036568] else 4
            try:
                await self.add_exp(message.author, add_exp=exp)
            except Exception as a:
                print(a)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        record = await exp_table.find_one({"NAME": member.name})
        if record != None:
            lvl = record.get("LVL")
            if lvl != 0:
                await self.add_lvl_role(member, record.get("LVL"))
        else:
            exp_table.insert_one({
                    "NAME": member.name,
                    "ID": member.id,
                    "EXP": 0,
                    "LVL": 0,
                    "VOICE_TIME": '0:0:0'
                })

    @tasks.loop(seconds=1)
    async def _update_experience(self):
        for guild in self.bot.guilds:
            for voice_channel in guild.voice_channels:
                if str(voice_channel.id) not in self.no_voice_exp:
                    if voice_channel.id not in self.voice_members:
                        self.voice_members[voice_channel.id] = {}
                    for member in voice_channel.members:
                        if len(voice_channel.members) >= 2:
                            if member.id not in self.voice_members[voice_channel.id]:
                                self.voice_members[voice_channel.id][member.id] = 0
                            if not (member.voice.self_mute or member.voice.self_deaf):
                                self.voice_members[voice_channel.id][member.id] += 1

    async def add_exp(self, member, microphone_time = 0, add_exp = 0):
        if not member.name in self.no_voice_exp:
            member_document = await exp_table.find_one({"ID": member.id}, {"_id": 0, "EXP": 1, "LVL": 1, "VOICE_TIME" : 1})
            if member_document != None:
                member_exp = int(member_document["EXP"]) + round((5*(microphone_time/60))) + add_exp
                member_lvl = int(member_document["LVL"])
                member_voice = member_document["VOICE_TIME"]
                is_new_lvl = await self.check_lvl(member_lvl,member_exp, member)
                if is_new_lvl[0]: 
                    member_lvl = is_new_lvl[1]
                    if is_new_lvl[2]:
                        try:
                            await self.add_lvl_role(member, member_lvl)
                        except: pass
                        await self.new_level_send(member, member_lvl)
                if microphone_time != 0:
                    new_voice = self.compare_timedelta(member_voice, microphone_time)
                    new_voice = self.datetime_to_str(new_voice)
                else:
                    new_voice = member_voice
                await exp_table.update_one({"ID": member.id}, {"$set": {"EXP": member_exp, "LVL": member_lvl, "VOICE_TIME": new_voice}})
            else:
                member_exp = round(5*(microphone_time/60)) + add_exp
                member_lvl = 0
                is_new_lvl = await self.check_lvl(member_lvl,member_exp, member)
                if is_new_lvl[0]: 
                    member_lvl = is_new_lvl[1] 
                    try:
                        await self.add_lvl_role(member, is_new_lvl[1])
                    except: pass
                    await self.new_level_send(member.id)
                if microphone_time != 0:
                    time = self.datetime_to_str(timedelta(seconds=microphone_time))
                else:
                    time = "0:00:00"
                exp_table.insert_one({
                    "NAME": member.name,
                    "ID": member.id,
                    "EXP": member_exp,
                    "LVL": member_lvl,
                    "VOICE_TIME": time
                })


    async def get_top(self):
        pipeline = [
            {"$sort": {"EXP": -1}},  # Сортируем документы по убыванию EXP
            {
                "$project": {
                    "_id": 0, 
                    "NAME": 1, 
                    "EXP": 1,   
                    "LVL": 1,   
                    "VOICE_TIME": 1  
                }
            }
        ]
        cursor = exp_table.aggregate(pipeline)
        top_users = []
        async for document in cursor:
            top_users.append(document)
        top_users_dict = {i + 1: {"NAME": user["NAME"], "EXP": user["EXP"], "LVL": user["LVL"], "VOICE_TIME": user["VOICE_TIME"]} for i, user in enumerate(top_users)}
        return top_users_dict
        
    async def get_user_rank(self, username):
        top_users = await self.get_top()  # Вызываем вашу функцию get_top
        for rank, user_data in top_users.items():
            if user_data["NAME"] == username:
                return rank
        return None

    async def add_lvl_role(self, member, lvl):
        for role in member.roles:
            if "Level" in role.name:
                await member.remove_roles(role)
                
        role = discord.utils.get(member.guild.roles, name=f"Level {lvl}")
        if role is not None:
            if role not in member.roles:
                await member.add_roles(role)
            else:
                raise Exception("Member already has this role")
        else:
            role = await member.guild.create_role(name=f"Level {lvl}")
            await member.add_roles(role)
        
    async def new_level_send(self, member, member_lvl):
        channel_id = int(conf["COMMANDS_CHANNEL"])
        user_data = await exp_table.find_one({"ID": member.id}, {"_id": 0, "EXP": 1, "LVL": 1, "VOICE_TIME" : 1})
        if user_data != None:
            exp = user_data["EXP"]
            voice_time = user_data["VOICE_TIME"] 
            next_lvl_xp = self.xp_for_next_lvl(member_lvl, exp)[0]
            top = await self.get_top()
            top_place = "#" + str(next((key for key, value in top.items() if value.get("NAME") == member.name)))
            embed = WebhookMessages.message_new_lvl(member, member_lvl, top_place, next_lvl_xp, voice_time)
            channel = self.bot.get_channel(channel_id)
            await channel.send(embed = embed)

    async def check_lvl(self, lvl, exp, member):
        new_lvl = 0 
        lvl_exp = 1440
        while exp >= lvl_exp:
            if new_lvl < 10:
                lvl_exp += 1440
            else:
                lvl_exp += 3600
            new_lvl += 1
        if lvl == new_lvl:
            return [False, new_lvl, False]
        if lvl < 100 and new_lvl >= 100:
            role_add = discord.utils.get(member.guild.roles, id = 1189360936818061352)
            role_delete = discord.utils.get(member.guild.roles, name = f"Level {lvl}")
            await member.add_roles(role_add)
            await member.remove_roles(role_delete)
            return [True, new_lvl, False]
        return [True, new_lvl, True]
        
    def compare_timedelta(self, time, microphone_time):
        time_components = list(map(int, time.split(':')))
        time_delta = timedelta(hours=time_components[0], minutes=time_components[1], seconds=time_components[2])
        resulting_time = time_delta + timedelta(seconds=microphone_time)
        return resulting_time

    def xp_for_next_lvl(self,now_lvl,exp):
        lvl = 1
        a = 1440
        for i in range(now_lvl+1):
            if lvl < 10:
                a += 1440
            else:
                a += 3600
            lvl += 1
        return [round(a)-exp, round(a)]

    def datetime_to_str(self, delta):
        days, seconds = delta.days, delta.seconds
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        total_hours = days * 24 + hours
        return f"{total_hours:02}:{minutes:02}:{seconds:02}"

async def setup(bot):
    await bot.add_cog(Commands_XP(bot)) 