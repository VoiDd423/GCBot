import discord
from utils.webhook_messages import WebhookMessages

class Leaders_View(discord.ui.View):
    def __init__(self,now_page, max_page, top, user_id):
        super().__init__(timeout=0)
        self.max_page = max_page
        self.now_page = now_page
        self.top = top
        self.user_id = user_id

    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="⏪")
    async def btn_f(self, interaction: discord.Interaction , button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            if self.now_page != 1:
                self.now_page = 1
                await interaction.message.edit(embed=WebhookMessages.message_leaders(self.now_page,self.max_page,self.top))
                await interaction.response.defer()
            

    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="◀️")
    async def btn_p(self, interaction: discord.Interaction , button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            if self.now_page != 1:
                self.now_page -= 1
                await interaction.message.edit(embed=WebhookMessages.message_leaders(self.now_page,self.max_page,self.top))
                await interaction.response.defer()


    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="▶️")
    async def btn_n(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            if self.now_page != self.max_page:
                self.now_page += 1
                await interaction.message.edit(embed=WebhookMessages.message_leaders(self.now_page,self.max_page,self.top))
                await interaction.response.defer()
        
    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="⏩")
    async def btn_l(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            if self.now_page != self.max_page:
                self.now_page = self.max_page
                await interaction.message.edit(embed=WebhookMessages.message_leaders(self.now_page,self.max_page,self.top))
                await interaction.response.defer()

    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="<a:cr0ss:1167611479827152997>")
    async def btn_s(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.message.delete()
            await interaction.response.defer()
