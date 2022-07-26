# shrinkray
 A tool for shrinking videos to be under a user-defined size.
 
 This was originally intended for shrinking videos to be under 8MB so that they can be sent in Discord, but can be used for anything requiring video compression.
 It can also download videos from many sites, including YouTube and Reddit.
 
There are many settings within the Python file that area available to edit, to customise shrinkray to the user's needs.
This includes an audio-only mode where only the audio is encoded, and a "meme mode", where videos are encoded at a comically low bitrate.

# Usage
 If you are downloading a video:
 
    - Open shrinkray
    
    - Paste the video link
    
    - Wait for the magic to happen

 If you already have a video:
 
    - Drag the video onto the shrinkray file
    
    - Wait for the magic to happen

# Installation
 shrinkray is a Python script, and therefore requires [Python](https://www.python.org) to be installed in order to run.

 You must install [FFMPEG](https://ffmpeg.org) and add it to your system path. You also need to do this with [yt-dlp](https://github.com/yt-dlp/yt-dlp) - I like to keep this within FFMPEG's bin folder.
 
 On the first launch, you will be prompted to install dependencies. This is done using pip, which is included with Python. You will also be warned if FFMPEG can't be detected. If all is good, you can begin using shrinkray.
