from typing import List
from dhooks import Webhook, Embed

from Klassen.angebot import Angebot
from config import get_config

CONFIG = get_config()


def send_message(title, angebote: List[Angebot]):
    hook = Webhook(CONFIG["webhook_url"])

    if angebote:
        content = "\n".join(
            [f"{angebot.name} [{angebot.price}€]" for angebot in angebote])

        embed = Embed(
            title=f"**{title}**",
            description=f"```css\n{content}```",
            timestamp='now'
        )

        hook.send(embed=embed)
    else:
        ...
