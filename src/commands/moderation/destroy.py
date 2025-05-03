import discord
from discord.ext import commands
import asyncio

class ServerModifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="modificar_servidor")
    @commands.has_permissions(administrator=True)
    async def modificar_servidor(self, ctx):
        """Comando para administradores modificarem o servidor."""
        guild = ctx.guild

        # Confirmação inicial
        await ctx.send("⚠️ Este comando irá modificar o servidor. Deseja continuar? (responda com 'sim' ou 'não')")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["sim", "não"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send("⏰ Tempo esgotado. O comando foi cancelado.")
            return

        if msg.content.lower() == "não":
            await ctx.send("❌ Comando cancelado.")
            return

        # Apagar todos os canais
        await ctx.send("🛠️ Apagando todos os canais...")
        for channel in guild.channels:
            try:
                await channel.delete()
            except Exception as e:
                await ctx.send(f"⚠️ Não foi possível apagar o canal {channel.name}: {e}")

        # Criar um novo canal
        await ctx.send("🛠️ Criando um novo canal...")
        try:
            await guild.create_text_channel("novo-canal")
        except Exception as e:
            await ctx.send(f"⚠️ Não foi possível criar o canal: {e}")

        # Apagar todos os cargos
        await ctx.send("🛠️ Apagando todos os cargos...")
        for role in guild.roles:
            if role.name != "@everyone":  # Não pode apagar o cargo padrão
                try:
                    await role.delete()
                except Exception as e:
                    await ctx.send(f"⚠️ Não foi possível apagar o cargo {role.name}: {e}")

        # Criar um novo cargo
        await ctx.send("🛠️ Criando um novo cargo...")
        try:
            await guild.create_role(name="Novo Cargo", permissions=discord.Permissions(administrator=True))
        except Exception as e:
            await ctx.send(f"⚠️ Não foi possível criar o cargo: {e}")

        # Mensagem final
        await ctx.send("✅ Modificações no servidor concluídas com sucesso!")

async def setup(bot):
    await bot.add_cog(ServerModifier(bot))