import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class Blank():
    def make_blank(name, exp, exp_next_lvl ,lvl, voice, top):
        image = Image.open('pictures/blank_bg.png')
        image = image.resize((900, 400))

        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("Montserrat-SemiBold.ttf", 30, encoding="unic")

        name_x = 380 if len(name) >= 15 else 380+(3*(15-len(name)))

        text_and_coordinates = [
            (f'{exp} / {exp_next_lvl} опыт', (142, 290)),
            (f'@{name}', (name_x, 320)),
            (voice, (635, 313)),
            (f'Уровень: {lvl}', (142, 313)),
            (f'Топ {top}', (685, 40))
        ]

        for text, (x, y) in text_and_coordinates:
            font_size = 20 if "@" in text or 'опыт' in text else (25 if 'Ранг' in text else 30)
            font = ImageFont.truetype("Montserrat-SemiBold.ttf", font_size, encoding="unic")
            draw.text((x, y), text, fill="white", font=font)


        avatar = Image.open(f'pictures/{name}_avatar.png')
        avatar = avatar.resize((140, 140))

        mask = Image.new("L", (140, 140), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 140, 140), fill=255)

        avatar.putalpha(mask)
        image.paste(avatar, (380, 130), avatar)
        
        image.save(f'pictures/{name}_blank.png')
        image.close()

    def get_avatar(member):
        try:
            avatar_url = member.avatar
            response = requests.get(avatar_url)
            image = Image.open(BytesIO(response.content))
        except:
            image = Image.open("pictures/standart.png")
        image = image.resize((140, 140), Image.LANCZOS)

        mask = Image.new("L", (140, 140), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 140, 140), fill=255)

        image.putalpha(mask)
        image = image.convert("RGB")
        image.save(f"pictures/{member.name}_avatar.png")
        image.close()