import logging
import os

from discord_webhook import DiscordWebhook, DiscordEmbed


class DiscordWebhookHandler(logging.Handler):
    def emit(self, record):
        webhook = DiscordWebhook(url=os.getenv('LOGGING_WEBHOOK_URL'))
        embed = DiscordEmbed(
            title=':warning:  ' + record.getMessage(),
            description=f'```{self.format(record)}```',
            color=2966946
        )
        webhook.add_embed(embed)
        webhook.execute()
