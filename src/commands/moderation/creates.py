import discord
from discord.ext import commands

class ServerTemplate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="criar_template")
    @commands.has_permissions(administrator=True)
    async def criar_template(self, ctx, template: str = "padrão"):
        """
        Cria um template de servidor com base em um modelo predefinido.
        Modelos disponíveis: padrão, comunidade, suporte.
        """
        await ctx.send("⚙️ Criando o template do servidor...")

        # Modelos de templates
        templates = {
            "padrão": [
                {"categoria": "Geral", "canais": ["geral", "regras", "anúncios"]},
                {"categoria": "Texto", "canais": ["chat", "memes", "sugestões"]},
                {"categoria": "Voz", "canais": ["Geral", "Música"]},
            ],
            "comunidade": [
                {"categoria": "Boas-vindas", "canais": ["regras", "apresentações"]},
                {"categoria": "Discussões", "canais": ["geral", "off-topic", "arte"]},
                {"categoria": "Voz", "canais": ["Geral", "Jogos"]},
            ],
            "suporte": [
                {"categoria": "Informações", "canais": ["regras", "faq", "anúncios"]},
                {"categoria": "Suporte", "canais": ["pedir-suporte", "relatar-bugs"]},
                {"categoria": "Voz", "canais": ["Suporte 1", "Suporte 2"]},
            ],
        }

        # Verifica se o template existe
        if template not in templates:
            await ctx.send(f"❌ Template `{template}` não encontrado. Use: `padrão`, `comunidade` ou `suporte`.")
            return

        # Cria as categorias e canais com base no template
        for categoria in templates[template]:
            cat = await ctx.guild.create_category(categoria["categoria"])
            for canal in categoria["canais"]:
                if "voz" in categoria["categoria"].lower():
                    await ctx.guild.create_voice_channel(canal, category=cat)
                else:
                    await ctx.guild.create_text_channel(canal, category=cat)

        await ctx.send(f"✅ Template `{template}` criado com sucesso!")

async def setup(bot):
    await bot.add_cog(ServerTemplate(bot))