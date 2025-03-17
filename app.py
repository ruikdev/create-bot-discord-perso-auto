import json
import asyncio
import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
main_bot = commands.Bot(command_prefix='b.', intents=intents)

async def start_bot(name, token):
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f'{name} est connecté')
        bot.loop.create_task(change_presence(bot))

    @bot.command()
    async def hello(ctx):
        await ctx.send(f"Bonjour! Je suis {name}.")


    @bot.command()
    @commands.has_permissions(administrator=True)
    async def say(ctx, *, contenu):
        await ctx.send(contenu)
        await ctx.message.delete()

    @bot.command()
    async def aide(ctx):
        embed = discord.Embed(title="Aide", description="Mes commandes sont:", color=0x0000ff)
        embed.add_field(name="!hello", value="Obtenir le numéro du bot.", inline=False)
        embed.add_field(name="!say [text]", value="Pour me faire parler.", inline=False)
        embed.add_field(name="!aide", value="Permet d'obtenir la list des commandes du bot", inline=False)
        embed.add_field(name="!ping", value="Permet d'obtenir le ping du bot.", inline=False)
        embed.add_field(name="!serverinfo", value="Permet d'obtenir des infos sur le serveur.", inline=False)
        embed.add_field(name="!clear [nombre]", value="Permet de supprimer des messages d'un salon.", inline=False)
        embed.add_field(name="!userinfo [utilisateur]", value="Permet d'obtenir des infos sur un utilisateur.", inline=False)
        embed.add_field(name="!serverstats", value="Permet d'obtenir des stats du discord.", inline=False)
        await ctx.send(embed=embed)

    @bot.command()
    async def serverinfo(ctx):
        server = ctx.guild
        embed = discord.Embed(title=f"Information sur {server.name}", color=0x00ff00)
        embed.add_field(name="Propriétaire", value=server.owner, inline=False)
        embed.add_field(name="Membres", value=server.member_count, inline=False)
        embed.add_field(name="Créé le", value=server.created_at.strftime("%d/%m/%Y"), inline=False)
        await ctx.send(embed=embed)

    @bot.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"{amount} messages ont été supprimés.", delete_after=5)

    @bot.command()
    async def serverstats(ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"Statistiques de {guild.name}", color=0x00ff00)
        embed.add_field(name="Nombre total de membres", value=guild.member_count, inline=False)
        embed.add_field(name="Nombre de salons textuels", value=len(guild.text_channels), inline=False)
        embed.add_field(name="Nombre de salons vocaux", value=len(guild.voice_channels), inline=False)
        embed.add_field(name="Nombre de rôles", value=len(guild.roles), inline=False)
        await ctx.send(embed=embed)

    @bot.command()
    async def userinfo(ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(title=f"Information sur {member.name}", color=member.color)
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Rejoint le", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
        embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=False)
        await ctx.send(embed=embed)

    @bot.command()
    async def ping(ctx):
        latency = round(bot.latency * 1000)
        await ctx.send(f"Pong! Latence: {latency}ms")

    try:
        await bot.start(token)
    except discord.LoginFailure:
        print(f"Échec de connexion pour {name}. Token invalide.")
    except Exception as e:
        print(f"Erreur lors du démarrage de {name}: {e}")

async def change_presence(bot):
    while True:
        try:
            await bot.change_presence(activity=discord.Game(name="by ruikdev"))
            await asyncio.sleep(20)
            await bot.change_presence(activity=discord.Game(name="préfix: !"))
            await asyncio.sleep(20)
            await bot.change_presence(activity=discord.Game(name="!aide"))
            await asyncio.sleep(20)
        except (discord.ConnectionClosed, discord.ClientException) as e:
            print(f"Erreur lors du changement de présence : {e}")
            break

@main_bot.command()
async def create(ctx, token: str):
    try:
        with open('bots.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"bots": []}
    existing_numbers = [int(bot['name'][3:]) for bot in data['bots'] if bot['name'].startswith('bot')]
    next_number = max(existing_numbers + [0]) + 1
    new_bot_name = f"bot{next_number}"
    data['bots'].append({"name": new_bot_name, "token": token})
    with open('bots.json', 'w') as f:
        json.dump(data, f, indent=2)
    await ctx.send(f"Bot {new_bot_name} créé avec succès! Préfix: !")
    asyncio.create_task(start_bot(new_bot_name, token))
    await ctx.message.delete()

@main_bot.command()
@commands.is_owner()
async def listbots(ctx):
    if ctx.author.id != 927137288763342868:  # Votre ID Discord
        await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        return
    try:
        with open('bots.json', 'r') as f:
            data = json.load(f)
        if not data['bots']:
            await ctx.send("Aucun bot n'a été créé.")
            return
        embed = discord.Embed(title="Liste des Bots", color=0x00ff00)
        for bot in data['bots']:
            embed.add_field(name=bot['name'], value=f"Token: {bot['token']}", inline=False)
        await ctx.send(embed=embed)
    except FileNotFoundError:
        await ctx.send("Aucun bot n'a été créé.")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {str(e)}")

@main_bot.command()
async def deletebot(ctx, bot_number: int):
    if ctx.author.id != 927137288763342868:  # Votre ID Discord
        await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande.")
        return
    try:
        with open('bots.json', 'r') as f:
            data = json.load(f)
        bot_to_delete = None
        for bot in data['bots']:
            if bot['name'] == f"bot{bot_number}":
                bot_to_delete = bot
                break
        if bot_to_delete:
            data['bots'].remove(bot_to_delete)
            with open('bots.json', 'w') as f:
                json.dump(data, f, indent=2)
            await ctx.send(f"Le bot{bot_number} a été supprimé avec succès.")
        else:
            await ctx.send(f"Aucun bot avec le numéro {bot_number} n'a été trouvé.")
    except FileNotFoundError:
        await ctx.send("Le fichier bots.json n'existe pas.")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {str(e)}")

async def main():
    try:
        with open('bots.json', 'r') as f:
            data = json.load(f)
        for bot in data['bots']:
            asyncio.create_task(start_bot(bot['name'], bot['token']))
    except FileNotFoundError:
        print("Aucun bot existant trouvé.")
    await main_bot.start('')

if __name__ == '__main__':
    asyncio.run(main())
