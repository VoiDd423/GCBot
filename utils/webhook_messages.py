import discord
import datetime

class WebhookMessages():
    @staticmethod
    def message_punishment_bot(type : str, member, moderator, reason = None, time=None, role = None):
        embed = discord.Embed(
            title=type, color=discord.Color.red(), timestamp=datetime.datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name="Участник", value=member.mention)
        embed.add_field(name="ID", value=member.id)
        if time != None:
            embed.add_field(name="Время", value=time)
        if role != None:
            embed.add_field(name="Роль", value=role.mention)
        embed.add_field(name="Модератор", value=moderator.mention)
        embed.add_field(name="Причина", value=reason)
        return embed
    
    @staticmethod
    def message_unban(member, moderator, type):
        embed = discord.Embed(title=type, color=discord.Color.green(
        ), timestamp=datetime.datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name="Участник", value=member.mention)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Модератор", value=moderator.mention)
        return embed
    
    @staticmethod
    def message_leaders(now_page: int, all_pages: int, top):
        all_members_count =len(top)
        embed = discord.Embed(title=f"Cтраница {now_page} из {all_pages} - Всего участников {all_members_count}", color=discord.Color.red(), timestamp=datetime.datetime.now())
        em_value = ''
        if now_page == 1:
            amount = 10 if all_members_count >= 10 else all_members_count
            for i in range(amount):
                star = "<:3715trophy1:1167615508036718673>" if i == 0 else "<:trophy2:1167612938538983445>" if i == 1 else "<:trophy3:1167612952652816445>" if i == 2 else " "
                microphone_time = top[i+1]["VOICE_TIME"] if top[i+1]["VOICE_TIME"][1] != ":" else "0" + top[i+1]["VOICE_TIME"]
                em_value = em_value + f"{star}**#{i+1}.{top[i+1]['NAME']}**\nУровень: {top[i+1]['LVL']} | Опыт: {top[i+1]['EXP']} | :microphone:{microphone_time}\n\n"
        else:
            amount = 10 if all_members_count-((now_page-1)*10) >= 10 or (all_members_count-((now_page-1)*10))%10 == 0 else (all_members_count-((now_page-1)*10))%10
            for i in range(amount):
                top_place = top[i+((now_page-1)*10)+1]
                microphone_time = ":".join([part.zfill(2) for part in top_place['VOICE_TIME'].split(":")])
                em_value = em_value + f"**#{(now_page-1)*10+i+1}.{top_place['NAME']}**\nУровень: {top_place['LVL']} | Опыт: {top_place['EXP']} | :microphone:{microphone_time}\n\n"
        embed.add_field(name = "<a:314124124:1163132905141321878> Топ рейтинга участников",value = f"\n{em_value}")
        return embed
    
    @staticmethod
    def message_unmute_bot(member, type):
        embed = discord.Embed(
            title=f"Автоматическое снятие {type}а",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(),
        )
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name="Участник", value=member.mention)
        embed.add_field(name="ID", value=member.id)
        return embed

    @staticmethod
    def message_punishment(title, moderator,reason,end_time = "None", role= None):
        embed = discord.Embed(
            title=title, color=discord.Color.red(), timestamp=datetime.datetime.now())
        embed.add_field(name="Модератор", value=f"**{moderator.mention}**")
        embed.add_field(name="Причина", value=f"**{reason}**")
        if role != None:
            embed.add_field(name="Снятая роль", value=f"**{role.mention}**")
        if end_time != None:
            embed.add_field(name="Время окончания", value=f"**{str(end_time)}**")
        return embed
    
    @staticmethod
    def message_unmute(title, moderator):
        embed = discord.Embed(
            title=title, color=discord.Color.red(), timestamp=datetime.datetime.now())
        embed.add_field(name="Модератор", value=f"**{moderator.mention}**")
        return embed
    
    @staticmethod
    def message_new_lvl(member, lvl, top_place, exp_next_lvl, voice_time):
        embed = discord.Embed(color=discord.Color.blue())
        try:
            embed.set_thumbnail(url=member.avatar.url)
        except:
            embed.set_thumbnail("https://images-eds-ssl.xboxlive.com/image?url=4rt9.lXDC4H_93laV1_eHHFT949fUipzkiFOBH3fAiZZUCdYojwUyX2aTonS1aIwMrx6NUIsHfUHSLzjGJFxxsG72wAo9EWJR4yQWyJJaDb6rYcBtJvTvH3UoAS4JFNDaxGhmKNaMwgElLURlRFeVkLCjkfnXmWtINWZIrPGYq0-&format=source")
        embed.add_field(
        name="⭐️**Level Up**⭐️",
        value=f"Ты только что повысил свой уровень, {member.mention}.\n"
                f"Поздравляю тебя с `{lvl}` уровнем!\n"
                f"\n<a:dot:1130253812406439986> Требуемый опыт до следующего уровня: `{exp_next_lvl}`"
                f"\n<a:dot:1130253812406439986> Время в войсах: `{voice_time}`\n"
                f"<a:dot:1130253812406439986> Номер топа на сервере: `{top_place}`\n"
                "\n<a:line_2:1130253358733729974> Чтобы узнать подробнее пропишите команду: `!rank`"
        )
        embed.set_footer()
        return embed
    
    @staticmethod
    def mesage_gif_info(gifs : dict, texts : dict):
        embed = discord.Embed(title=f"Информация о гифках",color=discord.Color.blue())
        em_value = ''
        for gif in gifs:
            em_value =  em_value + f"!{gif}\nGif:{len(gifs[gif])} , Text : {len(texts.get(gif)) if texts.get(gif, 0) != 0 else 0 }\n\n"
        embed.add_field(name="INFO", value=em_value)
        return embed
    
    @staticmethod
    def message_roleplay_ask(asked, action): 
        embed = discord.Embed(color=discord.Color.dark_gray())
        embed.add_field(name="Разрешение", value=f"Пользователь {asked.mention} хочет {action}. Разрешаете ли вы ему(ей)?")
        return embed

    @staticmethod
    def message_roleplay_denial(asked):
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="Отказ!", value=f"Пользователь {asked.mention} отказался. :(")
        return embed

    @staticmethod
    def message_gif(now_gif, all_gifs, gif = None, text = ""):
        embed = discord.Embed(color=discord.Color.yellow())
        embed.add_field(name=f"{now_gif+1} из {all_gifs}", value=text)
        if gif != None:
            embed.set_image(url = gif)
        return embed