import discord
from discord.ext import commands
import os
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Função para carregar o prefixo do arquivo de configuração
CONFIG_FILE = "./config.json"

def get_prefix(bot, message):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config.get("prefix", "!")
    return "!"

# Initialize the bot with a dynamic prefix
intents = discord.Intents.default()
intents.message_content = True  # Ativa o acesso ao conteúdo das mensagens
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# Função para carregar cogs dinamicamente
async def load_cogs():
    for folder in ['economy', 'fun', 'moderation']:
        cog_path = f'./src/commands/{folder}'
        for filename in os.listdir(cog_path):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await bot.load_extension(f'commands.{folder}.{filename[:-3]}')
                    print(f"✅ Cog carregado: commands.{folder}.{filename[:-3]}")
                except Exception as e:
                    print(f"❌ Erro ao carregar cog {filename}: {e}")

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')
    print("✅ Bot está pronto e conectado ao Discord.")
    await bot.load_extension("commands.economy.cassino")

    # Inicia o loop do evento de carro-forte
    carro_forte_cog = bot.get_cog("CarroForte")
    if carro_forte_cog:
        if not carro_forte_cog.start_event_loop.is_running():
            carro_forte_cog.start_event_loop.start()
            print("🔄 Loop do evento de carro-forte iniciado.")
    else:
        print("❌ Cog 'CarroForte' não encontrado.")

@bot.command()
async def cogs(ctx):
    """Lista os cogs carregados no bot."""
    cogs = list(bot.cogs.keys())
    await ctx.send(f"Cogs carregados: {', '.join(cogs)}")

# Comando para atualizar o prefixo
@bot.command(name="setprefix")
@commands.has_permissions(administrator=True)
async def set_prefix(ctx, new_prefix: str):
    """Atualiza o prefixo do bot."""
    print(f"Comando 'setprefix' executado por {ctx.author.name} com o novo prefixo: {new_prefix}")
    if len(new_prefix) > 5:
        await ctx.send("❌ O prefixo não pode ter mais de 5 caracteres.")
        return

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    else:
        config = {}

    config["prefix"] = new_prefix
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    
    await ctx.send(f"✅ Prefixo atualizado para: `{new_prefix}`")
import os

if os.path.exists("./assets/fonts/DejaVuSans.ttf"):
    print("Fonte encontrada!")
else:
    print("Fonte não encontrada!")
@bot.event
async def on_message(message):
    """Gerencia mensagens recebidas e processa comandos."""
    if message.author.bot:
        return  # Ignora mensagens de outros bots

    print(f"Mensagem recebida: {message.content} de {message.author.name}")

    # Verifica se a mensagem é um comando
    if message.content.startswith(await bot.get_prefix(message)):
        try:
            # Apaga a mensagem do comando enviada pelo usuário
            await message.delete()
            print(f"Comando apagado: {message.content}")
        except discord.Forbidden:
            print("O bot não tem permissão para apagar mensagens neste canal.")
        except Exception as e:
            print(f"Erro ao tentar apagar o comando: {e}")

    # Garante que os comandos do bot ainda funcionem
    await bot.process_commands(message)


async def main():
    print("Iniciando o bot...")
    async with bot:
        await load_cogs()
        print("✅ Todos os cogs foram carregados com sucesso.")
        await bot.start(TOKEN)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nBot encerrado pelo usuário.")