import discord
from discord.ext import commands
import akinator
import asyncio

class AkinatorGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aki = akinator.Akinator()

    @commands.command(name="akinator")
    async def start_akinator(self, ctx):
        """Inicia o jogo do Akinator."""
        await ctx.send("🤔 Pense em um personagem, e eu tentarei adivinhar! Responda com `sim`, `não`, `não sei`, `provavelmente` ou `provavelmente não`. Para encerrar, digite `parar`.")

        try:
            print("Tentando iniciar o jogo do Akinator...")
            question = self.aki.start_game(language="pt")  # Especifique o idioma
            print(f"Pergunta inicial recebida: {question}")
            if not question:
                await ctx.send("❌ Não consegui iniciar o jogo. Tente novamente mais tarde.")
                return

            # Loop de perguntas
            while self.aki.progression <= 80:
                await ctx.send(f"❓ {question} (Progresso: {self.aki.progression:.2f}%)")
                try:
                    response = await self.bot.wait_for(
                        "message",
                        timeout=60.0,
                        check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    )
                except asyncio.TimeoutError:
                    await ctx.send("⏰ Tempo esgotado! Jogo encerrado.")
                    return

                answer = response.content.lower()

                if answer in ["sim", "s"]:
                    question = self.aki.answer("yes")
                elif answer in ["não", "n"]:
                    question = self.aki.answer("no")
                elif answer in ["não sei", "nao sei"]:
                    question = self.aki.answer("idk")
                elif answer in ["provavelmente", "prov"]:
                    question = self.aki.answer("probably")
                elif answer in ["provavelmente não", "prov nao"]:
                    question = self.aki.answer("probably not")
                elif answer == "parar":
                    await ctx.send("🛑 Jogo encerrado!")
                    return
                else:
                    await ctx.send("❌ Resposta inválida. Use: `sim`, `não`, `não sei`, `provavelmente` ou `provavelmente não`.")
                    continue

            # Akinator faz uma suposição
            self.aki.win()
            await ctx.send(f"🎉 Eu acho que é: **{self.aki.first_guess['name']}** ({self.aki.first_guess['description']})!\n\n{self.aki.first_guess['absolute_picture_path']}")
            await ctx.send("Eu acertei? Responda com `sim` ou `não`.")
            response = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            if response.content.lower() in ["sim", "s"]:
                await ctx.send("🎉 Eu sabia!")
            else:
                await ctx.send("😢 Que pena! Vou tentar melhorar na próxima vez.")
        except akinator.AkiNoQuestions:
            await ctx.send("❌ Não consegui encontrar mais perguntas. Jogo encerrado.")
        except Exception as e:
            print(f"Erro ao iniciar o jogo: {e}")
            await ctx.send(f"❌ Ocorreu um erro ao iniciar o jogo: {e}")

async def setup(bot):
    await bot.add_cog(AkinatorGame(bot))