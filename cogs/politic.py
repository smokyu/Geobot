from sqlite3 import IntegrityError
import discord
from discord.ext import commands
from discord.utils import get
from cogs.Data.database_handler import DatabaseHandler
from constants import GUILD_ID

database_handler = DatabaseHandler('database.db')


async def setup(bot):
    await bot.add_cog(Government(bot), guilds=[discord.Object(id=GUILD_ID)])
    await bot.add_cog(Vote(bot), guilds=[discord.Object(id=GUILD_ID)])


class Government(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    async def defgov(self, ctx):
        roles = database_handler.get_role_name_list()
        await self.resetgov(ctx)
        for i in roles:
            role_name = i["role_name"]
            role_id = i["role_id"]
            await ctx.send(f"Désignez votre {role_name}")

            def checkMessage(message):
                return message.author == ctx.message.author and ctx.message.channel == message.channel

            try:
                user = await self.fanbot.wait_for("message", timeout=20, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            user = user.mentions[0]
            role = ctx.guild.get_role(role_id)
            await user.add_roles(role)

    async def resetgov(self, ctx):
        roles_id = database_handler.get_role_name_list()
        for role_id in roles_id:
            role_id = role_id["role_id"]
            async for member in ctx.guild.fetch_members():
                role = ctx.guild.get_role(int(role_id))
                if role in member.roles:
                    await member.remove_roles(role)

    @commands.command(help="Définir son gouvernement.")
    @commands.has_role(976578012659220524)
    async def setgov(self, ctx):
        await ctx.message.delete()
        await self.defgov(ctx)

    @commands.command(help="Créer un rôle de ministre.")
    @commands.has_role(976578012659220524)
    async def addgov(self, ctx, *role: str):
        await ctx.message.delete()
        role = " ".join(role)
        role_create = await ctx.guild.create_role(name=role)
        database_handler.add_role(
            role_name=role_create.name, role_id=role_create.id)

    @commands.command(help="Supprimer un rôle de ministre.")
    @commands.has_role(976578012659220524)
    async def removegov(self, ctx, role: discord.Role = None):
        if role is None:
            await ctx.send("Vous n'avez pas spécifié le rôle à supprimer. Merci de retaper la commande.")
            return
        await ctx.message.delete()
        await role.delete()
        database_handler.remove_role(role_id=role.id)


class Vote(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    @commands.command(help="Présenter sa candidature à l'élection présidentielle.")
    async def candidate(self, ctx):
        await ctx.message.delete()
        await ctx.send("Êtes-vous vraiment sûr de vouloir candidater à la présidence de Fangosp ? *(oui, non)*")

        def checkMessage(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        try:
            choice = await self.fanbot.wait_for("message", timeout=10, check=checkMessage)
        except:
            await ctx.send("Temps dépassé!")
            return

        if "oui" == choice.content.lower():
            try:
                database_handler.add_candidate(user_id=ctx.message.author.id)
                await ctx.send("Votre participation a bien été ajoutée à la base de données !")
            except IntegrityError:
                await ctx.send("Vous êtes déjà candidat.")
        else:
            return

    @commands.command(help="Retirer sa candidature à l'élection présidentielle.")
    async def removecandidate(self, ctx):
        await ctx.message.delete()
        candidates = database_handler.get_candidate_list()
        for i in candidates:
            if ctx.message.author.id == i["user_id"]:
                database_handler.remove_candidate(
                    user_id=ctx.message.author.id)
                await ctx.send("Vous n'êtes plus candidat.")
                return
        await ctx.send("Vous n'êtes pas candidat.")

    @commands.command(help="Connaître les candidats à la présidentielle")
    async def candidatelist(self, ctx):
        await ctx.message.delete()
        candidates = database_handler.get_candidate_list()
        candidates_list = []
        for i in candidates:
            candidates_list.append(i["user_id"])

        if len(candidates_list) == 0:
            await ctx.send("Aucun candidat ne s'est présenté pour le moment.")
            return

        for j in candidates_list:
            user = ctx.message.guild.get_member(j)
            await ctx.send(user)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def election(self, ctx):
        await ctx.message.delete()
        candidates = database_handler.get_candidate_list()
        database_handler.reset_candidate_list()
        candidates_list = []

        for i in candidates:
            candidates_list.append(i["user_id"])

        if len(candidates_list) == 0:
            await ctx.send("Aucun candidat ne s'est présenté pour le moment.")
            return

        await ctx.send("__Voici les candidats à cette élection__:")
        for j in candidates_list:
            user = ctx.message.guild.get_member(j)
            choice = await ctx.send(user.mention)
            await choice.add_reaction('✅')
