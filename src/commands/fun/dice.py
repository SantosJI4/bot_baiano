import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import asyncio

class DiceRollView(View):
    def __init__(self, bot, sides, message):
        super().__init__(timeout=30)  # Define um tempo limite para os botões
        self.bot = bot
        self.sides = sides
        self.message = message
        self.interacted = False  # Flag para verificar se houve interação

    @discord.ui.button(label="Rolar Novamente", style=discord.ButtonStyle.green)
    async def roll_again(self, interaction: discord.Interaction, button: Button):
        """Sorteia um novo número ao clicar no botão."""
        self.interacted = True  # Marca que houve interação
        result = random.randint(1, self.sides)
        embed = discord.Embed(
            title="🎲 Novo Resultado!",
            description=f"Você rolou um dado de **{self.sides} lados** e obteve: **{result}**!",
            color=discord.Color.green()
        )
        embed.set_footer(text="Boa sorte na próxima rolagem! 🎲")
        embed.set_image(url="https://media.tenor.com/ziuSyYfo4xEAAAAC/dice.gif")

        await interaction.response.edit_message(embed=embed, view=self)  # Atualiza a mensagem com o novo resultado

    async def on_timeout(self):
        """Apaga a mensagem se não houver interação dentro do tempo limite."""
        if not self.interacted:  # Verifica se não houve interação
            try:
                await self.message.delete()
                print("Mensagem apagada por falta de interação.")
            except discord.NotFound:
                print("A mensagem já foi apagada.")
            except discord.Forbidden:
                print("O bot não tem permissão para apagar mensagens neste canal.")
            except Exception as e:
                print(f"Erro ao tentar apagar a mensagem: {e}")


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dice")
    async def dice(self, ctx, sides: int = 6):
        """
        Rola um dado com o número de lados especificado (padrão: 6).
        Exibe o resultado com um botão para rolar novamente.
        """
        if sides < 1:
            await ctx.send("❌ O número de lados deve ser maior que 0.")
            return

        # Gera o resultado do dado
        result = random.randint(1, sides)

        # Embed estilizado com o resultado
        embed = discord.Embed(
            title="🎲 Rolando o dado...",
            description=f"Você rolou um dado de **{sides} lados** e obteve: **{result}**!",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Boa sorte na próxima rolagem! 🎲")
        embed.set_image(url="https://media.tenor.com/ziuSyYfo4xEAAAAC/dice.gif")

        # Envia a mensagem com o botão
        message = await ctx.send(embed=embed, view=DiceRollView(self.bot, sides, message=None))

        # Atualiza a mensagem no objeto DiceRollView
        view = DiceRollView(self.bot, sides, message)
        view.message = message

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(Dice(bot))