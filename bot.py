import discord, asyncio, tomllib, os, tomli_w, json
from discord import *

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
        self.added = False

    async def on_ready(self):
            await self.wait_until_ready()
            if not self.synced:
                await tree.sync()
                self.synced = True
            activity = discord.Game(name=config["status"], type=3)
            await client.change_presence(status=discord.Status.online, activity=activity)
            print(f"Logged in as {self.user}")
            global chan
            chan = client.get_channel(config["chanid"])
            global hook
            hook = None
            for x in await chan.webhooks():
                if x.user.id == config["botid"]:
                    hook = x
            if hook is None:
                hook = await chan.create_webhook(name="ChatLink")

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(name = "addentry", description = "Posts an archive entry to an archive channel.")
@app_commands.default_permissions(administrator = True)
async def self(interaction: discord.Interaction, channel: discord.TextChannel, author: discord.Member, body: str):
    await interaction.response.defer()

client.run(config["bottoken"])