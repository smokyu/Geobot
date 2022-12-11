import math
from sqlite3 import IntegrityError
import discord
import datetime
import re
import cogs.colors
from discord.ext import commands
from discord.ui import Select
from discord.utils import get
from cogs.Data.database_handler import DatabaseHandler
from constants import GUILD_ID

database_handler = DatabaseHandler('database.db')
now = datetime.datetime.now()


async def setup(bot):
    await bot.add_cog(Economy(bot), guilds=[discord.Object(id=GUILD_ID)])
    await bot.add_cog(Company(bot), guilds=[discord.Object(id=GUILD_ID)])
    await bot.add_cog(Production(bot), guilds=[discord.Object(id=GUILD_ID)])
    await bot.add_cog(Patent(bot), guilds=[discord.Object(id=GUILD_ID)])

class Economy(commands.Cog):
    def __init__(self, fanbot: commands.Bot) -> None:
        self.fanbot = fanbot

    @commands.command(help="Connaitre l'argent de quelqu'un.", aliases=["balance"])
    async def money(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if member is None:
            member = ctx.message.author
        try:
            database_handler.create_account(user_id=member.id)
        except IntegrityError:
            pass
        finally:
            account = database_handler.get_account(user_id=member.id)
            member = ctx.message.guild.get_member(member.id)
            embed = discord.Embed(
                title=f"Porte-feuille de {member.display_name}", color=cogs.colors.ECONOMY_COLOR_EMBED)
            embed.add_field(name="Argent (compte courant)",
                            value=f"{account[0]} 🪙")
            embed.add_field(name="Argent (en action)", value="🚧 En travaux 🚧")
            await ctx.send(embed=embed)

    @commands.command(help="Envoyer de l'argent à quelqu'un.")
    async def pay(self, ctx, member: discord.Member = None, amount: int = 0):
        
        if member is None:
            await ctx.send("Vous n'avez pas défini qui doit recevoir l'argent.. merci de retaper la commmande.")
            if amount == 0:
                await ctx.send("Vous n'avez pas spécifié le montant.. merci de retaper la commande.")
            return
        elif amount == 0:
            await ctx.send("Vous n'avez pas spécifié le montant.. merci de retaper la commande.")
            return
        if member.id == ctx.message.author.id:
            await ctx.send("Vous ne pouvez pas vous donner de l'argent à vous-même !")
            return
        await ctx.message.delete()
        try:
            database_handler.create_account(user_id=member.id)
        except IntegrityError:
            pass
        try:
            database_handler.create_account(user_id=ctx.message.author.id)
        except IntegrityError:
            pass

        current_balance = database_handler.get_account(user_id=ctx.message.author.id)
        
        if current_balance[0] < amount:
            await ctx.send("Vous n'avez pas assez d'argent !")
            return

        member_account = database_handler.get_account(user_id=member.id)
        author_account = database_handler.get_account(
            user_id=ctx.message.author.id)
        author = ctx.message.guild.get_member(ctx.message.author.id)

        withdraw = database_handler.withdraw(
            user_id=ctx.message.author.id, amount=amount)
        deposit = database_handler.deposit(user_id=member.id, amount=amount)

        embed = discord.Embed(title="Transfert d'argent",
                              color=cogs.colors.ECONOMY_COLOR_EMBED)
        embed.add_field(name="__**Payeur**__",
                        value=f"{author.display_name} (-{str(amount)} 🪙)")
        embed.add_field(name="__**Bénéficiare**__",
                        value=f"{member.display_name} (+{str(amount)} 🪙)")

        await ctx.send(embed=embed)

    @commands.command(help="Demander de l'argent à quelqu'un.")
    async def askmoney(self, ctx, member: discord.Member = None, amount: int = 0):
        if member is None:
            await ctx.send("Vous n'avez pas défini qui doit vous envoyer de l'argent.. merci de retaper la commmande.")
            if amount == 0:
                await ctx.send("Vous n'avez pas spécifié le montant.. merci de retaper la commande.")
            return
        elif amount == 0:
            await ctx.send("Vous n'avez pas spécifié le montant.. merci de retaper la commande.")
            return
        await ctx.message.delete()
        author = ctx.message.guild.get_member(ctx.message.author.id)

        await member.send(f"{author.mention} vous demande de vous envoyer {str(amount)}$.")

    @commands.command(help="Affiche l'inventaire de quelqu'un.", aliases=["inv"])
    async def inventory(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.message.author
        await ctx.message.delete()

        data = database_handler.get_inventory(user_id=member.id)

        embed = discord.Embed(
            title=f"Inventaire de {member.display_name}", color=cogs.colors.ECONOMY_COLOR_EMBED)

        for i in data:
            if "Brevet" in i["item_name"]:
                pass
            else:
                embed.add_field(name=i["item_name"],
                                value=i["amount"], inline=False)

        await ctx.send(embed=embed)


class Company(commands.Cog):
    def __init__(self, fanbot):
        Company.fanbot = fanbot

    class selectMenuECREATE(discord.ui.Select):
        def __init__(select):
            options = [
                discord.SelectOption(label="Exploitations", value="1"),
                discord.SelectOption(
                    label="Productions industrielle", value="2"),
                discord.SelectOption(
                    label="Construction / Architecture", value="3"),
                discord.SelectOption(label="Transport", value="4"),
                discord.SelectOption(label="Recherche", value="5"),
                discord.SelectOption(label="Banque", value="6"),
                discord.SelectOption(label="Immobilier", value="7"),
                discord.SelectOption(label="Commerce", value="8"),
                discord.SelectOption(label="Informatique", value="9"),
                discord.SelectOption(label="Casino", value="10"),
                discord.SelectOption(label="Avocat", value="11"),
                discord.SelectOption(
                    label="Aucun des choix de la liste", value="0"),
            ]
            super().__init__(placeholder="Sélectionner son type d'entreprise...",
                             max_values=1,
                             min_values=1,
                             options=options)

        async def callback(select, interaction: discord.Interaction):
            def checkMessage(message):
                return message.author == interaction.user and interaction.channel == message.channel

            await interaction.channel.send("Quel nom voulez-vous donner à votre entreprise ?")

            try:
                channel_name = await Company.fanbot.wait_for("message", timeout=30, check=checkMessage)
            except:
                await interaction.channel.send("Temps dépassé!")
                return

            channel_name = channel_name.content.replace(" ", "-")

            if select.values[0] == "1":  # Exploitations
                category = get(interaction.guild.categories,
                               id=1012072126771101786)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Exploitations")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "2":  # Productions industrielle
                category = get(interaction.guild.categories,
                               id=976578014999642124)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Productions industrielles")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "3":  # Construction / Architecture
                category = get(interaction.guild.categories,
                               id=976578017046454313)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Construction / Architecture")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "4":  # Transport
                category = get(interaction.guild.categories,
                               id=1012072356040155177)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Transport")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "5":  # Recherche
                category = get(interaction.guild.categories,
                               id=1012345986988912721)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Recherche")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "6":  # Banque
                category = get(interaction.guild.categories,
                               id=976578014999642126)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Banque")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "7":  # Immobilier
                category = get(interaction.guild.categories,
                               id=976578014999642128)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Immobilier")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "8":  # Commerce
                category = get(interaction.guild.categories,
                               id=976578014999642130)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Commerce")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "9":  # Informatique
                category = get(interaction.guild.categories,
                               id=976578017046454316)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Informatique")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "10":  # Casino
                category = get(interaction.guild.categories,
                               id=1012346137597968384)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Casino")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            elif select.values[0] == "11":  # Avocat
                category = get(interaction.guild.categories,
                               id=1012346173333442642)
                await interaction.message.guild.create_text_channel(channel_name, category=category)
                database_handler.add_company_to_db(
                    company_name=channel_name, category="Avocat")
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=channel_name)
                database_handler.create_account_for_a_company(
                    company_id=company_id[0])
                withdraw = database_handler.withdraw(
                    user_id=interaction.user.id, amount=100)

            await interaction.guild.create_role(name=channel_name.title(), reason=f"Création de l'entreprise {channel_name.title()} ({interaction.message.author.display_name}).")
            owner = interaction.message.author
            role = discord.utils.get(
                interaction.guild.roles, name=channel_name.title())
            await owner.add_roles(role)

    class viewECREATE(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)
            self.add_item(Company.selectMenuECREATE())

    class buttonELIST_L(discord.ui.Button):
        def __init__(self):
            super().__init__(label="<-", style=discord.ButtonStyle.blurple,
                             disabled=True, custom_id="<-")

        async def callback(self, interaction: discord.Interaction):
            if self.view.page == 1:
                self.disabled = True
            self.view.page -= 1
            for child in self.view.children:
                if child.custom_id == "->":
                    child.disabled = False
            embed = discord.Embed(
                title=f"Entreprises de **{interaction.guild}**", color=cogs.colors.COMPANY_COLOR_EMBED)
            i = 0
            for company_name in self.view.companies_list[3*self.view.page:3*self.view.page+3]:
                if i < 3:
                    embed.add_field(
                        name=company_name["company_name"], value=company_name["category"], inline=False)
                    embed.set_footer(text="1")
                    i += 1
            embed.set_footer(text=self.view.page)
            await interaction.response.edit_message(embed=embed, view=self.view)

    class buttonELIST_R(discord.ui.Button):
        def __init__(self):
            super().__init__(label="->", style=discord.ButtonStyle.blurple,
                             disabled=False, custom_id="->")

        async def callback(self, interaction: discord.Interaction):
            if self.view.page == self.view.nb_of_pages-2:
                self.disabled = True
            self.view.page += 1
            for child in self.view.children:
                if child.custom_id == "<-":
                    child.disabled = False
            embed = discord.Embed(
                title=f"Entreprises de **{interaction.guild}**", color=cogs.colors.COMPANY_COLOR_EMBED)
            i = 0
            for company_name in self.view.companies_list[3*self.view.page:3*self.view.page+3]:
                if i < 3:
                    embed.add_field(
                        name=company_name["company_name"], value=company_name["category"], inline=False)
                    embed.set_footer(text="1")
                    i += 1
            embed.set_footer(text=self.view.page)
            await interaction.response.edit_message(embed=embed, view=self.view)

    class viewELIST(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)
            self.companies_list = database_handler.get_company_names_list()
            self.page = 1
            self.nb_of_pages = math.ceil(len(self.companies_list) / 3)
            self.add_item(Company.buttonELIST_L())
            self.add_item(Company.buttonELIST_R())

    @commands.command(help="Créer son entreprise.", aliases=["ccreate"])
    async def ecreate(self, ctx):
        await ctx.send(view=self.viewECREATE())

    @commands.command(help="Liste toutes les entreprises du pays.", pass_context=True, aliases=["clist"])
    async def elist(self, ctx):
        await ctx.message.delete()

        company_names = database_handler.get_company_names()

        embed = discord.Embed(
            title=f"Entreprises de **{ctx.guild}**", color=cogs.colors.COMPANY_COLOR_EMBED)
        i = 0
        for company_name in company_names:
            if i < 3:
                embed.add_field(
                    name=company_name["company_name"], value=company_name["category"], inline=False)
                embed.set_footer(text="1")
                i += 1

        await ctx.send(embed=embed, view=self.viewELIST())

    @commands.command(help="Connaitre l'argent d'une entreprise.", aliases=["cmoney"])
    async def emoney(self, ctx, company):
        await ctx.message.delete()
        if company is None:
            await ctx.send("Veuillez fournir le nom de l'entreprise.")
            return
        company = re.sub("\<|\#|\>", "", company)
        company = await ctx.guild.fetch_channel(company)
        company_id = database_handler.get_company_id_by_company_name(
            company_name=company.name)
        account = database_handler.get_company_account(
            company_id=company_id[0])
        embed = discord.Embed(
            title=f"Solde de {company.name.title()}", color=cogs.colors.COMPANY_COLOR_EMBED)
        embed.add_field(name="Argent (compte courant)",
                        value=f"{account[0]} 🪙")
        await ctx.send(embed=embed)

    @commands.command(help="Affiche l'inventaire d'une entreprise.", aliases=["einv", "cinv"])
    async def einventory(self, ctx, company=None):
        await ctx.message.delete()
        if company is None:
            await ctx.send("Veuillez fournir le nom de l'entreprise.")
            return
        company = re.sub("\<|\#|\>", "", company)
        company = await ctx.guild.fetch_channel(company)
        company_id = database_handler.get_company_id_by_company_name(
            company_name=company.name)
        data = database_handler.get_company_inventory(company_id=company_id[0])

        embed = discord.Embed(
            title=f"Inventaire de {company.name.title()}", color=cogs.colors.COMPANY_COLOR_EMBED)

        for i in data:
            embed.add_field(name=i["item_name"],
                            value=i["amount"], inline=False)

        await ctx.send(embed=embed)


class Production(commands.Cog):
    def __init__(self, fanbot):
        Company.fanbot = fanbot

    @commands.command(help="Affiche les brevets détenus par quelqu'un", aliases=["vrecipe"])
    async def viewrecipe(self, ctx, *item: str):
        await ctx.message.delete()

        item = " ".join(item)
        item = item.title()

        recipe = database_handler.get_recipe(recipe=item)

        embed = discord.Embed(
            title=f"Recette pour constituer faire du {item}", color=cogs.colors.PRODUCTION_COLOR_EMBED)
        
        for i in recipe:
            embed.add_field(name=i["item_name"],
                            value=i["amount"], inline=False)
        await ctx.send(embed=embed)
        
    @commands.command(help="Affiche la liste des recettes du serveur.", aliases=["rlist"])
    async def recipelist(self, ctx):
        await ctx.message.delete()

        recipes = database_handler.get_recipes()
        
        embed = discord.Embed(
            title=f"Recettes disponibles pour {ctx.message.author.display_name}", color=cogs.colors.PRODUCTION_COLOR_EMBED)
        recipes_already_used = ["20nov2022 15h40"]
        detector = False
        for recipe in recipes:
            for recipe_already_used in recipes_already_used:
                if recipe["recipe_name"] == recipe_already_used:
                    detector = True
            if detector == False:
                embed.add_field(
                    name=recipe["recipe_name"], value="** **", inline=False)
                recipes_already_used.append(recipe["recipe_name"])
        embed.set_footer(text="'!viewrecipe <nom de la recette>'   pour avoir accès au craft de la recette.")
        
        await ctx.send(embed=embed)

    
class Patent(commands.Cog):
    def __init__(self, fanbot):
        Company.fanbot = fanbot
        
    @commands.command(help="Faire une demande de brevet.", aliases=["brevet"])
    async def patent(self, ctx):
        await ctx.message.delete()
        
        detected = False
        for category in ctx.guild.categories:
            if category.name == "Tickets":
                detected = True

        if detected == False:
            await ctx.guild.create_category(name="Tickets")

        category = get(ctx.guild.categories, name="Tickets")
        
        channel_name = f"Demande de brevet ({ctx.message.author.display_name})"

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.message.author: discord.PermissionOverwrite(view_channel=True),
        }
        channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
        await channel.send(f"Bonjour {ctx.message.author.mention}, présente nous ton brevet ici !")

    @commands.command(help="Affiche les brevets détenus par quelqu'un.", aliases=["pinv", "brevetinventory","binv"])
    async def patentinventory(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.message.author
        await ctx.message.delete()

        data = database_handler.get_inventory(user_id=member.id)

        embed = discord.Embed(
            title=f"Brevets de {member.display_name}", color=cogs.colors.PATENT_COLOR_EMBED)

        items_name = []
        for i in data:
            if "Brevet" in i["item_name"]:
                item_name = i["item_name"]
                items_name.append(item_name.replace("Brevet:", "__Brevet:__"))
            else:
                pass
        i = 0
        for item_name in items_name:
            items_name[i] = item_name.lower()
            i += 1
        items_name.sort()
        for item_name in items_name:
            embed.add_field(name=item_name.title(),
                value="** **", inline=False)


        await ctx.send(embed=embed)