import discord
import json
import datetime
from pymongo import MongoClient
from discord.ext import commands
from discord import app_commands
from utils.config import Config
from utils.webhook_messages import WebhookMessages
from utils.roleplay.gifinfo_view import GifInfo_StartView

config = Config()
conf = config.get_config()

client = MongoClient(conf["MONGO_URI"])
db = client["gameclub-bot"]
collection = db["punishments"]
exp_table = db["exp_table"]

class Commands_Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.categories = ["kick", "slap", "kiss", "fkiss", "bite", "pinch", "hug", "handshake", "pat", "react", "sad"]

    @app_commands.command(name="help", description="Получить список всех команд")
    @commands.has_any_role("Supreme", "Tester")
    async def help(self, interaction : discord.Interaction):
        embed = discord.Embed(
            title="Commands", color=discord.Color.red(), timestamp=datetime.datetime.now())
        embed.add_field(name="Administration", value="`/take_role` `/kick` `/ban` `/mute` `/warn` `/unmute` `/unban` `/unwarn`")
        embed.add_field(name="Exp", value="`!leaders` `!rank`")
        embed.add_field(name="Roleplay", value="`!kick` `!slap` `!kiss` `!fkiss` `!bite` `!pinch` `!hug` `!handshake` `!pat` `!react` `!sad`")
        embed.add_field(name="Settings", value="`/gif_info` - выводит информацию о гифках.\n"
                    "`/add_gif` - добавляет гифку.\n"
                    "`/add_gif_text` - добавляет текст для гифки.\n"
                    "`/command_channel` - устанавливает канал для команд.\n"
                    "`/set_moderation_role` - устанавливает роль модератора.\n"
                    "`/turn_off` - выключает бота.\n"
                    "`/set_no_exp_voice` - устанавливает войсы в которых не зачисляеться опыт.\n"
                    "`/set_exp_factor` - множитель между уровнями.\n"
                    "`/delete_from_statistic` - удаляет человека из топа.\n")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name = "gif_info", description="Выводит количество гифок") 
    @commands.has_any_role("Supreme", "Tester")
    async def gif_info(self, interaction : discord.Interaction):
        try:
            with open("utils/roleplay/gifs.json","r") as f:
                gifs = json.load(f)
            with open("utils/roleplay/gifs_text.json","r") as f:
                texts = json.load(f)
            embed = WebhookMessages.mesage_gif_info(gifs,texts)
            await interaction.response.send_message(embed=embed, view= GifInfo_StartView(interaction.user.id, gifs,texts))
        except Exception as a:
            print(a)

    @app_commands.command(name = "add_gif", description="Добавить гифку. Выберите категорию и добавьте url gif") 
    @commands.has_any_role("Supreme", "Tester")
    async def add_gif(self, interaction : discord.Interaction, category : str, url : str):
        if category in self.categories:
            if url.endswith(".gif"):
                with open("utils/roleplay/gifs.json","r") as f:
                    gifs = json.load(f)
                if category not in gifs:
                    with open("utils/roleplay/gifs.json","w") as f:
                        gifs[category] = [url]
                        json.dump(gifs, f)
                    await interaction.response.send_message(f"Cозданна категория - {category}. Гиф был добавлен в нее")
                else:
                    if url not in gifs[category]:
                        with open("utils/roleplay/gifs.json","w") as f:
                            gifs[category].append(url)
                            json.dump(gifs, f)
                        await interaction.response.send_message(f"Гиф добавлена в категорию - {category}")
                    else:
                        await interaction.response.send_message("Данная gif уже добавлена", ephemeral=True)
            else:
                await interaction.response.send_message("Неправильный тип ссылки!", ephemeral=True)
        else:
            await interaction.response.send_message("Такой категории не может быть!",ephemeral=True)

    @app_commands.command(name = "add_gif_text", description="Добавить текст под гифку") 
    @commands.has_any_role("Supreme", "Tester")
    async def add_gif_text(self, interaction : discord.Interaction, category : str, text : str):
        if category in self.categories:
            with open("utils/roleplay/gifs_text.json","r") as f:
                texts = json.load(f)
            if category not in texts:
                with open("utils/roleplay/gifs_text.json","w") as f:
                    texts[category] = [text]
                    json.dump(texts, f)
                await interaction.response.send_message(f"Cозданна категория - {category}. Текст был добавлен в нее")
            else:
                if text not in texts[category]:
                    with open("utils/roleplay/gifs_text.json","w") as f:
                        texts[category].append(text)
                        json.dump(texts, f)
                    await interaction.response.send_message(f"Текст добавлен в категорию - {category}")
                else:
                    await interaction.response.send_message("Данный текст уже добавлен", ephemeral=True)
        else:
            await interaction.response.send_message("Такой категории не может быть!",ephemeral=True)

    @app_commands.command(name="set_command_channel", description="Установить канал с уведомлениями о новом уровне")
    @commands.has_any_role("Supreme", "Tester")
    async def command_channel(self, interaction: discord.Interaction, channel_id: str):
        conf["COMMANDS_CHANNEL"] = int(channel_id)
        with open("config.json", "w") as f:
            json.dump(conf, f)

    @app_commands.command(name="set_moderation_role", description="Установить роль модерации")
    @commands.has_any_role("Supreme", "Tester")
    async def set_moderation_role(self, interaction: discord.Interaction, role: discord.Role):
        mod_id = role.id
        a = []
        try:
            with open("utils/punishments/moderator_roles_id.json", "r") as f:
                a = json.load(f)
        except: pass
        a.append(mod_id)
        with open("utils/punishments/moderator_roles_id.json", "w") as f:
            json.dump(a, f)
        await interaction.response.send_message(content=f"Роль {role.mention} установленна!")
    
    @app_commands.command(name="turn_off_bot", description="Выключает бота")
    @commands.has_any_role("Supreme","Tester")
    async def turn_off(self, interaction : discord.Interaction):
        try:
            for member in interaction.guild.members:
                if member.voice is not None and member.voice.channel is not None:
                    await member.move_to(member.voice.channel)
            await interaction.response.send_message("Бот выключен!")
            await self.bot.close()
            print("Bot turned off")
        except Exception as a:
            print(a)

    @app_commands.command(name="set_exp_factor", description="Установить множитель опыта.")
    @commands.has_any_role("Supreme", "Tester")
    async def set_exp_factor(self, interaction : discord.Interaction, factor : float):
        conf["EXP_FACTOR"] = factor
        config.write_config(conf)


async def setup(bot):
    await bot.add_cog(Commands_Settings(bot))
