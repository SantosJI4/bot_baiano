import discord
from discord.ext import commands
import asyncio  # Import necessário para adicionar delays entre os envios

class Div(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="enviar_dm_todos")
    @commands.has_permissions(administrator=True)  # Apenas administradores podem usar este comando
    async def enviar_dm_todos(self, ctx, *, mensagem: str):
        """
        Envia uma mensagem personalizada na DM de todos os membros do servidor.
        Uso: !enviar_dm_todos Sua mensagem aqui
        """
        enviados = 0
        erros = 0

        await ctx.send("📢 Iniciando o envio de mensagens para todos os membros...")

        for member in ctx.guild.members:
            if not member.bot:  # Ignora bots
                try:
                    await member.send(mensagem)
                    enviados += 1
                except discord.Forbidden:
                    erros += 1  # Não foi possível enviar a mensagem (DM fechada)
                except Exception as e:
                    erros += 1
                    print(f"Erro ao enviar mensagem para {member.name}: {e}")
                await asyncio.sleep(1)  # Aguarda 1 segundo entre os envios para evitar rate limits

        await ctx.send(f"✅ Mensagens enviadas com sucesso para {enviados} membros. ❌ Erros: {erros}.")

# Adicione o cog ao bot
async def setup(bot):
    await bot.add_cog(Div(bot))