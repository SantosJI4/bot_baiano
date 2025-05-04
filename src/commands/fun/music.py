import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

# Configurações do yt-dlp para SoundCloud
ytdl_format_options = {
    "format": "bestaudio/best",
    "quiet": True,       # Suprimir logs desnecessários
    "default_search": "scsearch",  # Busca no SoundCloud por padrão
}
ffmpeg_options = {
    "options": "-vn",  # Ignorar vídeo
    "options": "-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",  # Ignorar vídeo e reconectar automaticamente
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_song = None  # Armazena informações da música atual
        self.song_queue = []  # Fila de músicas

    async def join_channel(self, ctx):
        """Faz o bot entrar no canal de voz do autor."""
        if ctx.author.voice is None:
            await ctx.send("❌ Você precisa estar em um canal de voz para usar este comando.")
            return None

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

        return ctx.voice_client

    @commands.command(name="play")
    async def play(self, ctx, *, query):
        """Reproduz uma música ou playlist do SoundCloud no canal de voz."""
        voice_client = await self.join_channel(ctx)
        if voice_client is None:
            return

        # Busca o link de streaming no SoundCloud
        try:
            info = ytdl.extract_info(query, download=False)
            if "entries" in info:  # Verifica se é uma playlist
                await ctx.send(f"🎶 Playlist detectada: **{info['title']}** com {len(info['entries'])} faixas.")
                for entry in info["entries"]:
                    self.song_queue.append(entry)  # Adiciona à fila
                await ctx.send("🎶 Playlist adicionada à fila!")
            else:  # É uma única música
                self.song_queue.append(info)
                await ctx.send(f"🎶 Música **{info['title']}** adicionada à fila!")

            # Toca a próxima música se não estiver tocando
            if not voice_client.is_playing():
                await self.play_next(ctx, voice_client)
        except Exception as e:
            await ctx.send(f"❌ Não foi possível processar o termo de busca: {e}")

    async def play_next(self, ctx, voice_client):
        """Toca a próxima música na fila."""
        if len(self.song_queue) == 0:
            self.current_song = None
            await self.bot.change_presence(activity=None)  # Limpa o status do bot
            await ctx.send("✅ Fila de músicas finalizada!")
            return

        # Remove a próxima música da fila
        self.current_song = self.song_queue.pop(0)
        url2 = self.current_song["url"]
        title = self.current_song.get("title", "Música Desconhecida")
        duration = int(self.current_song.get("duration", 0))  # Converte para inteiro

        # Atualiza o status do bot
        await self.bot.change_presence(activity=discord.Game(name=f"Tocando: {title}"))

        # Reproduz a música
        voice_client.play(
            discord.FFmpegPCMAudio(url2, **ffmpeg_options),
            after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx, voice_client), self.bot.loop)
        )
        await ctx.send(f"🎶 Tocando agora: **{title}**\n⏱️ Duração: {duration // 60}:{duration % 60:02d}\n🔗 [Link]({url2})")

    @commands.command(name="skip")
    async def skip(self, ctx):
        """Pula para a próxima música na fila."""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("❌ Não há nenhuma música tocando no momento.")
            return

        ctx.voice_client.stop()  # Para a música atual
        await ctx.send("⏭️ Música pulada!")

    @commands.command(name="stop")
    async def stop(self, ctx):
        """Para a reprodução."""
        if ctx.voice_client is None:
            await ctx.send("❌ O bot não está em um canal de voz.")
            return

        self.song_queue.clear()  # Limpa a fila
        ctx.voice_client.stop()
        await self.bot.change_presence(activity=None)  # Limpa o status do bot
        await ctx.send("⏹️ Reprodução encerrada!")

    @commands.command(name="help")
    async def help(self, ctx):
        """Mostra os comandos disponíveis."""
        commands_list = """
        **Comandos de Música:**
        🎵 `!play <termo ou link>` - Reproduz uma música ou playlist do SoundCloud.
        ⏭️ `!skip` - Pula para a próxima música na fila.
        ⏹️ `!stop` - Para a reprodução e limpa a fila.
        ℹ️ `!help` - Mostra esta mensagem de ajuda.
        """
        await ctx.send(commands_list)

async def setup(bot):
    await bot.add_cog(Music(bot))