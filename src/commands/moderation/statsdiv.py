import discord
from discord.ext import commands

class InviteManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="divulgacao")
    @commands.has_permissions(administrator=True)
    async def divulgacao(self, ctx, membro: discord.Member = None):
        """
        Mostra as estatísticas de divulgação do bot e os links de convite.
        Se um membro for especificado, mostra quantas pessoas entraram pelo link dele.
        """
        if membro:
            # Mostra as estatísticas de um membro específico
            invites = await ctx.guild.invites()
            total_entradas = 0
            for invite in invites:
                if invite.inviter == membro:
                    total_entradas += invite.uses
            await ctx.send(f"📊 **Estatísticas de {membro.mention}:**\n👥 Pessoas que entraram pelo link: {total_entradas}")
        else:
            # Mostra as estatísticas gerais e os links criados pelo bot
            invites = await ctx.guild.invites()
            bot_invites = [invite for invite in invites if invite.inviter == ctx.guild.me]
            total_entradas = sum(invite.uses for invite in bot_invites)

            if bot_invites:
                links = "\n".join([f"🔗 {invite.url} - Usos: {invite.uses}" for invite in bot_invites])
                await ctx.send(f"📊 **Estatísticas de Divulgação do Bot:**\n👥 Total de pessoas que entraram pelos links do bot: {total_entradas}\n\n**Links Criados pelo Bot:**\n{links}")
            else:
                await ctx.send("❌ O bot não criou nenhum link de convite.")

    @commands.command(name="criarlink")
    @commands.has_permissions(administrator=True)
    async def criar_link(self, ctx, max_usos: int = 0, expira_em: int = 0):
        """
        Cria um link de convite personalizado.
        - max_usos: Número máximo de usos (0 para ilimitado).
        - expira_em: Tempo em segundos para o link expirar (0 para nunca expirar).
        """
        try:
            invite = await ctx.channel.create_invite(max_uses=max_usos, max_age=expira_em, unique=True)
            await ctx.send(f"🔗 Link de convite criado: {invite.url}")
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao criar o link: {e}")

async def setup(bot):
    await bot.add_cog(InviteManager(bot))