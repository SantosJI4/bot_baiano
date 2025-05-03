import discord
from discord.ext import commands

class Repeat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repeating_users = {}  # Dicionário para rastrear usuários em modo de repetição

    @commands.command(name="repeart")
    async def start_repeat(self, ctx, user: discord.Member):
        """Inicia o modo de repetição para um usuário específico."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Apenas administradores podem usar este comando.")
            return

        if user.id in self.repeating_users:
            await ctx.send(f"❌ O bot já está repetindo as mensagens de {user.mention}.")
            return

        # Cria um webhook para o canal
        webhook = await ctx.channel.create_webhook(name=f"Repeat-{user.id}")
        self.repeating_users[user.id] = webhook
        await ctx.send(f"✅ O bot agora está repetindo as mensagens de {user.mention} neste canal.")

    @commands.command(name="stoprepeart")
    async def stop_repeat(self, ctx, user: discord.Member):
        """Para o modo de repetição para um usuário específico."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Apenas administradores podem usar este comando.")
            return

        if user.id not in self.repeating_users:
            await ctx.send(f"❌ O bot não está repetindo as mensagens de {user.mention}.")
            return

        # Remove o webhook e para a repetição
        webhook = self.repeating_users.pop(user.id)
        await webhook.delete()
        await ctx.send(f"✅ O bot parou de repetir as mensagens de {user.mention}.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Repete as mensagens dos usuários em modo de repetição."""
        if message.author.bot:
            return  # Ignora mensagens de outros bots

        user_id = message.author.id
        if user_id in self.repeating_users:
            webhook = self.repeating_users[user_id]
            try:
                await webhook.send(
                    content=message.content,
                    username=message.author.display_name,
                    avatar_url=message.author.avatar.url if message.author.avatar else None
                )
            except Exception as e:
                print(f"❌ Erro ao enviar mensagem pelo webhook: {e}")

async def setup(bot):
    await bot.add_cog(Repeat(bot))