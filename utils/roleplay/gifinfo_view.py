import discord
import json
from utils.webhook_messages import WebhookMessages

class GifInfo_View(discord.ui.View):
    def __init__(self, items, category, type, user_id):
        super().__init__(timeout=0)
        self.items = items
        self.now_item = 0
        self.category = category
        self.now_item_url = items[category][0]
        self.type = type
        self.user_id = user_id

    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="◀️")
    async def button_pre(self, interaction: discord.Interaction , button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            if self.now_item != 0:
                await self.pre_gif(interaction)  

    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="▶️")
    async def button_next(self, interaction: discord.Interaction , button: discord.ui.Button):
        try:
            if interaction.user.id == self.user_id:
                if self.now_item+1 != len(self.items[self.category]):
                    await self.next_gif(interaction)
        except Exception as a:
            print(a)

    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="🗑️")
    async def button_del(self, interaction: discord.Interaction , button: discord.ui.Button):
        try:
            if interaction.user.id == self.user_id:
                self.items[self.category].remove(self.now_item_url)
                with open(f"utils/roleplay/{self.type}.json","w") as f:
                    json.dump(self.items, f)
                if len(self.items[self.category]) > 1:
                    if self.now_item+1 != len(self.items[self.category]):
                        self.now_item -= 1
                        await self.next_gif(interaction)
                    else:
                        self.now_item += 1
                        await self.pre_gif(interaction)
                else:
                    self.now_item = -1
                    await interaction.message.edit(embed= WebhookMessages.message_gif("",0,0))
                    await interaction.response.defer()
        except Exception as a:
            print(a)

    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="<a:cr0ss:1167611479827152997>")
    async def button_stop(self, interaction: discord.Interaction , button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.message.delete()
            await interaction.response.defer()

    async def next_gif(self, interaction: discord.Interaction):
        try:
            self.now_item += 1
            self.now_item_url = self.items[self.category][self.now_item]
            if self.type == "gifs":
                await interaction.message.edit(embed= WebhookMessages.message_gif(self.now_item,len(self.items[self.category]), gif = self.now_item_url))
            elif self.type == "gifs_text":
                await interaction.message.edit(embed= WebhookMessages.message_gif(self.now_item,len(self.items[self.category]), text= self.now_item_url))
            await interaction.response.defer()
        except Exception as a:
            print(a)
    
    async def pre_gif(self, interaction: discord.Interaction):
        self.now_item -= 1
        self.now_item_url = self.items[self.category][self.now_item]
        if self.type == "gifs":
            await interaction.message.edit(embed= WebhookMessages.message_gif(self.now_item,len(self.items[self.category]), gif = self.now_item_url))
        elif self.type == "gifs_text":
            await interaction.message.edit(embed= WebhookMessages.message_gif(self.now_item,len(self.items[self.category]), text=self.now_item_url))
        await interaction.response.defer()



class GifInfo_Select(discord.ui.View):
    def __init__(self, type, user_id,intr, gifs = None, texts = None):
        super().__init__(timeout=0)
        self.gifs = gifs
        self.texts = texts
        self.type = type
        self.user_id = user_id
        self.intr = intr

    @discord.ui.select( 
        placeholder = "Choose a option", 
        min_values = 1, 
        max_values = 1, 
        options = [ 
            discord.SelectOption(label="punch"),
            discord.SelectOption(label="slap"),
            discord.SelectOption(label="kiss"),
            discord.SelectOption(label="bite"),
            discord.SelectOption(label="pinch"),
            discord.SelectOption(label="hug"),
            discord.SelectOption(label="handshake"),
            discord.SelectOption(label="pat"),
            discord.SelectOption(label="react"),
            discord.SelectOption(label="sad")
        ]
    )
    async def select_callback(self,interaction ,select): 
        if self.texts != None:
            await interaction.message.edit(embed= WebhookMessages.message_gif(0,len(self.texts[select.values[0]]), text= self.texts[select.values[0]][0]), view = GifInfo_View(self.texts, select.values[0], self.type, self.user_id))
            await interaction.response.defer()

        elif self.gifs != None:
            await interaction.message.edit(embed= WebhookMessages.message_gif(0,len(self.gifs[select.values[0]]), gif = self.gifs[select.values[0]][0]), view = GifInfo_View(self.gifs, select.values[0], self.type, self.user_id))
            await interaction.response.defer()

class GifInfo_StartView(discord.ui.View):
    def __init__(self, user_id, gifs, texts):
        super().__init__(timeout=0)
        self.user_id = user_id
        self.gifs = gifs
        self.texts = texts

    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="🅰️")
    async def button_textlist(self, interaction: discord.Interaction , button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            embed = discord.Embed(color=discord.Color.yellow())
            embed.add_field(name="Выберите команду",value="Выберите команду, гифки которой будут вам показаны")
            await interaction.message.edit(embed =  embed, view = GifInfo_Select(type = "gifs_text", user_id=self.user_id ,intr=interaction,texts= self.texts))
            await interaction.response.defer()

    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="🖼️")
    async def button_giflist(self, interaction: discord.Interaction , button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            embed = discord.Embed(color=discord.Color.yellow())
            embed.add_field(name="Выберите команду",value="Выберите команду, текста которой будут вам показаны")
            await interaction.message.edit(embed =  embed, view = GifInfo_Select(type = "gifs", user_id=self.user_id ,intr=interaction,gifs= self.gifs))
            await interaction.response.defer()

    @discord.ui.button( style=discord.ButtonStyle.blurple, emoji="<a:info:1190108008353644674>")
    async def button_info(self, interaction : discord.Interaction, button : discord.ui.Button):
        pass

    @discord.ui.button(style=discord.ButtonStyle.red, emoji="<a:cr0ss:1167611479827152997>")
    async def button_del(self, interaction: discord.Interaction , button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.message.delete()
            await interaction.response.defer()

