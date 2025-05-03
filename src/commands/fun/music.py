import discord
from discord.ext import commands
import youtube_dl
import asyncio
import yt_dlp as youtube_dl  # Substitua youtube_dl por yt_dlp

# Configurações do yt-dlp
ytdl_format_options = {
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}
ffmpeg_options = {
    "options": "-vn",
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Configurações do youtube_dl
youtube_dl.utils.bug_reports_message = lambda: ""
ytdl_format_options = {
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}
ffmpeg_options = {
    "options": "-vn",
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}  # Fila de músicas por servidor

    async def join_channel(self, ctx):
        """Faz o bot entrar no canal de voz do autor."""
        if ctx.author.voice is None:
            await ctx.send("❌ Você precisa estar em um canal de voz para usar este comando.")
            print("Usuário não está em um canal de voz.")
            return None

        voice_channel = ctx.author.voice.channel
        try:
            if ctx.voice_client is None:
                print(f"Conectando ao canal: {voice_channel.name}")
                await voice_channel.connect()
            elif ctx.voice_client.channel != voice_channel:
                print(f"Movendo para o canal: {voice_channel.name}")
                await ctx.voice_client.move_to(voice_channel)
        except Exception as e:
            print(f"Erro ao conectar ao canal de voz: {e}")
            await ctx.send(f"❌ Não foi possível conectar ao canal de voz: {e}")
            return None

        return ctx.voice_client

    @commands.command(name="play")
    async def play(self, ctx, *, query):
        """Adiciona uma música à fila e começa a tocar."""
        voice_client = await self.join_channel(ctx)
        if voice_client is None:
            return

        guild_id = ctx.guild.id
        if guild_id not in self.queue:
            self.queue[guild_id] = []

        # Baixa informações da música
        try:
            # Se não for uma URL, realiza uma busca no YouTube
            if not query.startswith("http://") and not query.startswith("https://"):
                query = f"ytsearch:{query}"

            info = ytdl.extract_info(query, download=False)
            url2 = info["entries"][0]["formats"][0]["url"]  # Pega o primeiro resultado da busca
            title = info["entries"][0].get("title", "Música Desconhecida")
        except Exception as e:
            await ctx.send(f"❌ Não foi possível processar o link ou termo de busca: {e}")
            return

        # Adiciona à fila
        self.queue[guild_id].append({"title": title, "url": url2})
        await ctx.send(f"🎵 Adicionado à fila: **{title}**")

        # Se não estiver tocando, começa a tocar
        if not voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        """Toca a próxima música na fila."""
        guild_id = ctx.guild.id
        if guild_id not in self.queue or len(self.queue[guild_id]) == 0:
            await ctx.voice_client.disconnect()
            return

        song = self.queue[guild_id].pop(0)
        ctx.voice_client.play(
            discord.FFmpegPCMAudio(song["url"], **ffmpeg_options),
            after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
        )
        await ctx.send(f"🎶 Tocando agora: **{song['title']}**")

    @commands.command(name="skip")
    async def skip(self, ctx):
        """Pula a música atual."""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("❌ Não há nenhuma música tocando no momento.")
            return

        ctx.voice_client.stop()
        await ctx.send("⏭️ Música pulada!")

    @commands.command(name="stop")
    async def stop(self, ctx):
        """Para a reprodução e limpa a fila."""
        if ctx.voice_client is None:
            await ctx.send("❌ O bot não está em um canal de voz.")
            return

        self.queue[ctx.guild.id] = []
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Reprodução encerrada e fila limpa!")

async def setup(bot):
    await bot.add_cog(Music(bot))