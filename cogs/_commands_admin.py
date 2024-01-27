import discord
import json
import re
from datetime import datetime
from pymongo import MongoClient
from discord.ext import commands
from discord import app_commands
from dateutil.relativedelta import relativedelta
from utils.config import Config
from utils.webhook_messages import WebhookMessages


config = Config()
conf = config.get_config()

client = MongoClient(conf["MONGO_URI"])
db = client["gameclub-bot"]
collection = db["punishments"]


class Commands_Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banns_ammount = {}
        self.banns_times = {}
    
    @app_commands.command(name="take_role", description="Забрать роль у человека")
    @commands.has_permissions(manage_roles=True)
    @commands.has_any_role("Trainee", "Helper", "Moder", "Curator", "Tester", "Support", "Supreme")
    async def take_role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role , reason: str):
        if self.check_power(interaction.user, member):
            guild = interaction.guild
            muted_role = discord.utils.get(guild.roles, name=role.name)
            await interaction.response.send_message(content=f"Вы сняли роль {role.mention} с {member.mention}")

            await member.remove_roles(muted_role, reason=reason)
            history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
            webhook = await history_channel.create_webhook(name="GameClub")
            await webhook.send(embed=WebhookMessages.message_punishment_bot(type = "Снятие роли",member= member,moderator= interaction.user,reason=reason, role=role))
            await webhook.delete()

            await member.send(embed=WebhookMessages.message_punishment("Снятие роли!",interaction.user,reason))
        else:
            await interaction.response.send_message(content="У вас нет прав для использования этой команды!")

    @app_commands.command(name="kick", description="Кикнуть человека")
    @app_commands.checks.cooldown(1,4)
    @commands.has_permissions(kick_members=True)
    @commands.has_any_role("Trainee", "Helper", "Moder", "Curator", "Tester", "Support", "Supreme")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if self.check_power(interaction.user, user):
            await user.send(embed=WebhookMessages.message_punishment("Вы были кикнуты!",interaction.user,reason))
            await interaction.response.send_message(f"Вы кикнули {user.mention}")
            await user.kick()
            history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
            webhook = await history_channel.create_webhook(name="GameClub")
            await webhook.send(embed=WebhookMessages.message_punishment_bot("Кик", user, interaction.user, reason))
            await webhook.delete()
        else:
            await interaction.response.send_message(content="У вас нет прав для использования этой команды!")

    @app_commands.command(name="ban", description="Забанить человека")
    @app_commands.checks.cooldown(1,4)
    @commands.has_guild_permissions(ban_members=True)
    @commands.has_any_role("Trainee", "Helper", "Moder", "Curator", "Tester", "Support", "Supreme")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str):
        moderator = interaction.user
        if self.check_power(moderator, member):
            start_time = datetime.now()
            await interaction.response.send_message(f"Вы забанили {member.mention}")
            history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
            webhook = await history_channel.create_webhook(name="GameClub")
            if duration != 'inf':
                end_time = self.add_times(start_time, duration)
                self.add_punished(member.name, member.id, start_time,end_time,duration, "ban")
                await webhook.send(embed=WebhookMessages.message_punishment_bot("Бан", member, moderator, reason, time=duration))
            else:
                end_time = "Never"
                await webhook.send(embed=WebhookMessages.message_punishment_bot("Бан", member, moderator, reason, time=end_time))
            await webhook.delete()
            try:
                await member.send(embed=WebhookMessages.message_punishment("Вы были забанены!", moderator,reason,end_time.strftime("%Y.%m.%d %H:%M")))
            except: pass
            await member.ban(reason=reason)
            await self.anti_crush(interaction, member, start_time)
        else:
            await interaction.response.send_message(content="У вас нет прав для использования этой команды!")

    @app_commands.command(name="mute", description="Замутить человека")
    @app_commands.checks.cooldown(1,4)
    @commands.has_permissions(manage_roles=True)
    @commands.has_any_role("Trainee", "Helper", "Moder", "Curator", "Tester", "Support", "Supreme")
    async def mute(self, interaction: discord.Interaction, member: discord.Member,duration : str, reason: str ):
        if self.check_power(interaction.user, member):
            guild = interaction.guild
            warned_role = discord.utils.get(guild.roles, name="Warned")
            muted_role = discord.utils.get(guild.roles, name="Muted")
            if warned_role in member.roles:
                member.remove_roles(warned_role)
            if muted_role not in member.roles:
                await member.add_roles(muted_role)
                await interaction.response.send_message(content=f"Вы замьютили {member.mention}")

                history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
                webhook = await history_channel.create_webhook(name="GameClub")
                start_time = datetime.now()
                end_time = self.add_times(duration, start_time)
                await member.timeout(self.add_times(duration, datetime.now().astimezone()))
                try:
                    self.add_punished(member= member, id= member.id, start_time= start_time, end_time=end_time, pun_type = "mute")
                except Exception as a:
                    if str(a) == "Member already has a punishment":
                        await interaction.response.send_message(str(a))
                        return
                await webhook.send(embed=WebhookMessages.message_punishment_bot(type = "Мут",member= member,moderator= interaction.user,reason=reason, time=duration))
                await webhook.delete()
                voice_channel = member.voice.channel
                await member.move_to(voice_channel)
                await member.send(embed=WebhookMessages.message_punishment("Вы были замьючены!",interaction.user,reason,end_time.strftime("%Y.%m.%d %H:%M")))
            else:
                interaction.response.send_message(content="У пользователя уже есть мут!")
        else:
            await interaction.response.send_message(content="У вас нет прав для использования этой команды!")

    @app_commands.command(name="warn", description="Предупредить человека")
    @app_commands.checks.cooldown(1,4)
    @commands.has_permissions(manage_roles=True)
    @commands.has_any_role("Trainee", "Helper", "Moder", "Curator", "Tester", "Support", "Supreme")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str):
        if self.check_power(interaction.user, member):
            guild = interaction.guild
            warned_role = discord.utils.get(guild.roles, name="Warned")
            muted_role = discord.utils.get(guild.roles, name="Muted")
            if muted_role not in member.roles:
                if warned_role not in member.roles:
                    start_time = datetime.now()
                    end_time = self.add_times(start_time, duration)    
                    self.add_punished(member= member.name, id= member.id, start_time= start_time, end_time=end_time, duration= duration, pun_type = "warn")
                    await member.add_roles(warned_role, reason=reason)

                    await interaction.response.send_message(content= f"Вы выдали предупреждение учатснику под ником {member.mention}")
                    history_channel = self.bot.get_channel(1114645158017900571)
                    webhook = await history_channel.create_webhook(name="GameClub")
                    await webhook.send(embed=WebhookMessages.message_punishment_bot("Варн", member, interaction.user, reason, time=duration))
                    await webhook.delete()
                    await member.send(embed=WebhookMessages.message_punishment("Вам выдали предупреждение!",interaction.user,reason, end_time=end_time))
                else:
                    interaction.response.send_message(content="У пользователя уже есть предупреждение!")
            else:
                interaction.response.send_message(content="Пользователь замьючен!")
        else:
            await interaction.response.send_message(content="У вас нет прав для использования этой команды!")

    @app_commands.command(name="unmute", description="Размутить человека")
    @commands.has_permissions(manage_roles=True)
    @commands.has_any_role("Trainee", "Helper", "Moder", "Curator", "Tester", "Support", "Supreme")
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await member.timeout(None)
            await interaction.response.send_message(f"Вы размьютили {member.mention}")

            self.delete_from_databases(member.name)
            history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
            webhook = await history_channel.create_webhook(name="GameClub")
            await webhook.send(embed=WebhookMessages.message_unban(member, interaction.user, 'Размут'))
            await webhook.delete()

            try:
                voice_channel = member.voice.channel
                await member.move_to(voice_channel)
            except:pass
            await member.send(embed=WebhookMessages.message_unmute("Вы были размьючены!", interaction.user))
        else:
            await interaction.response.send_message(f"У этого человека нету мута!", ephemeral=True)


    @app_commands.command(name='unban', description="Разбанить человека") 
    @commands.has_permissions(ban_members=True)
    @commands.has_any_role("Trainee", "Helper", "Moder", "Curator", "Tester", "Support", "Supreme")
    async def unban(self, interaction: discord.Interaction, member_id: str):
        banned_users = interaction.guild.bans()
        member = None
        async for ban_entry in banned_users:
            if str(ban_entry.user.id) == member_id:
                member = ban_entry.user
                break

        if member is not None:
            await interaction.guild.unban(member)
            await interaction.response.send_message(f"Вы разбанили {member.mention}")
            history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
            webhook = await history_channel.create_webhook(name="GameClub")
            await webhook.send(embed=WebhookMessages.message_unban(member, interaction.user, 'Разбан'))
            self.delete_from_databases(member.name)
        else:
            await interaction.response.send_message("Участник с указанным ID не найден в списке забаненных.", ephemeral=True)
        await webhook.delete()

    @app_commands.command(name='unwarn', description="Снять предупреждение")
    @commands.has_permissions(manage_roles=True)
    @commands.has_any_role("Trainee", "Helper", "Moder", "Curator", "Tester", "Support", "Supreme")
    async def unwarn(self, interaction : discord.Interaction, member: discord.Member):
        warned_role = discord.utils.get(interaction.guild.roles, name="Warned")
        if warned_role in member.roles:
            await member.remove_roles(warned_role)

            self.delete_from_databases(member.name)

            await interaction.response.send_message(f"Вы сняли предупреждение с {member.mention}")
            history_channel = self.bot.get_channel(conf["HISTORY_CHANNEL"])
            webhook = await history_channel.create_webhook(name="GameClub")
            await webhook.send(embed=WebhookMessages.message_unban(member, interaction.user, 'Предупреждение снято'))
            await webhook.delete()

            await member.send(embed=WebhookMessages.message_unmute("Предупреждение снято",interaction.user))
        else:
            await interaction.response.send_message(f"У этого человека нету предупреждения!", ephemeral=True)

    def delete_from_databases(self, name):
        collection.delete_many({"NAME": name})

    def check_power(self, moderator, user):
        moderator_roles = moderator.roles[1:]
        user_roles = user.roles[1:]

        if user_roles and moderator_roles:
            max_role_moderator = max(
                moderator_roles, key=lambda role: role.position)
            max_role_user = max(user_roles, key=lambda role: role.position)

            if max_role_moderator.position > max_role_user.position:
                return True
            elif max_role_moderator.position < max_role_user.position:
                return False
        else:
            if len(moderator.roles) <= 1:
                return False
            return True

    def get_config(self):
        with open("config.json", "r") as f:
            return json.load(f)

    def get_allowed_roles(self):
        # Check for moderation role
        with open('moderator_roles_id.json', 'r') as f:
            moderation_roles = json.load(f)
        return moderation_roles

    def add_punished(self, member, id, start_time, end_time ,pun_type):
        query = {
            "NAME": id,
            "PUNISHMENT_TYPE": pun_type
        }
        col = collection.find_one({"ID": id})
        if col != None:
            if collection.find_one(query) != None:
                raise Exception("Member already has a punishment")
            else:
                if col["PUNISHMENT_TYPE"] == "ban":
                    raise Exception("Member is banned")
                else:
                    collection.delete_one({"ID": id})

        data = {
            "NAME": member.name,
            "ID": id,
            "PUNISHMENT_TIME": start_time,
            "PUNISHMENT_END": end_time,
            "PUNISHMENT_TYPE": pun_type,
            "GUILD_ID": conf["SERVER_ID"]
        }
        collection.insert_one(data)

    def add_times(self, duration_str, start_time):
        years, months, days, hours, minutes, seconds = 0, 0, 0, 0, 0, 0
        matches = re.findall(r'(\d+)([ymdhrs])', duration_str)
        
        for value, unit in matches:
            value = int(value)
            if unit == 'y':
                years = value
            elif unit == 'mth':
                months = value
            elif unit == 'd':
                days = value
            elif unit == 'h':
                hours = value
            elif unit == 'm':
                minutes = value
            elif unit == 's':
                seconds = value

        delta = relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds)
        result_time = start_time + delta
        return result_time
    
    async def anti_crush(self, interaction, member, start_time):
        moderator = interaction.user

        if moderator in self.banns_ammount:
            self.banns_ammount[moderator] += 1
            self.banns_times[moderator] += f",{start_time}"

            banns_times = self.banns_times[moderator].split(",")
            while banns_times and datetime.datetime.strptime(banns_times[0], "%Y-%m-%d %H:%M:%S") < start_time - datetime.timedelta(minutes=30):
                banns_times.pop(0)
                self.banns_ammount[moderator] -= 1

            if self.banns_ammount[moderator] >= 15:
                roles_id = []
                with open("utils/punishments/moderator_roles_id.json", "r") as f:
                    roles_id = json.load(f)
                
                roles_to_remove = [member.guild.get_role(role_id) for role_id in roles_id]
                roles_to_remove = [role for role in roles_to_remove if role in member.roles]

                await member.remove_roles(*roles_to_remove)
                await interaction.response.send_message(f"Вы забанили за последние полчаса 15 или больше человек. Все роли администратора были сняты с вас. Обратитесь к модерации, чтобы вернуть роли. {moderator.mention} <@&1114645156877058054> <@&1114645156877058049> <@1117200503395340420> <@507178010387152914>")
                
                del self.banns_ammount[moderator]
                del self.banns_times[moderator]
        else:
            self.banns_ammount[moderator] = 1
            self.banns_times[moderator] = f"{start_time}"


async def setup(bot):
    await bot.add_cog(Commands_Admin(bot))
