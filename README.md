# MusicBot
This code is not very optimized for local operation, be prepared to put it on hosting
 MusicBot for Discord
 This is a simple music bot for Discord that can play tracks from Spotify via YouTube search integration. It supports basic controls like playing, skipping, and repeating tracks.

Features
Play music from Spotify links.
Queue management.
Replay track multiple times.
Skip current track.
Libraries and Frameworks Used
discord.py: For interacting with the Discord API and handling voice channels.
yt-dlp: For downloading audio from YouTube.
spotipy: For interacting with the Spotify API.
Requirements
Python 3.8 or higher
discord.py: For creating and managing the bot.
yt-dlp: For extracting YouTube audio.
spotipy: For interacting with Spotify.

Commands
!play <spotify link>: Adds a song to the queue from a Spotify link.
!replay <times>: Repeats the current track the specified number of times.
!skip: Skips the current track and plays the next one in the queue.
Usage
Invite the bot to your server.
Join a voice channel.
Use !play <spotify link> to play a song from Spotify.
Control playback with !replay <times> and !skip.
Important Notes
Before uploading the bot code to GitHub, remove any hardcoded sensitive information such as:
Spotify Client ID and Client Secret.
Discord Bot Token.
Use environment variables or configuration files to store sensitive data securely.
License
This project is licensed under the MIT License - see the LICENSE.md file for details.