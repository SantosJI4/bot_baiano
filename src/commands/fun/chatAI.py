import discord
from discord.ext import commands
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Carrega o modelo e o tokenizer da Hugging Face
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {device}")


class ChatAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chat_history = {}  # Armazena o histórico de conversas por usuário

    @commands.command(name="chat")
    async def chat(self, ctx, *, prompt):
        """Conversa com o modelo DialoGPT."""
        user_id = ctx.author.id
        if user_id not in self.chat_history:
            self.chat_history[user_id] = []

        # Adiciona a mensagem do usuário ao histórico
        self.chat_history[user_id].append(f"User: {prompt}")

        # Tokeniza o histórico de conversa
        input_ids = tokenizer.encode(" ".join(self.chat_history[user_id]), return_tensors="pt")

        # Gera a resposta
        response_ids = model.generate(input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(response_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)

        # Adiciona a resposta ao histórico
        self.chat_history[user_id].append(f"Bot: {response}")

        await ctx.send(f"🤖 {response}")

async def setup(bot):
    await bot.add_cog(ChatAI(bot))