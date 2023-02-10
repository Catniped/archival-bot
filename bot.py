import discord, tomllib, typing
from discord import *

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

class aclient(discord.Client):
    clipboard = ""
    aclipboard = []
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
            global botid
            botid = self.user.id

class EditModal(ui.Modal, title='Edit message'):
    def __init__(self, deftext, message):
        super().__init__()
        self.message = message
        self.answer = ui.TextInput(label='Text', style=discord.TextStyle.paragraph, default=deftext)
        self.add_item(self.answer)
    async def on_submit(self, interaction: discord.Interaction):
        hook = await get_webhook(self.message.channel)
        await hook.edit_message(message_id=self.message.id, content=self.answer.value)
        await interaction.response.send_message("Edited!", ephemeral=True)

# class PostModal(ui.Modal, title='Post message'):
#     def __init__(self):
#         super().__init__()
#         self.answer = ui.TextInput(label='Text', style=discord.TextStyle.paragraph)
#         self.add_item(self.answer)
#         self.tname = ui.TextInput(label='Thread name', style=discord.TextStyle.short, required=False)
#         self.add_item(self.tname)
#     async def on_submit(self, interaction: discord.Interaction):
#         hook = await get_webhook(self.message.channel)
#         await hook.edit_message(message_id=self.message.id, content=self.answer.value)
#         await interaction.response.send_message("Edited!", ephemeral=True)

client = aclient()
tree = app_commands.CommandTree(client)

async def get_webhook(chan):
    hook = None
    for x in await chan.webhooks():
        if x.user.id == botid:
            hook = x
    if hook is None:
        hook = await chan.create_webhook(name="Archive Webhook")
    return(hook)

@tree.context_menu(name="Copy")
async def react(interaction: discord.Interaction, message: discord.Message):
    aclient.clipboard = message.content
    ls = []
    for x in message.attachments:
        ls.append(await x.to_file())
    aclient.aclipboard = ls
    await interaction.response.send_message('Copied message content! run /addentry or /editentry to apply this!', ephemeral=True)

@tree.command(name = "addentry", description = "Posts an archive entry to an archive channel.")
@app_commands.default_permissions(administrator = True)
async def self(interaction: discord.Interaction, channel: discord.TextChannel, author: discord.Member, threadname: typing.Optional[str] = None):
    await interaction.response.defer()
    hook = await get_webhook(channel)
    try:
        if aclient.aclipboard != []:
            msg = await hook.send(content=aclient.clipboard, username=author.name, avatar_url=author.avatar.url, files=aclient.aclipboard, wait=True)
        else:
            msg = await hook.send(content=aclient.clipboard, username=author.name, avatar_url=author.avatar.url, wait=True)
        if threadname is not None:
            await msg.create_thread(name=threadname)
        else:
            await msg.create_thread(name=aclient.clipboard.split("\n")[0])
        aclient.clipboard = ""
        aclient.aclipboard = []
        await interaction.followup.send("Added!", ephemeral=True)
    except:
        await interaction.followup.send("Failed to add entry. Did you copy a message?", ephemeral=True)

@tree.context_menu(name="Edit")
@app_commands.default_permissions(administrator = True)
async def self(interaction: discord.Interaction, message: discord.Message):
    if message.author.bot:
        await interaction.response.send_modal(EditModal(message.content, message))
    else:
        await interaction.response.send_message("Unable to edit this message.", ephemeral=True)

@tree.command(name = "test", description = "Edits an archive entry in an archive channel.")
@app_commands.default_permissions(administrator = True)
async def self(interaction: discord.Interaction, textuwu: str):
    await interaction.response.send_modal(EditModal(textuwu))

client.run(config["bottoken"])