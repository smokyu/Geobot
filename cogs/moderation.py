from email.message import Message
import discord
from discord.ext import commands
from cogs.roles import getMutedRole

async def setup(bot):
    await bot.add_cog(Ban(bot), guilds = [discord.Object(id = 976578012592111646)])
    await bot.add_cog(Kick(bot), guilds = [discord.Object(id = 976578012592111646)])
    await bot.add_cog(MessageModeration(bot), guilds = [discord.Object(id = 976578012592111646)])

class Ban(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    @commands.command(description="")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member = None, *, reason: str = None):
        if user is None:
            await ctx.send("Vous n'avez pas spécifié la personne qui doit être bannie. Merci de retaper la commande")
            return
        if reason is None:
            reason = "Aucune raison n'a été renseignée"
        await ctx.message.delete()
        reason = " ".join(reason)
        await ctx.guild.ban(user, reason=reason)

        embed = discord.Embed(title="Sanction")
        embed.add_field(name=f"Le membre **{user.mention}** a été banni.", description=f"Raison={reason}")
        await ctx.send(embed=embed)

    @commands.command(description="")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: str = None, *, reason: str = None):
        if user is None:
            await ctx.send("Vous n'avez pas spécifié la personne qui ne doit plus être bannie. Merci de retaper la commande")
            return
        if reason is None:
            reason = "Aucune raison n'a été renseignée"
        await ctx.message.delete()
        reason = " ".join(reason)
        userName, userId = user.split("#")
        bannedUsers = ctx.guild.bans()
        async for i in bannedUsers:
            if i.user.name == userName and i.user.discriminator == userId:
                await ctx.guild.unban(i.user, reason=reason)

                embed = discord.Embed(title="Sanction")
                embed.add_field(name=f"Le membre **{user}** a été débanni.", description=f"Raison={reason}")
                await ctx.send(embed=embed)
                return
        await ctx.send(f"L'utilisateur {user} n'est pas banni.")

    @commands.command(description="")
    @commands.has_permissions(ban_members=True)
    async def banlist(self, ctx):
        await ctx.message.delete()
        async for guild in self.fanbot.fetch_guilds(limit=50):
            if guild == ctx.guild:
                embed = discord.Embed(title=f"Liste des bannis de {guild}", color=0x552E12)
                banned_Users = guild.bans()
                async for banned_user in banned_Users:
                    embed.add_field(name=banned_user.user, value=banned_user.user.id, inline=False)
                await ctx.send(embed=embed)
                return
            
class Kick(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    @commands.command(description="")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member = None, *, reason="Aucune raison n'a été renseignée"):
        if user is None:
            await ctx.send("Vous n'avez pas spécifié la personne qui ne doit plus être muée. Merci de retaper la commande")
            return
        await ctx.message.delete()
        reason = " ".join(reason)
        await ctx.guild.kick(user, reason=reason)

        embed = discord.Embed(title="Sanction")
        embed.add_field(name=f"Le membre **{user.mention}** a été expulsé.", description=f"Raison={reason}")
        await ctx.send(embed=embed)


class MessageModeration(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    @commands.command(description="")
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, amount: int = 1):
        await ctx.channel.purge(limit=amount + 1)

    @commands.command(description="")
    async def mute(self, ctx, user: discord.Member=None, *, reason="Aucune raison n'a été renseigné"):
        if user is None:
            await ctx.send("Vous n'avez pas spécifié la personne qui ne doit plus être muée. Merci de retaper la commande")
            return
        await ctx.message.delete()
        mutedRole = await getMutedRole(ctx)
        await user.add_roles(mutedRole, reason=reason)

        embed = discord.Embed(title="Sanction")
        embed.add_field(name=f"Le membre **{user.mention}** est devenu mué.", description=f"Raison={reason}")
        await ctx.send(embed=embed)

    @commands.command(description="")
    async def unmute(self, ctx, user: discord.Member=None, *, reason="Aucune raison n'a été renseigné"):
        if user is None:
            await ctx.send("Vous n'avez pas spécifié la personne qui ne doit plus être muée. Merci de retaper la commande")
            return
        await ctx.message.delete()
        mutedRole = await getMutedRole(ctx)
        await user.remove_roles(mutedRole, reason=reason)

        embed = discord.Embed(title="Sanction")
        embed.add_field(name=f"Le membre **{user.mention}** n'est plus mué.", description=f"Raison={reason}")
        await ctx.send(embed=embed)