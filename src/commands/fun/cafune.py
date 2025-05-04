import discord
from discord.ext import commands
import random

class Cafune(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cafune")
    async def cafune(self, ctx, membro: discord.Member):
        """Faz um cafuné em outro membro com um GIF aleatório."""
        if membro == ctx.author:
            await ctx.send("❌ Você não pode fazer cafuné em si mesmo!")
            return

        # Lista de GIFs de cafuné
        gifs = [
            "https://media.giphy.com/media/4HP0ddZnNVvKU/giphy.gif",
            "https://media.giphy.com/media/109ltuoSQT212w/giphy.gif",
            "https://media.giphy.com/media/xUNd9HZq1itMkiK652/giphy.gif",
            "https://media.giphy.com/media/ye7OTQgwmVuVy/giphy.gif",
            "https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif"
        ]

        gif = random.choice(gifs)

        # Cria o embed com o GIF
        embed = discord.Embed(
            title="✨ Cafuné!",
            description=f"{ctx.author.mention} fez um cafuné em {membro.mention}!",
            color=discord.Color.blue()
        )
        embed.set_image(url=gif)

        # Botão para retribuir o cafuné
        view = CafuneView(ctx.author, membro)
        await ctx.send(embed=embed, view=view)


class CafuneView(discord.ui.View):
    def __init__(self, autor, alvo):
        super().__init__(timeout=60)  # O botão ficará ativo por 60 segundos
        self.autor = autor
        self.alvo = alvo

    @discord.ui.button(label="Retribuir", style=discord.ButtonStyle.blurple, emoji="🔄")
    async def retribuir(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retribui o cafuné."""
        if interaction.user != self.alvo:
            await interaction.response.send_message("❌ Apenas quem recebeu o cafuné pode retribuir!", ephemeral=True)
            return

        # Lista de GIFs de cafuné
        gifs = [
            "https://media.giphy.com/media/4HP0ddZnNVvKU/giphy.gif",
            "https://media.giphy.com/media/109ltuoSQT212w/giphy.gif",
            "https://media.giphy.com/media/xUNd9HZq1itMkiK652/giphy.gif",
            "https://media.giphy.com/media/ye7OTQgwmVuVy/giphy.gif",
            "https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif"
        ]

        gif = random.choice(gifs)

        # Cria o embed com o GIF
        embed = discord.Embed(
            title="✨ Retribuição!",
            description=f"{self.alvo.mention} retribuiu o cafuné em {self.autor.mention}!",
            color=discord.Color.blue()
        )
        embed.set_image(url=gif)

        await interaction.response.send_message(embed=embed)
        self.stop()  # Desativa os botões após a interação


async def setup(bot):
    await bot.add_cog(Cafune(bot))