import discord
from discord.ext import commands
import openai
import os

# Carrega a chave da API do OpenAI do arquivo .env
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chat")
    async def chat(self, ctx, *, prompt):
        """Conversa com o ChatGPT usando a API do OpenAI."""
        await ctx.send("🤖 Processando sua mensagem...")
        try:
            # Envia a mensagem para a API do ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Modelo usado
                messages=[
                    {"role": "system", "content": "Você é um assistente útil e amigável."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            # Resposta do ChatGPT
            reply = response["choices"][0]["message"]["content"]
            await ctx.send(f"💬 {reply}")
        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao processar sua mensagem: {e}")

async def setup(bot):
    await bot.add_cog(ChatAI(bot))