import discord
import json
from random import randint
from discord.ext import commands
from utils.webhook_messages import WebhookMessages
from utils.roleplay.rolepay_view import Roleplay_View
from utils.config import Config

config = Config()
conf = config.get_config()

class Commands_Roleplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.actions = {"kiss" : {"ru" : ["поцеловал", "вас поцеловать"], "en" : ["kissed", "to kiss you"]},
                        "fkiss" : {"ru" : ["засосать", "вас засосать"], "en" : ["kissed", "to kiss you"]},
                        "handshake" : {"ru" : ["пожал руку", "вам пожать руку"], "en" : ["shaked your hand", "to shake your hand"]}}
        self.lng = conf["LANGUAGE"]
        
    @commands.command(name="kick")
    async def kick (self, ctx, member: discord.Member):
        if await self.self_check(member, ctx):
            message = self.generate_message("kick")
            await ctx.send(f"{ctx.message.author.mention} ударил {member.mention}!{message[0]}", embed=message[1])

    @commands.command(name="slap")
    async def slap (self, ctx, member: discord.Member):
        if await self.self_check(member, ctx):
            message = self.generate_message("slap")
            await ctx.send(f"{ctx.message.author.mention} дал пощечину {member.mention}! {message[0]}", embed=message[1])

    @commands.command(name="kiss")
    async def kiss (self, ctx, member: discord.Member):
        if await self.self_check(member, ctx, self_check= True):
            await self.message_send(ctx,member,"kiss")

    @commands.command(name="fkiss") 
    async def fkiss (self, ctx, member: discord.Member):
        if await self.self_check(member, ctx, self_check= True):
            await self.message_send(ctx,member,"fkiss")

    @commands.command(name="bite")
    async def bite (self, ctx, member: discord.Member):
        if await self.self_check(member, ctx):
            message = self.generate_message("bite")
            await ctx.send(f"{ctx.message.author.mention} укусил {member.mention}! {message[0]}", embed=message[1])

    @commands.command(name="pinch")
    async def pinch (self, ctx, member: discord.Member):
        if self.self_check(member, ctx):
            message = self.generate_message("pinch")
            await ctx.send(f"{ctx.message.author.mention} ущипнул {member.mention}! {message[0]}", embed=message[1])

    @commands.command(name="hug")
    async def hug (self, ctx, member: discord.Member):
        if await self.self_check(member, ctx):
            message = self.generate_message("hug")
            await ctx.send(f'{ctx.message.author.mention} обнял {member.mention}! {message[0]}', embed=message[1])

    @commands.command(name="handshake")
    async def handshake (self, ctx, member: discord.Member):
        if await self.self_check(member, ctx, self_check=True):
            await self.message_send(ctx,member,"handshake")

    @commands.command(name="pat")
    async def pat (self, ctx, member: discord.Member):
        if await self.self_check(member, ctx, self_check= True):
            message = self.generate_message("pat")
            await ctx.send(f'{ctx.message.author.mention} погладил {member.mention}! {message[0]}', embed=message[1])

    @commands.command(name="react")
    async def react (self, ctx):
        message = self.generate_message("react")
        await ctx.send(f"Рекация {ctx.message.author.mention}...", embed=message[1])

    @commands.command(name="sad")
    async def sad (self, ctx):
        message = self.generate_message("sad")
        await ctx.send(f"{ctx.message.author.mention} загрустил!{message[0]}", embed=message[1])

    def generate_message(self, action):
        text = None
        if action != "react":
            with open("utils/roleplay/gifs_text.json","r") as f:
                texts = json.load(f)
            text = texts[action][randint(0, len(texts[action]) - 1)]

        with open("utils/roleplay/gifs.json","r") as f:
            gifs = json.load(f)
        img = gifs[action][randint(0, len(gifs[action]) - 1)]
        embed = discord.Embed()
        embed.set_image(url=img)
        return [text,embed]

    async def message_send(self,ctx ,member, action):
        message = self.generate_message(action)
        await ctx.send(f"||{member.mention}||", embed = WebhookMessages.message_roleplay_ask(ctx.message.author, self.actions[action][self.lng][0]), 
                       view = Roleplay_View(ctx.message.author, member, self.actions[action][self.lng][0],message))
    
    async def self_check(self, member, ctx, self_check = False):
        if self_check == True:
            if ctx.message.author.id == member.id:
                await ctx.send("Вы не можете использовать эту команду на себя.")
                return False
        if member.bot:
            await ctx.send("Вы не можете использовать эту команду на бота.")
            return False
        return True

async def setup(bot):
    await bot.add_cog(Commands_Roleplay(bot))
