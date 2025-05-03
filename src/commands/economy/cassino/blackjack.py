import discord
from discord.ext import commands

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="blackjack")
    async def blackjack(self, ctx):
        """Jogo de Blackjack (21)."""
        await ctx.send("🃏 **Jogo de Blackjack Iniciado!** Tente chegar o mais próximo de 21 sem ultrapassar.")
        # Implementação do jogo de blackjack...

async def setup(bot):
    await bot.add_cog(Blackjack(bot))