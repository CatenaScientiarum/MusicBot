import discord
from discord.ext import commands
from discord.ui import Button, View
import yt_dlp
import asyncio
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
FFMPEG_OPTIONS = {
    'options': '-vn',
         'before_options': (
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 5 '
        '-probesize 32M '
        '-fflags +nobuffer '
        '-flush_packets 1 '
        '-rw_timeout 15000000 '
    )
}

YDL_OPTIONS = {
    'format': 'bestaudio[ext=webm]/bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': True,
    'verbose': True,
    'default_search': 'ytsearch',
}

URL_REGEX = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')
SPOTIFY_REGEX = re.compile(r'(https?://)?(www\.)?(open\.)?spotify\.com/(track|album|playlist)/[\w-]+')

# Установите свои client_id и client_secret
SPOTIPY_CLIENT_ID = 'YOUR_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))
class MusicControlView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # Без тайм-ауту
        self.bot = bot

    @discord.ui.button(label="⏯️ Pause/Resume", style=discord.ButtonStyle.green)
    async def pause_resume(self, interaction: discord.Interaction, button: Button):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("⏸️ Музика поставлена на паузу.", ephemeral=True)
        elif voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("▶️ Музика відновлена.", ephemeral=True)
        else:
            await interaction.response.send_message("Зараз нічого не грає.", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.blurple)
    async def skip(self, interaction: discord.Interaction, button: Button):
        command = self.bot.get_command("skip")
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(command)
        
    @discord.ui.button(label="⏭️ Skip Next", style=discord.ButtonStyle.blurple)
    async def skip_next(self, interaction: discord.Interaction, button: Button):
        command = self.bot.get_command("skipNext")
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(command)

    @discord.ui.button(label="📜 Queue", style=discord.ButtonStyle.gray)
    async def show_queue(self, interaction: discord.Interaction, button: Button):
        command = self.bot.get_command("queue")
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(command)
        await interaction.response.defer()

    @discord.ui.button(label="🔄 Replay", style=discord.ButtonStyle.green)
    async def replay(self, interaction: discord.Interaction, button: Button):
        command = self.bot.get_command("replay")
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(command)
        await interaction.response.defer()

    @discord.ui.button(label="🗑️ Skip All", style=discord.ButtonStyle.red)
    async def skip_all(self, interaction: discord.Interaction, button: Button):
        command = self.bot.get_command("skipall")
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(command)
        await interaction.response.defer()

    @discord.ui.button(label="🔗 Get Link", style=discord.ButtonStyle.blurple)
    async def get_link(self, interaction: discord.Interaction, button: Button):
        command = self.bot.get_command("get")
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(command)
        await interaction.response.defer()

    @discord.ui.button(label="Info", style=discord.ButtonStyle.gray)
    async def info(self, interaction: discord.Interaction, button: Button):
        command = self.bot.get_command("info")
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(command)
        await interaction.response.defer()
            
