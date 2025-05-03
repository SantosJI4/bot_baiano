import discord
from discord.ext import commands
import asyncio

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_mute_role(self, guild):
        """Cria o cargo de mute no servidor, caso ele não exista."""
        mute_role = discord.utils.get(guild.roles, name="Mute")
        if not mute_role:
            try:
                mute_role = await guild.create_role(
                    name="Mute",
                    permissions=discord.Permissions(send_messages=False, speak=False),
                    reason="Cargo de mute criado automaticamente pelo bot."
                )
                # Remove permissões de envio de mensagens em todos os canais
                for channel in guild.channels:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)
                print(f"Cargo 'Mute' criado no servidor {guild.name}.")
            except Exception as e:
                print(f"Erro ao criar o cargo de mute: {e}")
        return mute_role

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 0, *, reason="Nenhum motivo especificado"):
        """
        Silencia um membro aplicando o cargo de mute.
        Duração é opcional e deve ser especificada em minutos.
        """
        mute_role = await self.create_mute_role(ctx.guild)

        if mute_role in member.roles:
            await ctx.send(f"❌ {member.mention} já está mutado.")
            return

        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"✅ {member.mention} foi mutado.\n**Motivo:** {reason}\n**Duração:** {duration} minutos" if duration > 0 else f"✅ {member.mention} foi mutado indefinidamente.\n**Motivo:** {reason}")

        # Se uma duração foi especificada, remove o mute após o tempo
        if duration > 0:
            await asyncio.sleep(duration * 60)  # Converte minutos para segundos
            if mute_role in member.roles:  # Verifica se o membro ainda está mutado
                await member.remove_roles(mute_role, reason="Tempo de mute expirado.")
                await ctx.send(f"✅ {member.mention} não está mais mutado (tempo expirado).")

    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Remove o silêncio de um membro."""
        mute_role = discord.utils.get(ctx.guild.roles, name="Mute")

        if not mute_role or mute_role not in member.roles:
            await ctx.send(f"❌ {member.mention} não está mutado.")
            return

        await member.remove_roles(mute_role, reason="Silêncio removido pelo administrador.")
        await ctx.send(f"✅ {member.mention} não está mais mutado.")

    @commands.command(name="mute_test")
    @commands.has_permissions(administrator=True)
    async def mute_test(self, ctx):
        """Comando de teste para verificar o sistema de mute."""
        embed = discord.Embed(
            title="🔇 Teste do Sistema de Mute",
            description="Este é um teste do sistema de mute. Use os comandos `!mute` e `!unmute` para gerenciar silêncios.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Teste realizado com sucesso.")
        await ctx.send(embed=embed)

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(Mute(bot))  # Certifique-se de que o nome da classe está correto