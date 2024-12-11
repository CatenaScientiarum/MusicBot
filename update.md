Music Bot for Discord

This Discord bot allows you to play music from YouTube and Spotify, manage your song queue, skip songs, repeat songs, and get a link to the current track. The bot uses discord.py libraries to work with Discord, as well as yt-dlp to fetch videos from YouTube and spotipy to work with Spotify.

Libraries and frameworks used:
discord.py: The main library for interacting with the Discord API.
yt-dlp: Used to download and retrieve data from YouTube.
spotipy: Library for working with the Spotify API.
asyncio: For asynchronous code execution.

Main features:
!play [search/URL]: Adds a song from YouTube or Spotify to the queue.
!skip: Skips the current song.
!skipNext: Removes the next song from the queue.
!skipAll: Clears the entire queue, including the current song.
!replay [count]: Repeats the current song or a song in the queue a specified number of times.
!queue: Displays the current song queue.
!get: Displays a link to the current song on YouTube or Spotify.
!info: Displays a list of available commands.