class MusicBot(commands.Cog):
    def __init__(self, global_client):
        self.client = global_client
        self.queue = []  
        self.current_track = None
        self.replay_count = 0
        self.last_text_channel = None
        self.last_youtube_url = None
        self.last_spotify_url = None
    async def add_to_queue(self, title, url, is_spotify):
        # Покращена перевірка на наявність треку в черзі
        if not any(track[0] == title for track in self.queue):
            self.queue.append((title, url, is_spotify))

    @commands.command()
    async def play(self, ctx, *, search: str = None):
        self.last_text_channel = ctx.channel
        if not search:
            return await ctx.send("Будь ласка, введіть назву треку або URL.")

        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("Для активації зайдіть в голосовий канал.")

        if not ctx.voice_client:
            await voice_channel.connect()

        async with ctx.typing():
            try:
                if re.match(URL_REGEX, search):
                    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(search, download=False)
                        url = info['url']
                        title = info['title']
                        self.queue.append((title, url, False))
                        await ctx.send(f'Додав у чергу: **{title}**')
                elif re.match(SPOTIFY_REGEX, search):
                    if "playlist" in search:
                        playlist_id = search.split("/")[-1].split("?")[0]
                        playlist_tracks = sp.playlist_tracks(playlist_id)["items"]
                        await ctx.send(f'Додаю пісні з плейлиста в чергу...')

                        tasks = []
                        for item in playlist_tracks:
                            track_info = item['track']
                            title = track_info['name'] + ' ' + ' '.join(artist['name'] for artist in track_info['artists'])
                            if (title, None, True) not in self.queue:
                                tasks.append(self.add_to_queue(title, None, True))
                    
                        await asyncio.gather(*tasks)
                        await ctx.send(f'Плейлист додано до черги!')
                    else:
                        spotify_info = sp.track(search)
                        title = spotify_info['name'] + ' ' + ' '.join(artist['name'] for artist in spotify_info['artists'])
                        if (title, None, True) not in self.queue:
                            self.queue.append((title, None, True))
                            await ctx.send(f'Додав у чергу: **{title}**')
                else:
                    # Якщо це пошук за ключовими словами
                    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(f"ytsearch:{search}", download=False)
                        if 'entries' in info:
                            info = info['entries'][0]
                        url = info['url']
                        title = info['title']
                        self.queue.append((title, url, False))
                        await ctx.send(f'Додав у чергу: **{title}**')
            except Exception as e:
                pass

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    @commands.command()
    async def play_next(self, ctx):
        if self.replay_count > 0:
            self.replay_count -= 1
            title, url, is_spotify = self.current_track
            self.queue.append((title, url, is_spotify))
            await ctx.send(f'**{title}** буде повторено.')
        else:
            if self.queue:
                title, url, is_spotify = self.queue.pop(0)
                self.current_track = (title, url, is_spotify)
            else:
                return await ctx.send('Черга порожня :(')

        try:
            if is_spotify:
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{title}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    url = info['url']
    
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda e: self.client.loop.create_task(self.play_next(ctx)))
            
            await ctx.send(f'Зараз грає **{title}**')
            view = MusicControlView(self.client)
            await ctx.send("🎵 Управляйте музикою за допомогою кнопок нижче:", view=view)
                    
        except Exception as e:
            pass  


        
    @commands.command()
    async def replay(self, ctx, times: int = 1, track_num: int = None):
        """Повторити заданий трек із черги кілька разів на початку."""
        if times < 1 or times > 10:
            return await ctx.send("Число повторень повинно бути від 1 до 10.")

        if track_num is None:
            # Якщо не вказано номер треку, повторюється поточна пісня
            if not self.current_track:
                return await ctx.send("Наразі немає відтворюваної пісні для повторення.")
    
            title, url, is_spotify = self.current_track
    
            # Вставляємо повтори поточного треку після нього в чергу
            for i in range(times):
                self.queue.insert(i - 1, (title, url, is_spotify))
    
            await ctx.send(f'Пісня **{title}** буде повторена {times} разів на початку черги.')
    
        else:
            # Якщо вказано номер треку, перевіряємо його дійсність
            if track_num < 1 or track_num > len(self.queue):
                return await ctx.send("Номер пісні недійсний. Переконайтесь, що він у межах черги.")
    
            title, url, is_spotify = self.queue[track_num - 1]
    
            # Вставляємо повтори треку починаючи з його позиції у черзі, зсуваючи інші треки
            for i in range(times):
                self.queue.insert(track_num - i, (title, url, is_spotify))
    
            await ctx.send(f'Пісня **{title}** буде повторена {times} разів на позиції {track_num}.')



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_client = discord.utils.get(self.client.voice_clients, guild=member.guild)
    
        if voice_client:
            if len(voice_client.channel.members) == 1:
                await voice_client.disconnect()
                if self.last_text_channel:  # Використовуємо текстовий канал, з якого викликали команду
                    await self.last_text_channel.send("Ніхто не в голосовому каналі. Виходжу.")

    @commands.command()
    async def skip(self, ctx):
        """Пропуск і видалення поточної пісні."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Пропущено поточну пісню.")
        else:
            await ctx.send("Наразі немає відтворюваної пісні.")

    @commands.command()
    async def skipNext(self, ctx):
        """Видалення наступної пісні з черги."""
        if self.queue:
            removed_track = self.queue.pop(0)
            await ctx.send(f'Наступна пісня видалена з черги: **{removed_track[0]}**')
        else:
            await ctx.send("Черга порожня, немає наступної пісні для видалення.")

    @commands.command()
    async def skipAll(self, ctx):
        """Очищення черги разом із поточною піснею."""
        self.queue = [track for track in self.queue if not track[2]]  # Remove replayed tracks
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()  # Stop the current song
        await ctx.send("Усі пісні видалено з черги, включно з поточною.")

    @commands.command()
    async def queue(self, ctx):
        """Показати поточну чергу."""
        # Повідомлення про те, що грає зараз
        current_track_message = f"**Грає зараз:** {self.current_track[0]}" if self.current_track else "**Грає зараз:** Нічого"

        # Перевірка наявності треків у черзі
        if not self.queue:
            return await ctx.send(f"{current_track_message}\n**Черга порожня.**")

        # Відображення черги
        queue_list = "\n".join([
            f"{index + 1}. {title} ({'Spotify' if is_spotify else 'YouTube'})"
            for index, (title, url, is_spotify) in enumerate(self.queue)
        ])

        await ctx.send(f"{current_track_message}\n**Поточна черга:**\n{queue_list}")

    @commands.command()
    async def get(self, ctx):
        """Отримати URL YouTube або Spotify поточної пісні."""
        if self.current_track:
            title, url, is_spotify = self.current_track
            response = f"**Поточна пісня:** {title}\n"

            if is_spotify:
                if self.last_spotify_url:
                    response += f"Посилання на Spotify: {self.last_spotify_url}\n"
                else:
                    response += "Посилання на Spotify не знайдено.\n"
                
                async with ctx.typing():
                    try:
                        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                            info = ydl.extract_info(f"ytsearch:{title}", download=False)
                            if 'entries' in info:
                                info = info['entries'][0]
                            youtube_url = info['webpage_url']
                            response += f"Посилання на YouTube: {youtube_url}"
                    except Exception as e:
                        response += f"Помилка при пошуку URL для {title}: {e}"
            else:
                response += f"Посилання: {url}"
    
            await ctx.send(response)
        else:
            await ctx.send("Наразі немає відтворюваної пісні.")


    @commands.command()
    async def info(self, ctx):
        commands_list = """
        **!play [пошук/URL]** - Додати пісню в чергу.
        **!skip** - Пропустити поточну пісню.
        **!skipNext** - Видалити наступну пісню з черги.
        **!skipAll** - Видалити всі пісні з черги (включно з поточною).
        **!replay [кількість]** - Повторити поточну пісню кілька разів.Ви можете повторити будь що в черзі !replay "кількість" "номер пісні в черзі"
        **!queue** - Показати список треків у черзі.
        **!get** - Вивести посилання на поточну пісню.
        **!info** - Вивести список усіх команд.
        """
        await ctx.send(commands_list)

client = commands.Bot(command_prefix="!", intents=intents)

async def main():
    await client.add_cog(MusicBot(client))
    await client.start('YOUR_TOKEN')

asyncio.run(main())