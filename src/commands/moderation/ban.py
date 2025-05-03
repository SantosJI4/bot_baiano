import discord
from discord.ext import commands
from discord.ui import View, Button

class BanConfirmationView(View):
    def __init__(self, ctx, member, reason):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.member = member
        self.reason = reason
        self.result = None

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Apenas o autor do comando pode tomar essa decisão.", ephemeral=True)
            return

        self.result = True
        await interaction.response.send_message(f"✅ {self.member.mention} foi banido com sucesso!")
        await self.member.ban(reason=self.reason)
        self.stop()

    @discord.ui.button(label="Não", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Apenas o autor do comando pode tomar essa decisão.", ephemeral=True)
            return

        self.result = False
        await interaction.response.send_message("❌ Banimento cancelado.")
        self.stop()


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Nenhum motivo especificado"):
        """Inicia o processo de banimento de um membro."""
        embed = discord.Embed(
            title="⚠️ Confirmação de Banimento",
            description=(
                f"Você está prestes a banir {member.mention}.\n\n"
                f"**Motivo:** {reason}\n\n"
                "Clique em **Sim** para confirmar ou **Não** para cancelar."
            ),
            color=discord.Color.red()
        )
        embed.set_image(url="https://media.tenor.com/uBXw33B8tlIAAAAM/thor-banhammer.gif")  # GIF de banimento
        embed.set_footer(text="Decisão final necessária.")

        view = BanConfirmationView(ctx, member, reason)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="ban_test")
    @commands.has_permissions(administrator=True)
    async def ban_test(self, ctx):
        """Comando de teste para visualizar o sistema de banimento."""
        embed = discord.Embed(
            title="⚠️ Teste de Banimento",
            description="Este é um teste do sistema de banimento estilizado.",
            color=discord.Color.orange()
        )
        embed.set_image(url="https://media.tenor.com/uBXw33B8tlIAAAAM/thor-banhammer.gif")  # GIF de banimento
        embed.set_footer(text="Teste realizado com sucesso.")

        await ctx.send(embed=embed)

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(Moderation(bot))