import discord
from utils.webhook_messages import WebhookMessages

class Roleplay_View(discord.ui.View):
    def __init__(self,user, asked, action, message):
        super().__init__(timeout=0)
        self.user = user
        self.asked = asked
        self.action = action
        self.message = message
    
    @discord.ui.button( style=discord.ButtonStyle.gray, emoji="✅")
    async def btn_yes(self, interaction: discord.Interaction , button: discord.ui.Button):
        if self.asked.id == interaction.user.id:
            await interaction.message.edit(content= f"{self.user.mention} {self.action} {self.asked.mention}! {self.message[0]}", embed=self.message[1], view=None)
            await interaction.response.defer()

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji="❌")
    async def btn_no(self, interaction: discord.Interaction , button: discord.ui.Button):
        if self.asked.id == interaction.user.id:
            await interaction.message.edit(embed=WebhookMessages.message_roleplay_denial(self.asked))
            await interaction.response.defer()