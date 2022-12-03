import discord

async def createMutedRole(ctx):
    mutedRole = await ctx.guild.create_role(name = "Mute",
                                            permissions = discord.Permissions(
                                                send_messages = False,
                                                speak = False),
                                            reason = "Creation du role Mute (FANBOT)")
    for channel in ctx.guild.channels:
        await channel.set_permissions(mutedRole, send_messages = False, speak = False)
    return mutedRole

async def getMutedRole(ctx):
    roles = ctx.guild.roles
    for role in roles:
        if role.name == "Mute":
            return role
        
    return await createMutedRole(ctx)