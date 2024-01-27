import discord
from utils.config import Config

config = Config()
conf = config.get_config()

class Checks():

    @staticmethod
    def creator_check(interaction : discord.Interaction):
        if conf["FOUR_GROUP_SYSTEM"] == True:
            if any(role.id in conf["CREATORS_ROLES"].split(",") for role in interaction.user.roles):
                return True
            return False
        else:
            return True

    @staticmethod
    def adm_check(interaction : discord.Interaction):
        if conf["FOUR_GROUP_SYSTEM"] == True:
            if any(role.id in conf["ADM_ROLES"].split(",") for role in interaction.user.roles):
                return True
            return False
        else:
            return True
        
    @staticmethod
    def mod_check(interaction : discord.Interaction):
        if conf["FOUR_GROUP_SYSTEM"] == True:
            if any(role.id in conf["MOD_ROLES"].split(",") for role in interaction.user.roles):
                return True
            return False
        else:
            return True

    @staticmethod
    def lowmod_check(interaction : discord.Interaction):
        if conf["FOUR_GROUP_SYSTEM"] == True:
            if any(role.id in conf["LOWMOD_ROLES"].split(",") for role in interaction.user.roles):
                return True
            return False
        else:
            return True
