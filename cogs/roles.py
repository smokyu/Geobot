import discord

async def createMutedRole(ctx):
    mutedRole = await ctx.guild.create_role(name = "Mute",
                                            permissions = discord.Permissions(
                                                send_messages = False,
                                                speak = False),
                                            reason = "Creation du role Mute (FANBOT)")
    return mutedRole

async def getMutedRole(ctx):
    roles = ctx.guild.roles
    for role in roles:
        if role.name == "Mute":
            return role
        
    return await createMutedRole(ctx)


async def createMutedTextRole(ctx):
    mutedTextRole = await ctx.guild.create_role(name = "Mute_texte",
                                            permissions = discord.Permissions(
                                                send_messages = False),
                                            reason = "Creation du role Mute_texte (FANBOT)")
    return mutedTextRole

async def getMutedTextRole(ctx):
    roles = ctx.guild.roles
    for role in roles:
        if role.name == "Mute_texte":
            return role
        
    return await createMutedTextRole(ctx)


async def createMutedAudioRole(ctx):
    mutedVocalRole = await ctx.guild.create_role(name = "Mute_vocal",
                                            permissions = discord.Permissions(
                                                speak = False),
                                            reason = "Creation du role Mute_vocal (GEOBOT)")
    return mutedVocalRole

async def getMutedAudioRole(ctx):
    roles = ctx.guild.roles
    for role in roles:
        if role.name == "Mute_vocal":
            return role
        
    return await createMutedAudioRole(ctx)