import discord
from discord.ext import commands
import random

class Beijo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="beijo")
    async def beijo(self, ctx, membro: discord.Member):
        """Dá um beijo em outro membro com um GIF aleatório."""
        if membro == ctx.author:
            await ctx.send("❌ Você não pode dar um beijo em si mesmo!")
            return

        # Lista de GIFs de beijo
        gifs = [
            "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
            "https://media.giphy.com/media/3o6ZsYm5P38NvUWrDi/giphy.gif",
            "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
            "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
            "https://media.giphy.com/media/11k3oaUjSlFR4I/giphy.gif"
        ]

        gif = random.choice(gifs)

        # Cria o embed com o GIF
        embed = discord.Embed(
            title="💋 Beijo!",
            description=f"{ctx.author.mention} deu um beijo em {membro.mention}!",
            color=discord.Color.pink()
        )
        embed.set_image(url=gif)

        # Botão para retribuir o beijo
        view = BeijoView(ctx.author, membro)
        await ctx.send(embed=embed, view=view)


class BeijoView(discord.ui.View):
    def __init__(self, autor, alvo):
        super().__init__(timeout=60)  # O botão ficará ativo por 60 segundos
        self.autor = autor
        self.alvo = alvo

    @discord.ui.button(label="Retribuir", style=discord.ButtonStyle.blurple, emoji="🔄")
    async def retribuir(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retribui o beijo."""
        if interaction.user != self.alvo:
            await interaction.response.send_message("❌ Apenas quem recebeu o beijo pode retribuir!", ephemeral=True)
            return

        # Lista de GIFs de beijo
        gifs = [
            "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
            "https://media.giphy.com/media/3o6ZsYm5P38NvUWrDi/giphy.gif",
            "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
            "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
            "https://media.giphy.com/media/11k3oaUjSlFR4I/giphy.gif"
        ]

        gif = random.choice(gifs)

        # Cria o embed com o GIF
        embed = discord.Embed(
            title="💋 Retribuição!",
            description=f"{self.alvo.mention} retribuiu o beijo em {self.autor.mention}!",
            color=discord.Color.pink()
        )
        embed.set_image(url=gif)

        await interaction.response.send_message(embed=embed)
        self.stop()  # Desativa os botões após a interação


async def setup(bot):
    await bot.add_cog(Beijo(bot))