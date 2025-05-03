import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    async def say(self, ctx, *, text: str):
        """Repete a mensagem enviada pelo usuário."""
        await ctx.send(text)

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(Fun(bot))