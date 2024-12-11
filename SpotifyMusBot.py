
import discord
from discord.ext import commands
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
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': False,
    'verbose': True,
}

SPOTIFY_REGEX = re.compile(r'(https?://)?(www\.)?(open\.)?spotify\.com/(track|album|playlist)/.+')

SPOTIPY_CLIENT_ID = 'SPOTIPY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'SPOTIPY_CLIENT_SECRET'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

class MusicBot(commands.Cog):
    def __init__(self, global_client):
        self.client = global_client
        self.queue = []
        self.current_track = None
        self.replay_count = 0

    @commands.command()
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("Enter channel to activate")
        if not ctx.voice_client:
            await voice_channel.connect()

        async with ctx.typing():
            try:
                if re.match(SPOTIFY_REGEX, search):
                    spotify_info = sp.track(search)
                    title = spotify_info['name'] + ' ' + ' '.join(artist['name'] for artist in spotify_info['artists'])
                    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(f"ytsearch:{title}", download=False)
                        if 'entries' in info:
                            info = info['entries'][0]
                        url = info['url']
                        title = info['title']
                else:
                    await ctx.send("Please only use links to Spotify")
                    return

                self.queue.append((url, title))
                await ctx.send(f'Added to the queue: **{title}**')
            except yt_dlp.utils.DownloadError as e:
                await ctx.send(f"Error when uploading a video: {e}")
            except Exception as e:
                await ctx.send(f"Error while processing a request: {e}")

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if self.replay_count > 0:
            self.replay_count -= 1
            url, title = self.current_track
        else:
            if self.queue:
                url, title = self.queue.pop(0)
                self.current_track = (url, title)
            else:
                return await ctx.send('The queue is empty:(')

        try:
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda _: self.client.loop.create_task(self.play_next(ctx)))
            await ctx.send(f'Now playing **{title}**')
        except Exception as e:
            await ctx.send(f"Error during playback: {e}")

    @commands.command()
    async def replay(self, ctx, times: int):
        if times < 1:
            return await ctx.send("The number of repetitions must be greater than zero")
        self.replay_count = times
        await ctx.send(f'The current music will be repeated {times} times.')

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Rewind the track")

client = commands.Bot(command_prefix="!", intents=intents)

async def main():
    await client.add_cog(MusicBot(client))
    await client.start('YOUR_BOT_TOKEN')

asyncio.run(main())
