import discord
import datetime
import re
import cogs.colors
import time
from discord.ext import commands, tasks
from discord.utils import get
from discord.errors import Forbidden
from cogs.Data.database_handler import DatabaseHandler


database_handler = DatabaseHandler('database.db')
now = datetime.datetime.now()


async def setup(bot):
    await bot.add_cog(FixDatabase(bot), guilds=[discord.Object(id=976578012592111646)])
    await bot.add_cog(Status(bot), guilds=[discord.Object(id=976578012592111646)])
    await bot.add_cog(Admineconomy(bot), guilds=[discord.Object(id=976578012592111646)])


class FixDatabase(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_db.start()

    def get_absent_members_from_db(self, guild):
        return set(member.id for member in guild.members).difference([row["user_id"] for row in database_handler.get_members_list()]).difference({self.fanbot.user.id})

    def get_members_has_not_account(self, guild):
        return set(member.id for member in guild.members).difference([row["user_id"] for row in database_handler.get_account_list()]).difference({self.fanbot.user.id})

    @tasks.loop(hours=24)
    async def update_db(self):
        async for guild in self.fanbot.fetch_guilds(limit=50):
            list_ids = self.get_absent_members_from_db(guild)
            if len(list_ids) > 0:
                database_handler.add_members_to_db(user_ids=list_ids)
            list_ids = self.get_members_has_not_account(guild)
            try:
                database_handler.create_accounts(user_ids=list_ids)
            except:
                channel = self.fanbot.get_channel(976578013502242820)
                await self.channel.send(f"{now.strftime('%H:%M %d/%m/%Y ')} - [Error on update_db]")


class Status(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ping(self, ctx):
        await ctx.message.delete()
        channel = self.fanbot.get_channel(976578013502242820)
        await channel.send(f"Voici la latence du bot: {round(self.fanbot.latency, 1)}ms")


class Admineconomy(commands.Cog):
    def __init__(self, fanbot):
        self.fanbot = fanbot

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_patent.start()

    @commands.command(aliases=["admininv", "ainv"])
    @commands.has_permissions(administrator=True)
    async def admininventory(self, ctx):
        await ctx.message.delete()

        embed = discord.Embed(
            title="Que souhaitez-vous faire ?", color=cogs.colors.ADMIN_COLOR_EMBED)
        embed.add_field(
            name="\u200b", value="`give` ⇒ Ajouter un objet x fois à l'inventaire d'un membre.", inline=False)
        embed.add_field(
            name="\u200b", value="`remove` ⇒ Retirer un objet x fois à l'inventaire d'un membre.", inline=False)
        embed.set_footer(
            text="Faites 'cancel' pour annuler la commande.")
        await ctx.send(embed=embed)

        def checkMessage(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        try:
            choice = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
        except:
            await ctx.send("Temps dépassé!")
            return

        if "give" == choice.content.lower():
            embed = discord.Embed(
                title="De quel membre souhaitez-vous modifier l'inventaire ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                user = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            user = user.content
            # '<@id>'  to  'id'
            user = re.sub("\<|\@|\>", "", user)

            embed = discord.Embed(
                title="Quel objet souahitez-vous donner ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                item_name = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            embed = discord.Embed(
                title="Combien voulez-vous en donner ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                amount = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            try:
                database_handler.add_item_to_items_list(
                    item_name=str(item_name.content))
            except:
                pass
            finally:
                item_id = database_handler.get_item_id_by_item_name(
                    item_name=str(item_name.content))

                current_inventory = database_handler.get_inventory(
                    user_id=user)
                detector = False
                for item in current_inventory:
                    if item["item_name"] == item_name.content:
                        detector = True
                if detector == False:
                    # si l'item à ajouter n'est déjà pas présent dans l'inv du joueur
                    # on crée la ligne avec l'item et le montant donné
                    database_handler.add_item_to_inv(user_id=int(
                        user), item_id=int(item_id[0]), amount=int(amount.content))
                else:
                    # si item_id est dans l'inv du joueur
                    # on ajoute le montant au montant déjà dans l'inventaire
                    database_handler.add_amount_item_to_inv(user_id=int(
                        user), item_id=int(item_id[0]), amount=int(amount.content))

        elif "remove" == choice.content.lower():
            embed = discord.Embed(
                title="De quel membre souhaitez-vous modifier l'inventaire ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                user = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            user = user.content
            # '<@id>'  to  'id'
            user = re.sub("\<|\@|\>", "", user)

            embed = discord.Embed(
                title="Quel objet souahitez-vous retirer ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                item_name = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return
            item_name = item_name.content
            current_inventory = database_handler.get_inventory(user_id=user)
            detector = False
            for item in current_inventory:
                if item["item_name"] == item_name:
                    detector = True
            if detector == False:
                await ctx.send(
                    f"Il n'y a pas {item_name} dans l'inventaire demandé !")
                return

            embed = discord.Embed(
                title="Combien voulez-vous en retirer ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                amount = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return
            amount = int(amount.content)
            detector = False
            if amount < 0:
                await ctx.send("Le montant n'est pas valide.")
                return
            for item in current_inventory:
                if item["item_name"] == item_name:
                    if amount <= item["amount"]:
                        detector = True
            if detector == False:
                member = ctx.guild.get_member(user)
                await ctx.send(
                    f"Il y a moins de {amount} {item_name} dans l'inventaire demandé !")
                return

            item_id = database_handler.get_item_id_by_item_name(
                item_name=str(item_name))
            for item in current_inventory:
                if item["item_name"] == item_name:
                    if item["amount"] == amount:
                        database_handler.delete_item_to_inv(
                            user_id=int(user), item_id=int(item_id[0]))
                    if amount < item["amount"]:
                        database_handler.remove_item_to_inv(user_id=int(
                            user), item_id=int(item_id[0]), amount=amount)

        elif "cancel" == choice.content.lower():
            return
        else:
            await ctx.send("L'action choisie n'est pas valide !")
            return

    @commands.command(aliases=["admineinv", "admincinv", "aeinv"])
    @commands.has_permissions(administrator=True)
    async def admineinventory(self, ctx):
        await ctx.message.delete()

        embed = discord.Embed(
            title="Que souhaitez-vous faire ?", color=cogs.colors.ADMIN_COLOR_EMBED)
        embed.add_field(
            name="\u200b", value="`give` ⇒ Ajouter un objet x fois à l'inventaire d'une entreprise.", inline=False)
        embed.add_field(
            name="\u200b", value="`remove` ⇒ Retirer un objet x fois à l'inventaire d'une entreprise.", inline=False)
        embed.set_footer(
            text="Faites 'cancel' pour annuler la commande.")
        await ctx.send(embed=embed)

        def checkMessage(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        try:
            choice = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
        except:
            await ctx.send("Temps dépassé!")
            return

        if "give" == choice.content.lower():
            embed = discord.Embed(
                title="De quelle entreprise souhaitez-vous modifier l'inventaire ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                company = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            company = company.content
            # '<#id>'  to  'id'
            company = re.sub("\<|\#|\>", "", company)

            company = await ctx.guild.fetch_channel(company)
            embed = discord.Embed(
                title="Quel objet souahitez-vous donner ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                item_name = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            embed = discord.Embed(
                title="Combien voulez-vous en donner ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                amount = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            try:
                database_handler.add_item_to_items_list(
                    item_name=str(item_name.content))
            except:
                pass
            finally:
                item_id = database_handler.get_item_id_by_item_name(
                    item_name=str(item_name.content))
                company_id = database_handler.get_company_id_by_company_name(
                    company_name=company.name)

                current_inventory = database_handler.get_company_inventory(
                    company_id=company_id[0])
                detector = False
                for item in current_inventory:
                    if item["item_name"] == item_name.content:
                        detector = True
                if detector == False:
                    # si l'item à ajouter n'est déjà pas présent dans l'inv dé l'entreprise
                    # on crée la ligne avec l'item et le montant donné
                    database_handler.add_item_to_company_inv(company_id=int(
                        company_id[0]), item_id=int(item_id[0]), amount=int(amount.content))
                else:
                    # si item_id est dans l'inv de l'entreprise
                    # on ajoute le montant au montant déjà dans l'inventaire
                    database_handler.add_amount_item_to_company_inv(company_id=int(
                        company_id[0]), item_id=int(item_id[0]), amount=int(amount.content))

        elif "remove" == choice.content.lower():
            embed = discord.Embed(
                title="De quelle entreprise souhaitez-vous modifier l'inventaire ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                company = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            company = company.content
            # '<#id>'  to  'id'
            company = re.sub("\<|\#|\>", "", company)

            company = await ctx.guild.fetch_channel(company)
            embed = discord.Embed(
                title="Quel objet souahitez-vous retirer ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                item_name = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return
            item_name = item_name.content
            company_id = database_handler.get_company_id_by_company_name(
                company_name=company.name)
            current_inventory = database_handler.get_company_inventory(
                company_id=company_id[0])
            detector = False
            for item in current_inventory:
                if item["item_name"] == item_name:
                    detector = True
            if detector == False:
                await ctx.send(
                    f"Il n'y a pas {item_name} dans l'inventaire demandé !")
                return

            embed = discord.Embed(
                title="Combien voulez-vous en retirer ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                amount = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return
            amount = int(amount.content)
            detector = False
            if amount < 0:
                await ctx.send("Le montant n'est pas valide.")
                return
            for item in current_inventory:
                if item["item_name"] == item_name:
                    if amount <= item["amount"]:
                        detector = True
            if detector == False:
                await ctx.send(
                    f"Il y a moins de {amount} {item_name} dans l'inventaire demandé !")
                return

            item_id = database_handler.get_item_id_by_item_name(
                item_name=str(item_name))
            for item in current_inventory:
                if item["item_name"] == item_name:
                    if item["amount"] == amount:
                        database_handler.delete_item_to_company_inv(
                            company_id=int(company_id[0]), item_id=int(item_id[0]))
                    if amount < item["amount"]:
                        database_handler.remove_item_to_company_inv(company_id=int(
                            company_id[0]), item_id=int(item_id[0]), amount=amount)
        elif "cancel" == choice.content.lower():
            return
        else:
            await ctx.send("L'action choisie n'est pas valide !")
            return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def recipe(self, ctx):
        await ctx.message.delete()

        embed = discord.Embed(
            title="Que souhaitez-vous faire ?", color=cogs.colors.ADMIN_COLOR_EMBED)
        embed.add_field(
            name="\u200b", value="`create` ⇒ Créer une recette", inline=False)
        embed.add_field(
            name="\u200b", value="`delete` ⇒ Supprimer une recette", inline=False)
        embed.set_footer(
            text="Faites 'cancel' pour annuler la commande.")
        await ctx.send(embed=embed)

        def checkMessage(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        try:
            choice = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
        except:
            await ctx.send("Temps dépassé!")
            return

        if "create" == choice.content.lower():
            embed = discord.Embed(
                title="Quel nom souahitez-vous donner à la future recette ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                recipe_name = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            embed = discord.Embed(
                title="Combien d'objets différents est nécessaire pour créer cette recette ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                nbr_of_items = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            if int(nbr_of_items.content) <= 0:
                await ctx.send("Le nombre d'items est inférieur à 1. Craft impossible !")
                return

            i = 0
            items_list = []
            amounts_list = []
            while i < int(nbr_of_items.content):
                embed = discord.Embed(
                    title=f"Donner un item n°{i + 1} pour le craft de {recipe_name.content}.", color=cogs.colors.ADMIN_COLOR_EMBED)
                await ctx.send(embed=embed)

                try:
                    item = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
                except:
                    await ctx.send("Temps dépassé!")
                    return
                items_list.append(item.content)

                embed = discord.Embed(
                    title=f"Donner un motant pour l'item n°{i + 1} pour le craft de {recipe_name.content}.", color=cogs.colors.ADMIN_COLOR_EMBED)
                await ctx.send(embed=embed)

                try:
                    amount = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
                except:
                    await ctx.send("Temps dépassé!")
                    return
                amounts_list.append(int(amount.content))

                i += 1

            try:
                database_handler.add_item_to_items_list(
                    item_name=str(recipe_name.content))
            except:
                pass
            finally:
                item_id = database_handler.get_item_id_by_item_name(
                    item_name=str(recipe_name.content))

            items_ids_list = []
            for item in items_list:
                try:
                    database_handler.add_item_to_items_list(
                        item_name=str(item))
                except:
                    pass
                finally:
                    item_id = database_handler.get_item_id_by_item_name(
                        item_name=str(item))
                    items_ids_list.append(item_id[0])

            recipe_name = recipe_name.content
            database_handler.create_recipe(
                recipe_name=recipe_name.title(), items_id=items_ids_list, amounts=amounts_list)

        if "delete" == choice.content.lower():
            embed = discord.Embed(
                title="Quelle recette souhaitez-vous supprimer ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                recipe_name = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            recipe_name = recipe_name.content

            recipes = database_handler.get_recipes()

            detector = False
            for recipe in recipes:
                if recipe["recipe_name"].lower() == recipe_name.lower():
                    database_handler.delete_recipe(
                        recipe_name=recipe_name.title())
                    return

            await ctx.send("La recette que vous souhaitez supprimer n'existe pas.")

    @commands.command(aliases=["setbrevettime", "spt", "sbt"])
    @commands.has_permissions(administrator=True)
    async def setpatenttime(self, ctx, number_of_days: int = None):
        await ctx.message.delete()

        def checkMessage(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        if number_of_days is None:
            embed = discord.Embed(
                title="Combien de temps un brevet est-il privé ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                number_of_days = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            number_of_days = int(number_of_days.content)

        database_handler.edit_brevet_time(number_of_days)

        days = database_handler.get_brevet_time()

        embed = discord.Embed(
            title="Temps du brevet", color=cogs.colors.ADMIN_COLOR_EMBED)
        embed.add_field(
            name="En semaines", value=f"{round(days[0] / 7, 1)}", inline=False)
        embed.add_field(
            name="En jours", value=f"{days[0]}", inline=False)
        channel = self.fanbot.get_channel(976578013502242820)
        await channel.send(embed=embed)

    @commands.command(aliases=["pcreate","brevetcreate", "bcreate"])
    @commands.has_permissions(administrator=True)
    async def patentcreate(self, ctx, user: discord.User = None, *, patent_name: str = None):
        await ctx.message.delete()

        def checkMessage(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        if user is None:
            embed = discord.Embed(
                title="Qui est le propriétaire de ce brevet ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                user = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            user = user.content
            # '<@id>'  to  'id'
            user = re.sub("\<|\@|\>", "", user)
        else:
            user = user.id

        if patent_name is None:
            embed = discord.Embed(
                title="Quel est le nom du Brevet ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                patent_name = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            patent_name = f"Brevet: {patent_name.content}"
            patent_name = patent_name.title()
        else:
            patent_name = "".join(patent_name)
            patent_name = f"Brevet: {patent_name}"
            patent_name = patent_name.title()

        try:
            database_handler.add_item_to_items_list(
                item_name=str(patent_name))
        except:
            pass
        finally:
            item_id = database_handler.get_item_id_by_item_name(
                item_name=str(patent_name))

            current_inventory = database_handler.get_inventory(
                user_id=user)

            detector = False
            for item in current_inventory:
                if item["item_name"] == patent_name:
                    detector = True
            if detector == False:
                # si l'item à ajouter n'est déjà pas présent dans l'inv du joueur
                # on crée la ligne avec l'item et le montant donné
                database_handler.add_item_to_inv(user_id=int(
                    user), item_id=int(item_id[0]), amount=1)
            else:
                # si item_id est dans l'inv du joueur
                # on ajoute le montant au montant déjà dans l'inventaire
                database_handler.add_amount_item_to_inv(user_id=int(
                    user), item_id=int(item_id[0]), amount=1)
                
            timestamp = database_handler.get_brevet_time()
            current_timestamp = time.time()
            timestamp = current_timestamp + timestamp[0] * 86400
            database_handler.create_patent(patent_id=int(item_id[0]), patent_name=str(patent_name), timestamp=timestamp)

    @commands.command(aliases=["pexpire", "brevetexpire", "bexpire", "expire"])
    @commands.has_permissions(administrator=True)
    async def patentexpire(self, ctx, *, patent_name: str = None):
        await ctx.message.delete()

        def checkMessage(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        if patent_name is not None:
            if patent_name.startswith("Brevet:"):
                patent_name = patent_name.title()
            else:
                patent_name = "".join(patent_name)
                patent_name = f"Brevet: {patent_name}"
                patent_name = patent_name.title()

        if patent_name is None:
            embed = discord.Embed(
                title="Quel est le nom du Brevet ?", color=cogs.colors.ADMIN_COLOR_EMBED)
            await ctx.send(embed=embed)

            try:
                patent_name = await self.fanbot.wait_for("message", timeout=15, check=checkMessage)
            except:
                await ctx.send("Temps dépassé!")
                return

            if patent_name.content.startswith("Brevet:"):
                patent_name = patent_name.title()
            else:
                patent_name = f"Brevet: {patent_name.content}"
                patent_name = patent_name.title()
        
        patent_id = database_handler.get_item_id_by_item_name(item_name=patent_name)
        
        database_handler.edit_patent_status(patent_id=patent_id[0], status="public")
        database_handler.remove_patent_to_inventory(patent_id=patent_id[0])
        

    @tasks.loop(seconds=10)
    async def update_patent(self):
        async for guild in self.fanbot.fetch_guilds(limit=50):
            patents = database_handler.get_patents()
            current_timestamp = time.time()
            days = database_handler.get_brevet_time()
            time_to_add = days[0] * 86400
            
            for patent in patents:
                if patent["status"].lower() == "private":        
                    if current_timestamp > patent["activate_time"]:
                        database_handler.edit_patent_status(patent_id=patent["patent_id"], status="public")
                        database_handler.remove_patent_to_inventory(patent_id=patent["patent_id"])
                        print(f"brevet public: {patent['patent_name'].title()}")