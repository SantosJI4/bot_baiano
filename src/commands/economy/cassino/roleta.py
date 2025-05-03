import discord
import random
from discord.ext import commands

class Roleta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roleta")
    async def roleta(self, ctx):
        """Jogo de Roleta."""
        await ctx.send("🎡 **Jogo de Roleta Iniciado!** Escolha sua aposta: número (0-36), cor (vermelho/preto) ou par/ímpar.")
        # Implementação do jogo de roleta...

async def setup(bot):
    await bot.add_cog(Roleta(bot))