import asyncio
from unicodedata import name
import discord
import random
from discord.ext import commands
from discord.utils import get
from discord.errors import Forbidden
from discord import app_commands
from discord.app_commands import Choice
from cogs.Data.database_handler import DatabaseHandler

database_handler = DatabaseHandler('database.db')
FANBOT_VERSION = "BÊTA"


async def setup(bot):
    await bot.add_cog(Response(bot), guilds=[discord.Object(id=976578012592111646)])
    await bot.add_cog(Games(bot), guilds=[discord.Object(id=976578012592111646)])
    await bot.add_cog(Ticket(bot), guilds=[discord.Object(id=976578012592111646)])
    await bot.add_cog(Help(bot), guilds=[discord.Object(id=976578012592111646)])
    

class Response(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    antifeur = [
        "ouge",
        "-me ta gueule",
        "C'est gratuit pour les chauvres",
    ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() == "feur":
            await message.channel.send(str(self.antifeur[random.randint(0, 2)]))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.fanbot.get_channel(976578013502242816)
        await channel.send(f"{member} nous a quitté. 🪦")


class Games(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    @commands.command(help="Jouer au shifumi avec une IA.")
    async def shifumi(self, ctx):
        await ctx.message.delete()
        msg = await ctx.channel.send("Que choisissez vous ?")
        await msg.add_reaction("🪨")
        await msg.add_reaction("🍃")
        await msg.add_reaction("✂️")

        try:
            reaction, user = await self.fanbot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in ["🪨", "🍃", "✂️"], timeout=5.0)

        except asyncio.TimeoutError:
            await ctx.channel.send("Temps limite dépassé")

        if reaction.emoji == "🪨" or reaction.emoji == "🍃" or reaction.emoji == "✂️":
            list = ["🪨", "🍃", "✂️"]

            botchoice = list[random.randint(0, 2)]
            userchoice = reaction.emoji

            if userchoice == botchoice or userchoice == botchoice or userchoice == botchoice:
                await ctx.channel.send(f"Match nul! (choix de l'IA: {botchoice}")
            elif userchoice == "🪨" and botchoice == "🍃" or userchoice == "🍃" and botchoice == "✂️" or userchoice == "✂️" and botchoice == "🪨":
                await ctx.channel.send(f"Perdu! (choix de l'IA: {botchoice}")
            elif userchoice == "🪨" and botchoice == "✂️" or userchoice == "🍃" and botchoice == "🪨" or userchoice == "✂️" and botchoice == "🍃":
                await ctx.channel.send(f"Gagné! (choix de l'IA: {botchoice}")

        else:
            await ctx.channel.send("Vous ne pouvez pas choisir cela!")


class Ticket(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    @app_commands.command(name="ticket", description="Ouvre un menu déroulant pour créer un ticket.")
    @app_commands.describe(name="Votre probleme")
    @app_commands.choices(name=[
        Choice(name="Perte de données (argent, inventaire...)",
               value="Perte de données (argent, inventaire...)"),
        Choice(name="Problème avec un compte",
               value="Problème avec un compte"),
        Choice(name="Autre", value="Autre")
    ])
    async def ticket(self, interaction: discord.Interaction, name: str):
        detected = False
        for category in interaction.guild.categories:
            if category.name == "Tickets":
                detected = True

        if detected == False:
            await interaction.guild.create_category(name="Tickets")

        category = get(interaction.guild.categories, name="Tickets")

        channel_name = f"Ticket de {interaction.user.display_name}"

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
        }

        channel = await interaction.guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
        await interaction.response.send_message(f"Bonjour {interaction.user.mention} ! Un ticket a été créé pour toi.")
        await channel.send(f"Bonjour {interaction.user.mention}, présente nous ton problème ici !")


async def send_embed(ctx, embed):
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Je n'ai pas les permissions !")
        except Forbidden:
            await ctx.author.send(
                f"Salut, on dirait bien que je ne peux pas envoyer de message dans {ctx.channel.name} sur {ctx.guild.name}.\n"
                f"Pouvez-vous informer le staff du serveur de ce problème ? :slight_smile: ", embed=embed)


class Help(commands.Cog):

    def __init__(self, fanbot):
        self.fanbot = fanbot

    @commands.command()
    @commands.bot_has_permissions(add_reactions=True, embed_links=True)
    async def help(self, ctx, *input):
        await ctx.message.delete()
        prefix = "!"
        version = FANBOT_VERSION

        owner = 447791268505059349
        owner_name = "BibYTB84#8143"

        description = {
            "Economy": "Connaitre l'économie de Géopole.",
            "Government": "Gérer un gouvernement.",
            "Vote": "Faire valoir ses idées.",
            "Games": "Un ensemble de mini-jeux pour vous faire passer le temps.",
        }

        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        if not input:
            # checks if owner is on this server - used to 'tag' owner
            try:
                owner = ctx.guild.get_member(owner).mention

            except AttributeError:
                owner = owner

            emb = discord.Embed(title='Commandes et modules', color=discord.Color.blue(),
                                description=f"Utilisez `{prefix}help <module>` pour avoir plus d'information sur le module en question. "
                                            f":smiley:\n")

            # iterating trough cogs, gathering descriptions
            cogs_desc = ''
            for cog in self.fanbot.cogs:
                if cog == "FixDatabase" or cog == "Ban" or cog == "Kick" or cog == "MessageModeration" or cog == "Response" or cog == "Help" or cog == "Ticket":
                    continue
                cogs_desc += f'`{cog}`: {description.get(cog)}\n'

            # adding 'list' of cogs to embed
            emb.add_field(name='Modules', value=cogs_desc, inline=False)

            # integrating trough uncategorized commands
            commands_desc = ''
            for command in self.fanbot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'

            # adding those commands to embed
            if commands_desc:
                emb.add_field(name="N'appartient à aucun module",
                              value=commands_desc, inline=False)

            # setting information about bot
            emb.set_footer(
                text=f"Fanbot est en version {version} ! Contactez Smokyu#7645 si vous avez un problème.")

        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:

            # iterating trough cogs
            for cog in self.fanbot.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'{cog} - Commandes', description=description.get(cog),
                                        color=discord.Color.green())

                    # getting commands from cog
                    for command in self.fanbot.get_cog(cog).get_commands():
                        if command.name == "election":
                            continue
                        # if cog is not hidden
                        if not command.hidden:
                            emb.add_field(
                                name=f"`{prefix}{command.name}`", value=command.help, inline=False)
                    # found cog - breaking loop
                    break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                emb = discord.Embed(title="Qu'est-ce que c'est ?",
                                    description=f"Je n'ai jamais entendu un module s'appeller `{input[0]}` avant ! :scream:",
                                    color=discord.Color.orange())

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(title="C'est trop !",
                                description="Veuillez demander un seul module à la fois. :sweat_smile:",
                                color=discord.Color.orange())

        # sending reply embed using our own function defined above
        await send_embed(ctx, emb)
