import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)


active_timeouts = {}  # Dictionnaire pour suivre les timeouts

@client.hybrid_command(name="mute", description="Mute un utilisateur sur le serveur pour une durée spécifiée.")
async def mute(ctx: commands.Context, user: discord.Member, duration: int, *, reason: str = "Non spécifiée"):
    if not ctx.author.guild_permissions.moderate_members:
        no_perm_embed = discord.Embed(title="Permission Refusée", description="Vous n'avez pas la permission de mute des membres.", color=0x000000)
        no_perm_embed.set_footer(text=f"Action effectuée par {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=no_perm_embed, ephemeral=True)
        return

    timeout_end = discord.utils.utcnow() + timedelta(minutes=duration)
    await user.edit(timed_out_until=timeout_end, reason=reason)
    active_timeouts[user.id] = ctx.guild.id

    server_embed = discord.Embed(title="Utilisateur Mute", description=f"{user.display_name} a été mis en sourdine sur {ctx.guild.name}.", color=0x000000)
    server_embed.add_field(name="Raison :", value=reason or "Aucune raison spécifiée")
    server_embed.add_field(name="Auteur du mute :", value=f"||{ctx.author.mention}||", inline=True)
    server_embed.add_field(name="Temps :", value=f"{duration} minutes")
    server_embed.set_footer(text=f"Action effectuée par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=server_embed)

    dm_embed = discord.Embed(title="Vous avez été mis en sourdine", description=f"Vous avez été mis(e) en sourdine sur le serveur {ctx.guild.name}.", color=0x000000)
    dm_embed.add_field(name="Raison :", value=reason or "Aucune raison spécifiée")
    dm_embed.add_field(name="Temps :", value=f"{duration} minutes")
    dm_embed.add_field(name="Auteur du mute :", value=f"||{ctx.author.mention}||", inline=True)
    dm_embed.set_thumbnail(url=ctx.guild.icon.url)
    await user.send(embed=dm_embed)

    await asyncio.sleep(duration * 60)
    if user.id in active_timeouts and active_timeouts[user.id] == ctx.guild.id:
        await user.edit(timed_out_until=None)
        demute_embed = discord.Embed(title="Fin de la Mise en Sourdine", description=f"Vous avez été démuté(e) sur le serveur {ctx.guild.name}.", color=0x000000)
        demute_embed.set_thumbnail(url=ctx.guild.icon.url)
        await user.send(embed=demute_embed)
        del active_timeouts[user.id]
