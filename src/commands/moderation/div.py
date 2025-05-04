import discord
from discord.ext import commands

class EventAnnouncement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="divulgar")
    @commands.has_permissions(administrator=True)
    async def divulgar_evento(self, ctx, *, mensagem):
        """Envia uma mensagem de divulgação para as DMs de todos os membros do servidor."""
        await ctx.send("📢 Iniciando a divulgação do evento...")

        # Lista de membros que receberam a mensagem
        enviados = 0
        erros = 0

        for member in ctx.guild.members:
            if not member.bot:  # Ignora bots
                try:
                    await member.send(f"📢 **Divulgação de Evento:**\n\n{mensagem}")
                    enviados += 1
                except discord.Forbidden:
                    erros += 1  # Não foi possível enviar a mensagem (DM fechada)

        await ctx.send(f"✅ Mensagem enviada para {enviados} membros.\n❌ Não foi possível enviar para {erros} membros (DMs fechadas ou sem permissão).")

    @divulgar_evento.error
    async def divulgar_evento_error(self, ctx, error):
        """Trata erros no comando de divulgação."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Por favor, forneça a mensagem de divulgação. Exemplo: `!divulgar <mensagem>`.")
        else:
            await ctx.send(f"❌ Ocorreu um erro: {error}")

async def setup(bot):
    await bot.add_cog(EventAnnouncement(bot))