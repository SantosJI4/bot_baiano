import discord
from discord.ext import commands

# filepath: c:\Users\Maurício Santana\Documents\nocookie2.0 - Copia\discord-bot-project\src\commands\moderation\div.py

class Div(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="enviar_dm")
    async def enviar_dm(self, ctx, member: discord.Member, *, mensagem: str):
        """
        Envia uma mensagem personalizada na DM de um membro mencionado.
        Uso: !enviar_dm @usuario Sua mensagem aqui
        """
        try:
            await member.send(mensagem)
            await ctx.send(f"✅ Mensagem enviada para {member.mention} com sucesso!")
        except discord.Forbidden:
            await ctx.send(f"❌ Não foi possível enviar a mensagem para {member.mention}. O usuário pode ter as DMs fechadas.")
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao tentar enviar a mensagem: {e}")

# Adicione o cog ao bot
async def setup(bot):
    await bot.add_cog(Div(bot))