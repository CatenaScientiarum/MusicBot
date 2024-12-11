Changes in the second code relative to the first:
Adding support for Spotify:

The second code adds the use of the spotipy library to work with Spotify.
Added the ability to handle Spotify links (songs, albums, and playlists).
Added !play command, which can now add songs not only from YouTube, but also from Spotify by checking the URL on Spotify using the SPOTIFY_REGEX regular expression.
Improved queue management:

In the second code, the song queue management has been improved:
Added the ability to add songs from Spotify (both individual tracks and playlists).
Improved logic for adding songs to the queue, taking into account that one song will not be added several times (checking if the song is in the queue).
The ability to repeat a song several times (the !replay command).
Adding buttons to control music:

A new MusicControlView class has been added to the code, which creates buttons for controlling music playback (pause, skip songs, display the queue, repeat tracks, etc.)
The buttons are integrated into the command for playing songs so that users can control music directly from messages.
YouTube video processing via yt-dlp:

Improved use of yt-dlp to retrieve URLs of songs and videos from YouTube has been added to the song processing.
There is logic in the code to search for songs on YouTube using keywords and add them to the queue.
New queue management:

New commands have been added:
!skipNext: Removes the next song from the queue.
!skipAll: Clears the entire queue, including the current song.
!queue: Displays the current song queue.
!get: Displays the URL of the current song, either on Spotify or YouTube.
The queue logic has also been enhanced to work with songs from Spotify.
Work with the voice channel:

Added functionality for the bot to leave the voice channel if only one participant remains in it to avoid unnecessary resource consumption.
Improvements to the command interface:

Added !info command that displays a list of all available bot commands.
Added logic to display information about the current track, song queue, and the ability to get the song URL from YouTube or Spotify.