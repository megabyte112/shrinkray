# shrinkray, by megabyte112
# https://github.com/megabyte112/shrinkray
# see LICENSE for license info

### ----------[~~Settings~~]---------- ###

# Here you can find advanced settings for shrinkray.
# Lines prefixed with a hash (#) are comments and are ignored by the interpreter.
# Most of these are defaults: you can override them at runtime.
# All booleans (True/False) must have the first letter capitalized.

## ----[General]---- ##

# enable verbose mode.
# default: False
verbose = False

# string appended to filenames.
# default: "_shrinkray"
suffix = "_shrinkray"

# amount of 'wiggle room': higher means more chance of file being too big.
# always keep this less than 1, or else your files will be too large.
# default: 0.95
bitrate_multiplier = 0.95

# default target file size in kB.
# default: 8000
default_size = 8000

# trims the video between two timestamps by default.
# default: False
trim = False

# default shrinking speed, a number between 1 and 10, higher is faster.
# lower speeds lead to more accurate file sizes.
# set to 0 to disable ffmpeg speed presets.
# default: 5
speed = 5

# wait for enter key before closing.
# default: True
wait_when_done = True

# open in file manager by default when done.
# default: True
open_when_done = True

# send desktop notifications by default when shrinkray completes.
# default: True
send_notifs = True

# amount of allowed items in any of shrinkray's folders before showing a warning.
# these folders can eventually reach very large file sizes.
# set to None to disable.
# default: 100
warning_threshold = 100

## -----[Video]----- ##

# maximum allowed size of longest edge (in pixels) before scaling is needed.
# default: 1280
max_res_size = 1280

# framerate limit.
# this is also the framerate that the video can be interpolated to.
# default: 30
target_fps = 30

# container to contain video files.
# default: "mp4"
container = "mp4"

# video codec to use.
# default: "libx264"
video_codec = "libx264"

## -----[Audio]----- ##

# don't include video, and store file in audio container.
# default: False
audioonly = False

# don't include audio. 
# doesn't work when audioonly is True.
# default: False
mute = False

# fraction of bandwith dedicated to audio.
# ignored when mute or audioonly is True.
# must be less than 1.
# default: 1/4
audioratio = 1/4

# highest allowed audio bitrate (in kbps).
# ignored when audioonly is True.
# set to None to disable.
# default: 256
max_audio_bitrate = 256

# container to store audio when audioonly is True.
# default: "mp3"
audiocontainer = "mp3"

# audio codec to use when audioonly is True.
# default: "libmp3lame"
audio_codec = "libmp3lame"

# if you want some good quality audio with a small file size, you can try
# setting the audio container to "opus" and setting the audio codec to "libopus".
# however, opus is not compatible with many programs at this time.

## ----[Colours]---- ##
# or 'colors', whatever.

# allowed colours (for all):
# "red", "green", "blue", "cyan", "magenta", "yellow", "white"

# titles.
# default: "cyan"
titlecol = "cyan"

# when asking for user input.
# default: "yellow"
inputcol = "yellow"

# warnings or errors.
# default: "red"
warningcol = "red"

# usually parts of titles, like 'pass 1' or 'mp3'.
# default: "magenta"
othercol = "magenta"

# file size numbers once completed.
# default: "cyan"
numbercol = "cyan"

# file size units once completed.
# default: "yellow"
unitcol = "yellow"


## ------[Fun]------ ##

# ultra high compression for those moldy shitposts.
# locks video bitrate to 20kbps, and audio bitrate to 10kbps.
# resolution is also smaller and FPS is capped at 10.
# default: False
meme_mode = False

# makes the volume louder, and adds some bass.
# this is for those crunchy earrape memes.
# default: False
loud = False

# add text to the top and bottom of videos.
# default: False
dotext = False

# reverb audio.
# default: False
reverb = False

# playback speed.
# default: 1.0
playbackspeed = 1.0

# interpolate frames if playback speed is changed.
# this makes it look smoother, and is interpolated to target_fps.
# however, this is extremely slow.
# default: False
interpolate = False

# how many times smaller than the width is the text padding.
# higher is smaller.
# default: 10
text_devisor = 10

# amplification.
# only effective when loud is True.
# default: 5
volume_multiplier = 5

# bass boost.
# only effective when loud is True.
# default: 2
bass_multiplier = 2

# how "crunchy" the audio should sound.
# only effective when loud is True.
# default: 64
crunchiness = 64

### -------[~~End of Settings~~]------- ###

# Everything below this point is actual code.
# Only edit if you know exactly what you're doing.


# okay, let's do this.

# import standard libraries
import sys, os, subprocess, math, shutil, logging, time, webbrowser

# get epoch time, this is used for logging filenames.
# aka seconds since Jan 1 1970 0:00:00.
# this allows multiple instances running at once.
launchtime = int(time.time())

# check folders
if not os.path.isdir("logs"):
    os.mkdir("logs")
if not os.path.isdir("output"):
    os.mkdir("output")
if not os.path.isdir("temp"):
    os.mkdir("temp")

tempdir = "temp/"+str(launchtime)
os.mkdir(tempdir)

# don't edit
version = "1.7.5"

# setup logger
logformat='%(asctime)s: %(message)s'
logging.basicConfig(filename=f"logs/shrinkray_{launchtime}.log", filemode="w", level=logging.INFO, format=logformat)
if verbose:
    logging.getLogger().addHandler(logging.StreamHandler())

logging.info("starting")

# determine host OS
if os.name == "nt": # windows
    logging.info("host is Windows")
    nullfile="NUL"
    clearcmd = "cls"
else:   # posix
    logging.info("host is non-Windows")
    nullfile="/dev/null"
    clearcmd = "clear"

# early clear function which requires no dependencies, unlike the other
def earlyclearscreen():
    global clearcmd, version
    os.system(clearcmd)
    print(f"shrinkray {version} | Setup\n")

# check non-standard dependencies
try:
    import ffpb, yt_dlp, notifypy, showinfm, colorama
    logging.info("deps already installed")
except ImportError:
    # time to install deps
    earlyclearscreen()
    logging.info("installing deps")
    print("\nInstalling dependencies, you may see some warnings.\n")
    import pip
    pip.main(["install","--quiet",

    "ffpb",
    "yt-dlp",
    "notify-py",
    "show-in-file-manager",
    "colorama",
    
    "--exists-action","i"])
    import ffpb, yt_dlp, notifypy, showinfm, colorama
    earlyclearscreen()
    logging.info("done deps, closing")
    print("\nDependencies have been installed,\nPlease restart shrinkray.")
    if wait_when_done:
        input("\nPress Enter to close.")
    sys.exit()

# check for ffmpeg
if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
    earlyclearscreen()
    print("\nIt seems like FFMPEG isn't installed, or isn't in your system path.")
    print("Refer to shrinkray's guide for more info.")
    print("https://github.com/megabyte112/shrinkray/wiki/shrinkray-wiki")
    if wait_when_done:
        input("\nWhen you're done, reopen shrinkray, and you're all set.")
    sys.exit()

arg_length = len(sys.argv)

if verbose:
    executable = "ffmpeg"
else:
    executable = "ffpb"

tempfiles = []

# initialise text colouring for Windows hosts since it isn't natively supported,
# this has no effect on other platforms.
colorama.init()

# coloured or bold text
strreset = colorama.Style.RESET_ALL
strbold = colorama.Style.BRIGHT
strunbold = colorama.Style.NORMAL
strred = colorama.Fore.RED
stryellow = colorama.Fore.YELLOW
strgreen = colorama.Fore.GREEN
strblue = colorama.Fore.BLUE
strcyan = colorama.Fore.CYAN
strpurple = colorama.Fore.MAGENTA
strwhite = colorama.Fore.WHITE

def getcolfromtext(text):
    if text=="red":
        return strred
    elif text == "green":
        return strgreen
    elif text == "blue":
        return strblue
    elif text == "cyan":
        return strcyan
    elif text == "magenta":
        return strpurple
    elif text == "yellow":
        return stryellow
    else:
        return strwhite

titlecolour = getcolfromtext(titlecol)
askcolour = getcolfromtext(inputcol)
errorcolour = getcolfromtext(warningcol)
othercolour = getcolfromtext(othercol)
numbercolour = getcolfromtext(numbercol)
unitcolour = getcolfromtext(unitcol)

# define clear function
def clearscreen(stage, color):
    global clearcmd, version, verbose
    if verbose:
        return
    os.system(clearcmd)
    print(f"{strbold}shrinkray {version} | {color}{stage}{strreset}\n")

# configure notifs
logging.info("configuring notifs")

notif_convert = notifypy.Notify()
notif_convert.title = "Converting"
notif_convert.message = "Media is being converted to another format."

notif_audiocompress = notifypy.Notify()
notif_audiocompress.title = "Shrinking Audio"
notif_audiocompress.message = "You'll be notified once compression is complete."

notif_twopass = notifypy.Notify()
notif_twopass.title = "Shrinking Video"
notif_twopass.message = "You'll be notified once compression is complete."

notif_complete = notifypy.Notify()
notif_complete.title = "Shrinking Complete!"
notif_complete.message = "Your video was compressed successfully."

notif_failed = notifypy.Notify()
notif_failed.title = "Shrinking Failed!"
notif_failed.message = "Your video couldn't be compressed properly."

notif_toobig = notifypy.Notify()
notif_toobig.title = "Shrinking Complete!"
notif_toobig.message = "The resulting file is larger than you requested."

notif_smallenough = notifypy.Notify()
notif_smallenough.title = "Complete!"
notif_smallenough.message = "The file was already small enough."

notif_amplify = notifypy.Notify()
notif_amplify.title = "Amplifying"
notif_amplify.message = "Turning up the volume."

notif_mute = notifypy.Notify()
notif_mute.title = "Removing Audio"
notif_mute.message = "Your video will be muted."

notif_text = notifypy.Notify()
notif_text.title = "Writing text"
notif_text.message = "Text is being added to your video."

notif_trim = notifypy.Notify()
notif_trim.title = "Trimming"
notif_trim.message = "Your file is being trimmed to your specified time."

notif_spd = notifypy.Notify()
notif_spd.title = "Changing speed"
notif_spd.message = "The playback speed is being changed."

notif_reverb = notifypy.Notify()
notif_reverb.title = "Adding reverb"
notif_reverb.message = "Reverb is being added to audio."

notif_interpolate = notifypy.Notify()
notif_interpolate.title = "Interpolating"
notif_interpolate.message = "Your video is being interpolated for added smoothness."



logging.info("counting files")

# count the number of files in each folder
def countfiles(path):
    return len(os.listdir(path))

log_count = countfiles("logs")
logging.info(f"logs: {log_count}")

out_count = countfiles("output")
logging.info(f"output: {out_count}")


clearscreen("Waiting for input...", stryellow)

logging.info("args: " + str(sys.argv))
logging.info("wait when done: "+str(wait_when_done))
logging.info("count threshold: "+str(warning_threshold))

logging.info("initialization complete")


# we're running!!
print(f"\n{titlecolour}Welcome back to {strbold}shrinkray{strreset}.")

logging.info(f"shrinkray {version} is running!")
logging.info("tell megabyte112 about any issues :)")

if meme_mode:
    print(f"\n{strbold}{errorcolour}haha shitpost shrinkray go brrrrrrrrr")
    print(f"(meme mode is active by default){strreset}")
if audioonly:
    print(f"\n{strbold}{errorcolour}WARNING: Output will be audio only by default!{strreset}")
elif mute:
    print(f"\n{strbold}{errorcolour}WARNING: Video will be muted by default!{strreset}")
if loud and not mute:
    print(f"\n{strbold}{errorcolour}i hope your ears are okay")
    print(f"(loud mode enabled by default){strreset}")

if warning_threshold is not None:
    sizewarned = False
    if log_count >= warning_threshold:
        sizewarned = True
        print(f"\n{errorcolour}Logs folder contains {log_count} items!")
        print(f"Consider clearing it once shrinkray is closed.{strreset}")
    if out_count >= warning_threshold:
        sizewarned = True
        print(f"\n{errorcolour}Output folder contains {out_count} items!")
        print(f"Consider clearing it once shrinkray is closed.{strreset}")
    
    if sizewarned:
        print(f"\n{errorcolour}You can disable these folder warnings in the settings.{strreset}")


def kibiconvert(value):
    return value*0.9765625

def mebiconvert(value):
    return round(kibiconvert(value)*100/1024)/100

def printsizes(size1, size2):
    print()
    print(f"{titlecolour}before:")
    print(f"    {numbercolour}{round(size1)}{unitcolour}kB{strwhite}, {numbercolour}{round(kibiconvert(size1))}{unitcolour}kiB")
    print(f"    {numbercolour}{round(size1/10)/100}{unitcolour}MB{strwhite}, {numbercolour}{mebiconvert(size1)}{unitcolour}MiB")
    print()
    print(f"{strbold}{titlecolour}after:")
    print(f"    {numbercolour}{round(size2)}{unitcolour}kB{strwhite}, {numbercolour}{round(kibiconvert(size2))}{unitcolour}kiB")
    print(f"    {numbercolour}{round(size2/10)/100}{unitcolour}MB{strwhite}, {numbercolour}{mebiconvert(size2)}{unitcolour}MiB")
    print(strreset)
    shrinkness = round((size2/size1)*1000)/1000
    print(f"{titlecolour}{strbold}File is {othercolour}{shrinkness}x{titlecolour} the original size.{strreset}")
    print()

def CheckValidSizeInput(text):
    if 'k' in text:
        text = text[0:len(text)-1]
    return text.isnumeric() and int(text) >= 0

def CheckValidInput(text):
    return text.isnumeric() and int(text) > 0

def CheckValidSpeedInput(text):
    return text.isnumeric() and int(text) >= 0 and int(text) <= 10

def CheckValidMultiInput(text):
    return text.isnumeric() and int(text) > 0 and int(text) <= 100

def CheckValidRatioInput(text):
    text = text.split("/")
    return len(text) == 2 and text[0].isnumeric() and text[1].isnumeric() and int(text[0]) < int(text[1])

def GetMoreOptionsChoice():
    text = input(f"\n{strbold}{askcolour}More options?{strreset} [Y/N]\n> ")
    return text.lower() == "y"

def GetAdvancedOptionsChoice():
    text = input(f"\n{strbold}{askcolour}Advanced options?{strreset} [Y/N]\n> ")
    return text.lower() == "y"

# ask for target file size
def GetTargetSize():
    text = "abc"
    while not CheckValidSizeInput(text):
        text = input(f"\n{strbold}{askcolour}Target file size in MB {strreset}[add k for kB, or enter 0 for no limit]\n> ")
        if text == "":
            return default_size
        if not CheckValidSizeInput(text):
            logging.warning("rejected input: "+str(text))
            print(f"\n{errorcolour}Make sure your input a whole number!{strreset}")
        if 'k' in text:
            return text[0:len(text)-1]
    return text + "000"

def GetBitrateMultiplier():
    global bitrate_multiplier
    text = "abc"
    while not CheckValidMultiInput(text):
        text = input(f"\n{strbold}{askcolour}Bitrate multiplier {strreset}[as percentage, like 95]\n> ")
        if text == "":
            return bitrate_multiplier*100.0
        if not CheckValidMultiInput(text):
            logging.warning("rejected input: "+str(text))
            print(f"\n{errorcolour}Make sure your input a whole number!{strreset}")
    return text

def GetAudioRatio():
    text = "0"
    while not CheckValidRatioInput(text):
        text = input(f"\n{strbold}{askcolour}Audio ratio {strreset}[as bottom-heavy fraction of two ints: x/y]\n> ")
        if text == "":
            return audioratio
        if not CheckValidRatioInput(text):
            logging.warning("rejected input: "+str(text))
            print(f"\n{errorcolour}Make sure your input a bottom-heavy fraction of two integers, like 1/4.{strreset}")
    text = text.split("/")
    return float(text[0])/float(text[1])

# ask for speed
def GetSpeed():
    text = "123"
    while not CheckValidSpeedInput(text):
        text = input(f"\n{strbold}{askcolour}Encoding speed{strreset} [1-10]\n> ")
        if text == "":
            return speed
        if not CheckValidSpeedInput(text):
            logging.warning("rejected input: "+str(text))
            print(f"\n{errorcolour}Make sure your input a whole number between 1 and 10{strreset}")
    return text

def GetAudioContainer():
    global audiocontainer
    text = input(f"\n{strbold}{askcolour}Audio container{strreset}\n> ")
    if text == "":
        return audiocontainer
    else:
        return text

def GetAudioCodec():
    global audio_codec
    text = input(f"\n{strbold}{askcolour}Audio codec{strreset}\n> ")
    if text == "":
        return audio_codec
    else:
        return text

def GetVideoContainer():
    global container
    text = input(f"\n{strbold}{askcolour}Video container{strreset}\n> ")
    if text == "":
        return container
    else:
        return text

def GetVideoCodec():
    global video_codec
    text = input(f"\n{strbold}{askcolour}Video codec{strreset}\n> ")
    if text == "":
        return video_codec
    else:
        return text

def GetMaxAudioBitrate():
    global max_audio_bitrate
    text = "0"
    while not CheckValidInput(text):
        text = input(f"\n{strbold}{askcolour}Max audio bitrate {strreset}[in kbps]\n> ")
        if text == "":
            return max_audio_bitrate
        if not CheckValidInput(text):
            logging.warning("rejected input: "+str(text))
            print(f"\n{errorcolour}Make sure your input is a whole number greater than 0.{strreset}")
    return text

def GetMaxRes():
    global max_res_size
    text = "0"
    while not CheckValidInput(text):
        text = input(f"\n{strbold}{askcolour}Max resolution {strreset}[in pixels, longest edge]\n> ")
        if text == "":
            return max_res_size
        if not CheckValidInput(text):
            logging.warning("rejected input: "+str(text))
            print(f"\n{errorcolour}Make sure your input is a single whole number greater than 0.{strreset}")
    return text

def GetMaxFramerate():
    global target_fps
    text = "0"
    while not CheckValidInput(text):
        text = input(f"\n{strbold}{askcolour}Max framerate {strreset}[in fps]\n> ")
        if text == "":
            return target_fps
        if not CheckValidInput(text):
            logging.warning("rejected input: "+str(text))
            print(f"\n{errorcolour}Make sure your input is a whole number greater than 0.{strreset}")
    return text

def GetTrimChoice():
    global trim
    text = input(f"\n{strbold}{askcolour}Trim video?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return trim

def GetReverbChoice():
    global reverb
    text = input(f"\n{strbold}{askcolour}Reverb audio?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return reverb

def GetInterpolateChoice():
    global interpolate
    text = input(f"\n{strbold}{askcolour}Interpolate video?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return interpolate

def CheckValidSpeedFloat(text):
    try:
        a = float(text)
    except ValueError:
        return False
    if a >= 0.5 and a <= 2.0:
        return True
    return False

def GetPlaybackSpeed():
    global playbackspeed
    text = "abc"
    while not CheckValidSpeedFloat(text):
        text = input(f"\n{strbold}{askcolour}Playback speed {strreset}[normal speed = 1]\n> ")
        if text == "":
            return playbackspeed
        if not CheckValidSpeedFloat(text):
            logging.warning("rejected input: "+str(text))
            print(f"\n{errorcolour}Make sure your input is a decimal number between 0.5 and 2.0.{strreset}")
    return text

def GetOpenWhenDoneChoice():
    global open_when_done
    text = input(f"\n{strbold}{askcolour}Open file manager when completed?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return open_when_done

def GetAudioChoice():
    global audioonly
    text = input(f"\n{strbold}{askcolour}Get audio only?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return audioonly

def GetNotifChoice():
    global send_notifs 
    text = input(f"\n{strbold}{askcolour}Send notifications?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return send_notifs

def GetMemeChoice():
    global meme_mode
    text = input(f"\n{strbold}{askcolour}Meme mode?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return meme_mode

def GetLoudChoice():
    global loud
    text = input(f"\n{strbold}{askcolour}Loud mode?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return loud

def GetTextChoice():
    global dotext
    text = input(f"\n{strbold}{askcolour}Add text?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return dotext

def GetMuteChoice():
    global mute
    text = input(f"\n{strbold}{askcolour}Mute audio?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return mute

music_sites = [
    "music.youtube.com",
    "bandcamp.com",
    "soundcloud.com",
    "spotify.com",
    "deezer.com"
]

# download video if no arguments are given
if arg_length < 2:
    logging.info("prepare download...")
    url=input(f"\n{strbold}{askcolour}Paste a video link.{strreset}\n> ")
    logging.info(f"input: \"{url}\"")
    audiosite = False
    for site in music_sites:
        if site in url:
            audiosite = True
    if audiosite:
        logging.info("links to audio site")
        print(f"\n{othercolour}This URL links to a music site, your download will be audio-only.{strreset}")
        audioonly = True
        container = audiocontainer
    target_size = int(GetTargetSize())
    if not audiosite:
        audioonly = GetAudioChoice()
    logging.info("target (in kB): "+str(target_size))
    if GetMoreOptionsChoice():
        trim = GetTrimChoice()
        if trim:
            start_time = input(f"\n{strbold}{askcolour}Start time {strreset}[hh:mm:ss] / [m:ss] / [s]\n> ")
            end_time = input(f"\n{strbold}{askcolour}End time {strreset}[hh:mm:ss] / [m:ss] / [s]\n> ")
            if start_time == "":
                start_time = 0
            if end_time == "":
                end_time = -1
            logging.info(f"time range between {start_time} and {end_time}")
        if not audioonly:
            mute = GetMuteChoice()
        meme_mode = GetMemeChoice()
        if not mute:
            loud = GetLoudChoice()
        reverb = GetReverbChoice()
        playbackspeed = float(GetPlaybackSpeed())
        send_notifs = GetNotifChoice()
        open_when_done = GetOpenWhenDoneChoice()
        if not audioonly:
            dotext = GetTextChoice()
        else:
            dotext = False
        if dotext:
            text1 = input(f"\n{strbold}{askcolour}Top text{strreset}\n> ")
            logging.info("text1: "+text1)
            text2 = input(f"\n{strbold}{askcolour}Bottom text{strreset}\n> ")
            logging.info("text2: "+text2)
        if GetAdvancedOptionsChoice():
            print(f"\n{errorcolour}{strbold}Warning: Changing these may result in errors and crashes.{strreset}")
            speed = int(GetSpeed())
            bitrate_multiplier = float(GetBitrateMultiplier())/100.0
            if audioonly:
                audiocontainer = GetAudioContainer()
                audio_codec = GetAudioCodec()
            else:
                container = GetVideoContainer()
                video_codec = GetVideoCodec()
            if not audioonly and not meme_mode:
                audioratio = float(GetAudioRatio())
                max_audio_bitrate = int(GetMaxAudioBitrate())
                max_res_size = int(GetMaxRes())
                target_fps = int(GetMaxFramerate())
                interpolate = GetInterpolateChoice()

    logging.info("trim: "+str(trim))
    logging.info("audioonly: "+str(audioonly))
    logging.info("mute: "+str(mute))
    logging.info("meme: "+str(meme_mode))
    logging.info("loud: "+str(loud))
    logging.info("reverb: "+str(reverb))
    logging.info("playbackspeed: "+str(playbackspeed))
    logging.info("notifs: "+str(send_notifs))
    logging.info("open filemgr: "+str(open_when_done))
    logging.info("text: "+str(dotext))
    logging.info("speed: "+str(speed))
    logging.info("bitratemulti: "+str(bitrate_multiplier))
    if audioonly:
        logging.info("audio container: "+str(audiocontainer))
        logging.info("audio codec: "+str(audio_codec))
    else:
        logging.info("video container: "+str(container))
        logging.info("video codec: "+str(video_codec))
    logging.info("audioratio: "+str(audioratio))
    logging.info("max audio bitrate: "+str(max_audio_bitrate))
    logging.info("max resolution: "+str(max_res_size))
    logging.info("target fps: "+str(target_fps))
    logging.info("interpolate: "+str(interpolate))

    clearscreen("Downloading...", strpurple)

    print(f"\n{titlecolour}Fetching...{strreset}")
    titlecmd = "yt-dlp -e --no-playlist --no-warnings "+url
    logging.info("fetching title with the following command")
    logging.info(titlecmd)
    p = subprocess.getstatusoutput(titlecmd)
    if p[0] != 0:
        logging.info("title grab failed with return code "+str(p[0]))
        print(f"{errorcolour}There was an issue with your video URL.\nPress {strbold}[Enter]{strunbold} or {strbold}close this window{strunbold} and run shrinkray again.")
        print(f"Be sure to check whether your URL is correct!{strreset}")
        logging.shutdown()
        if wait_when_done:
            input()
        sys.exit()
    title = p[1].replace("\"","'")
    url=url.replace("\"","'")
    title = title.replace("/","#")
    logging.info("title: "+str(title))
    print(f"{strgreen}Found - {strbold}{othercolour}\"{title}\"{strreset}")
        
    # easter egg
    if "never gonna give you up" in title.lower() or "rickroll" in title.lower():
        webbrowser.open("https://youtu.be/dQw4w9WgXcQ")
        print(f"\n{othercolour}{strbold}you rickroll me, i rickroll you{strreset}")

    # if using youtube, assume mp4 to save time
    if container == "mp4" and ("youtube.com" in url or "youtu.be" in url or "ytsearch:" in url):
        logging.info("assuming mp4 download")
        typearg = "-f mp4 "
    elif audioonly:
        typearg = "-x "
    else:
        typearg = ""

    # find filename extension
    getfilenamecmd = f"yt-dlp \"{url}\" --get-filename --no-playlist --no-warnings {typearg}-o \"{tempdir}/{title}.%(ext)s\""
    logging.info("fetching filename with the following command")
    logging.info(getfilenamecmd)
    filein = subprocess.getoutput(getfilenamecmd)
    logging.info("filename: "+filein)
    splitfile = filein.split(".")
    extension = splitfile[len(splitfile)-1]
    logging.info("extension: "+extension)
    dlname = f"{tempdir}/dl_{launchtime}.{extension}"
    targetfilename = filein
    filein = dlname

    # escape quotes
    url=url.replace("\"","\\\"")

    if verbose:
        dlcommand = f"yt-dlp \"{url}\" -v --no-playlist {typearg}-o \"{filein}\""
    else:
        dlcommand = f"yt-dlp \"{url}\" --quiet --progress --no-playlist --no-warnings {typearg}-o \"{filein}\""
    print(f"\n{titlecolour}Downloading...{strreset}")
    logging.info("downloading with the following command")
    logging.info(dlcommand)
    os.system(dlcommand)
    filein = tempdir + "/" + os.listdir(tempdir)[0]
else:
    # if user is supplying file
    filein=sys.argv[1]
    targetfilename = filein
    logging.info("target file "+filein)
    target_size = int(GetTargetSize())
    logging.info("target (in kB): "+str(target_size))
    audioonly = GetAudioChoice()
    if GetMoreOptionsChoice():
        trim = GetTrimChoice()
        if trim:
            start_time = input(f"\n{strbold}{askcolour}Start time {strreset}[hh:mm:ss] / [m:ss] / [s]\n> ")
            end_time = input(f"\n{strbold}{askcolour}End time {strreset}[hh:mm:ss] / [m:ss] / [s]\n> ")
            if start_time == "":
                start_time = 0
            if end_time == "":
                end_time = -1
            logging.info(f"time range between {start_time} and {end_time}")
        if not audioonly:
            mute = GetMuteChoice()
        meme_mode = GetMemeChoice()
        if not mute:
            loud = GetLoudChoice()
        reverb = GetReverbChoice()
        playbackspeed = float(GetPlaybackSpeed())
        send_notifs = GetNotifChoice()
        open_when_done = GetOpenWhenDoneChoice()
        if not audioonly:
            dotext = GetTextChoice()
        else:
            dotext = False
        if dotext:
            text1 = input(f"\n{strbold}{askcolour}Top text{strreset}\n> ")
            logging.info("text1: "+text1)
            text2 = input(f"\n{strbold}{askcolour}Bottom text{strreset}\n> ")
            logging.info("text2: "+text2)
        if GetAdvancedOptionsChoice():
            print(f"\n{errorcolour}{strbold}Warning: Changing these may result in errors and crashes.{strreset}")
            speed = int(GetSpeed())
            bitrate_multiplier = float(GetBitrateMultiplier())/100.0
            if audioonly:
                audiocontainer = GetAudioContainer()
                audio_codec = GetAudioCodec()
            else:
                container = GetVideoContainer()
                video_codec = GetVideoCodec()
            if not audioonly and not meme_mode:
                audioratio = float(GetAudioRatio())
                max_audio_bitrate = int(GetMaxAudioBitrate())
                max_res_size = int(GetMaxRes())
                target_fps = int(GetMaxFramerate())
                interpolate = GetInterpolateChoice()

    logging.info("trim: "+str(trim))
    logging.info("audioonly: "+str(audioonly))
    logging.info("mute: "+str(mute))
    logging.info("meme: "+str(meme_mode))
    logging.info("loud: "+str(loud))
    logging.info("reverb: "+str(reverb))
    logging.info("playbackspeed: "+str(playbackspeed))
    logging.info("notifs: "+str(send_notifs))
    logging.info("open filemgr: "+str(open_when_done))
    logging.info("text: "+str(dotext))
    logging.info("speed: "+str(speed))
    logging.info("bitratemulti: "+str(bitrate_multiplier))
    if audioonly:
        logging.info("audio container: "+str(audiocontainer))
        logging.info("audio codec: "+str(audio_codec))
    else:
        logging.info("video container: "+str(container))
        logging.info("video codec: "+str(video_codec))
    logging.info("audioratio: "+str(audioratio))
    logging.info("max audio bitrate: "+str(max_audio_bitrate))
    logging.info("max resolution: "+str(max_res_size))
    logging.info("target fps: "+str(target_fps))
    logging.info("interpolate: "+str(interpolate))

target_size = float(target_size)
clearscreen("Running...", strblue)

# determine ffmpeg preset based on speed
if speed != 0:
    speeds = ["placebo", "veryslow", "slower", "slow", "medium", "fast", "faster", "veryfast", "superfast", "ultrafast"]
    preset = " -preset "+speeds[speed-1]
    logging.info(f"preset: {speeds[speed-1]}")
else:
    preset = " "

originalsize = round(os.path.getsize(filein)/1000) # kB

if audioonly:
    container = audiocontainer

if loud:
    audiofilters = f"-af volume={volume_multiplier},acrusher=.1:1:{crunchiness}:0:log,bass=g={bass_multiplier} "
else:
    audiofilters = ""

# convert to correct format
splitfilein = filein.split(".")
fileincontain = splitfilein[len(splitfilein)-1]
filenocontain = filein[0:len(filein)-len(fileincontain)-1]
if fileincontain != container:
    logging.info("converting file to "+container+" with the following command")
    print(f"\n{strbold}{titlecolour}Converting to {othercolour}{container}{titlecolour}...{strreset}")
    if send_notifs:
        notif_convert.send()
    convert_filename = f"{tempdir}/conv_{launchtime}.{container}"
    convertcommand = f"{executable} -y -i \"{filein}\"{preset} \"{convert_filename}\""
    tempfiles.append(convert_filename)
    logging.info(convertcommand)
    os.system(convertcommand)
    filein = convert_filename

# bitrate (in Mbps) = Size / Length
# divide target size by length in seconds
targetSizeKB = target_size * bitrate_multiplier
logging.info("target size: "+str(targetSizeKB)+"KB")
lencmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{filein}\""
logging.info("fetching length with the following command")
logging.info(lencmd)
length = math.ceil(float(subprocess.getoutput(lencmd)))
logging.info(f"video length: {length}s")
totalbitrate=targetSizeKB*8/length

# trim
if trim:
    if send_notifs:
        notif_trim.send()
    if end_time == -1:
        end_time = length
    print(f"\n{strbold}{titlecolour}Trimming between {othercolour}{start_time}{titlecolour} and {othercolour}{end_time}{titlecolour}...{strreset}")
    print(f"{othercolour}(the progress bar may not fully complete){strreset}")
    trim_filename = f"{tempdir}/trim_{launchtime}.{container}"
    trimcommand = f"{executable} -y -i \"{filein}\" -ss {start_time} -to {end_time} \"{trim_filename}\""
    tempfiles.append(trim_filename)
    logging.info("trimming with the following command")
    logging.info(trimcommand)
    os.system(trimcommand)
    filein = trim_filename

# get sample rate
samplerate = 0
if not mute:
    getratecmd = f"ffprobe -v error -select_streams a -of default=noprint_wrappers=1:nokey=1 -show_entries stream=sample_rate \"{filein}\""
    logging.info("fetching sample rate with the following command")
    logging.info(getratecmd)
    samplerate = float(subprocess.getoutput(getratecmd))
    logging.info(f"audio is {samplerate}Hz")

# playback speed
if playbackspeed != 1.0:
    if send_notifs:
        notif_spd.send()
    print(f"\n{strbold}{titlecolour}Recoding at {othercolour}{playbackspeed}x{titlecolour} speed...{strreset}")
    print(f"{othercolour}(the progress bar may disappear or not fully complete){strreset}")
    spd_filename = f"{tempdir}/spd_{launchtime}.{container}"
    spdmult = 1.0/playbackspeed
    if audioonly:
        spdcommand = f"{executable} -y -i \"{filein}\" -filter:a \"asetrate={samplerate*playbackspeed},aresample={samplerate}\" \"{spd_filename}\""
    elif mute:
        spdcommand = f"{executable} -y -i \"{filein}\" -filter:v \"setpts={spdmult}*PTS\" \"{spd_filename}\""
    else:
        spdcommand = f"{executable} -y -i \"{filein}\" -filter_complex \"[0:v]setpts={spdmult}*PTS[v];[0:a]asetrate={samplerate*playbackspeed},aresample={samplerate}[a]\" -map \"[v]\" -map \"[a]\" \"{spd_filename}\""
    tempfiles.append(spd_filename)
    logging.info("changing speed with the following command")
    logging.info(spdcommand)
    os.system(spdcommand)
    filein = spd_filename
    length = math.ceil(length/playbackspeed)

# get fps
if not audioonly:
    if meme_mode:
        target_fps = 10
    fpscmd = f"ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate \"{filein}\""
    logging.info("fetching framerate with the following command")
    logging.info(fpscmd)
    fullfps = subprocess.getoutput(fpscmd).split("/")
    fps = float(int(fullfps[0])/int(fullfps[1]))
    logging.info(f"video is {fps}fps")
    lowerfps = fps > target_fps

# get resolution
doScale = False
if not audioonly:
    if meme_mode:
        max_res_size = 640
    rescmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 \"{filein}\""
    logging.info("fetching resolution with the following command")
    logging.info(rescmd)
    fullresolution = subprocess.getoutput(rescmd)
    logging.info("video is "+fullresolution)
    splitres = fullresolution.split("x")
    width = int(splitres[0])
    height = int(splitres[1])
    if width > height:
        orientation = 'l'
        logging.info("video is landscape")
    else:
        orientation = 'p'
        logging.info("video is portrait")
    if width > max_res_size or height > max_res_size:
        doScale = True
        logging.info("scaling will be needed")

# start interpolation
if interpolate and not audioonly and not meme_mode and fps*playbackspeed < float(target_fps):
    if doScale:
        if orientation == 'p':
            scale = max_res_size / height
            newres = str(round((width*scale)/2)*2)+":"+str(max_res_size)
        else:
            scale = max_res_size / width
            newres = str(max_res_size)+":"+str(round((height*scale)/2)*2)
        scalearg = f"scale={newres},"
    else:
        scalearg = ""
    if send_notifs:
        notif_interpolate.send()
    print(f"\n{strbold}{titlecolour}Interpolating...{strreset}")
    itpl_filename = f"{tempdir}/itpl_{launchtime}.{container}"
    itplcommand = f"{executable} -y -i \"{filein}\" -filter:v \"{scalearg}minterpolate='mi_mode=mci:mc_mode=obmc:fps={target_fps}'\" \"{itpl_filename}\""
    tempfiles.append(itpl_filename)
    logging.info("interpolating with the following command")
    logging.info(itplcommand)
    os.system(itplcommand)
    filein = itpl_filename

# figure out valid file name
fullname = targetfilename.split("/")
fullname = fullname[len(fullname)-1].split("\\")
name = fullname[len(fullname)-1].split(".")
if len(name) == 1:
    fileout = "output/"+name+suffix+"."+container
else:
    name.pop(len(name)-1)
    newname = ""
    for eachitem in name:
        newname+=eachitem
    fileout = "output/"+newname+suffix+"."+container

# add text if requested
if dotext:
    text1 = text1.replace("\"","\\\"")
    text1 = text1.replace("'","\\\'")
    text2 = text2.replace("\"","\\\"")
    text2 = text2.replace("'","\\\'")
    textheight = math.floor(width / text_devisor)
    text_filename = f"{tempdir}/txt_{launchtime}.{container}"
    textcmd = f"{executable} -y -i \"{filein}\" -filter_complex \"[0:v]pad=iw:ih+{textheight*2}:0:(oh-ih)/2:color=white,drawtext=text='{text1}':fontsize={math.floor(textheight*0.75)}:x=(w-tw)/2:y=({textheight}-th)/2,drawtext=text='{text2}':fontsize={math.floor(textheight*0.75)}:x=(w-tw)/2:y=h-{math.floor(textheight/2)}-(th/2)\"{preset} \"{text_filename}\""
    tempfiles.append(text_filename)
    logging.info("adding text with the following command:")
    logging.info(textcmd)
    print(f"\n{strbold}{titlecolour}Writing text...{strreset}")
    if send_notifs:
        notif_text.send()
    os.system(textcmd)
    filein = text_filename

if mute:
    print(f"\n{strbold}{titlecolour}Removing Audio...{strreset}")
    if send_notifs:
        notif_mute.send()
    mute_filename = f"{tempdir}/mute_{launchtime}.{container}"
    mutecmd = f"{executable} -y -i \"{filein}\" -an \"{mute_filename}\""
    tempfiles.append(mute_filename)
    logging.info("removing audio with the following command:")
    logging.info(mutecmd)
    os.system(mutecmd)
    filein = mute_filename
elif loud:
    print(f"\n{strbold}{titlecolour}Amplifying...{strreset}")
    if send_notifs:
        notif_amplify.send()
    amp_filename = f"{tempdir}/amp_{launchtime}.{container}"
    amplifycmd = f"{executable} -y -i \"{filein}\" {audiofilters}\"{amp_filename}\""
    tempfiles.append(amp_filename)
    logging.info("amplifying with the following command:")
    logging.info(amplifycmd)
    os.system(amplifycmd)
    filein = amp_filename

if reverb and not mute:
    print(f"\n{strbold}{titlecolour}Adding reverb...{strreset}")
    if send_notifs:
        notif_reverb.send()
    rvb_filename = f"{tempdir}/rvb_{launchtime}.{container}"
    rvbcmd = f"{executable} -y -i \"{filein}\" -af aecho=1.0:0.3:35:1,bass=g=2 \"{rvb_filename}\""
    tempfiles.append(rvb_filename)
    logging.info("adding reverb with the following command:")
    logging.info(rvbcmd)
    os.system(rvbcmd)
    filein = rvb_filename

# calculate size: no need to shrink if file is already small enough
size=os.path.getsize(filein)/1000   # in kB
logging.info(f"size of input file: {size}kB (originally {originalsize}kB)")
if (size < targetSizeKB or targetSizeKB == 0) and not meme_mode:
    shutil.copy(filein, fileout)

    # delete temp files
    shutil.rmtree(tempdir)

    if countfiles("temp") == 0:
        os.rmdir("temp")

    clearscreen("Complete!", strgreen)

    if send_notifs:
        notif_smallenough.send()
    logging.info("file is already small enough")
    newdisplaysize=os.path.getsize(fileout)/1000 # in kB
    newkibisize=kibiconvert(newdisplaysize)
    logging.info(f"size of output file: {newdisplaysize}kB, or {newkibisize}kiB")
    expected = targetSizeKB
    if newdisplaysize > expected and expected != 0:
        logging.info("somehow, shrinkray went backwards.")
        logging.info(f"expected {expected}kB, got {newdisplaysize}kB.")
        print(f"\n{strbold}{errorcolour}Congratulations, it seems like you have broken shrinkray.")
        print(f"Something happened that shouldn't be possible.")
        print(f"Please open a GitHub issue, providing the latest log, so that I can fix this.")
        print(f"https://github.com/megabyte112/shrinkray/issues{strreset}")
        
        printsizes(originalsize, newdisplaysize)
    else:
        print(f"\n{strgreen}{strbold}Shrinking was not needed.{strreset}")
        printsizes(originalsize, newdisplaysize)
        print("Check the output folder for your file.")
        if open_when_done:
            showinfm.show_in_file_manager(fileout)
    logging.info("complete!")
    logging.shutdown()
    if wait_when_done:
        input(f"\nYou can now press {strbold}[Enter]{strunbold} or {strbold}close this window{strunbold} to exit.")
    sys.exit()

# split into audio and video
if audioonly:
    videobitrate = 0
    audiobitrate = totalbitrate
elif mute:
    audiobitrate = 0
    videobitrate = totalbitrate
else:
    audiobitrate=totalbitrate * audioratio
    if max_audio_bitrate is not None and audiobitrate > max_audio_bitrate:
        audiobitrate = max_audio_bitrate
    videobitrate=totalbitrate-audiobitrate

# ahh yes, crusty shitposts
if meme_mode:
    if loud:
        audiobitrate = 30
        videobitrate = 20
    else:
        audiobitrate = 10
        videobitrate = 20
    totalbitrate = audiobitrate + videobitrate

if videobitrate >= 1 and not audioonly:
    videobitrate = str(int(math.ceil(videobitrate))) + 'k'
elif videobitrate < 1 and not audioonly:
    videobitrate *= 1000
    videobitrate = str(math.ceil(videobitrate))

if audiobitrate >= 1 and not mute:
    audiobitrate = str(int(math.ceil(audiobitrate))) + 'k'
elif audiobitrate < 1 and not mute:
    audiobitrate *= 1000
    audiobitrate = str(math.ceil(audiobitrate))

totalbitrate = round(totalbitrate)

logging.info(f"audio bitrate: {audiobitrate}")
logging.info(f"video bitrate: {videobitrate}")
logging.info(f"total bitrate: {totalbitrate}kbps")

if audioonly:
    audioargs = f"-c:a {audio_codec} -b:a {audiobitrate} {audiofilters}"
    ffmpegcmd = f"{executable} -y -hide_banner -i \"{filein}\" {audioargs}\"{fileout}\""
    if send_notifs:
        notif_audiocompress.send()
    print(f"\n{strbold}{titlecolour}Shrinking...{strreset}")
    logging.info("audio shrinking using the following command")
    logging.info(ffmpegcmd)
    os.system(ffmpegcmd)
    logging.info("called command")
else:
    audioargs = f"-b:a {audiobitrate} "
    if mute:
        audioargs = "-an "
    if doScale:
        if lowerfps:
            fpsargs = ",fps="+str(target_fps)+" "
        else:
            fpsargs = " "
        if orientation == 'p':
            scale = max_res_size / height
            newres = str(round((width*scale)/2)*2)+":"+str(max_res_size)
        else:
            scale = max_res_size / width
            newres = str(max_res_size)+":"+str(round((height*scale)/2)*2)
        videoargs = f"-vf scale={newres}{fpsargs}-c:v {video_codec} -b:v {videobitrate}"
        if audioonly:
            videoargs = ""
        ffmpeg_commands = [f"{executable} -y -i \"{filein}\" {videoargs}{preset} -passlogfile {tempdir}/fflog{launchtime} -pass 1 -an -f null {nullfile}",
        f"{executable} -y -i \"{filein}\" {videoargs}{preset} -passlogfile {tempdir}/fflog{launchtime} {audioargs}-pass 2 \"{fileout}\""]
    else:
        if lowerfps:
            fpsargs = "-vf fps="+str(target_fps)+" "
        else:
            fpsargs = ""
        videoargs = f"{fpsargs}-c:v {video_codec} -b:v {videobitrate}"
        ffmpeg_commands = [f"{executable} -y -i \"{filein}\" {videoargs}{preset} -passlogfile {tempdir}/fflog{launchtime} -pass 1 -an -f null {nullfile}",
        f"{executable} -y -i \"{filein}\" {videoargs}{preset} -passlogfile {tempdir}/fflog{launchtime} {audioargs}-pass 2 \"{fileout}\""]

    logging.info("calling ffmpeg for two-pass, will now log commands")
    logging.info(ffmpeg_commands[0])
    if send_notifs:
        notif_twopass.send()
    print(f"\n{strbold}{titlecolour}Running {othercolour}pass 1{titlecolour}...{strreset}")
    os.system(ffmpeg_commands[0])
    logging.info(ffmpeg_commands[1])
    print(f"\n{strbold}{titlecolour}Running {othercolour}pass 2{titlecolour}...{strreset}")
    os.system(ffmpeg_commands[1])
    logging.info("called both commands")


# delete temp files
shutil.rmtree(tempdir)

if countfiles("temp") == 0:
    os.rmdir("temp")

# done!
clearscreen("Complete!", strgreen)
newdisplaysize=round(os.path.getsize(fileout)/1000) # in kB
newkibisize=kibiconvert(newdisplaysize)
logging.info(f"size of output file: {newdisplaysize}kB, or {newkibisize}kiB")
expected = target_size
failed = False
if newdisplaysize == 0:
    failed = True
    logging.warning("failed!")
    if send_notifs:
        notif_failed.send()
    print(f"\n{strred}{strbold}Shrinking failed!{strunbold} Try adjusting some settings.")
    print(f"If you can't fix it, tell megabyte112 or open a GitHub issue.")
    print(f"https://github.com/megabyte112/shrinkray/issues{strreset}")
elif newdisplaysize > expected and expected != 0:
    logging.info("file is larger than expected!")
    if send_notifs:
        notif_toobig.send()
    print(f"\n{strbold}{stryellow}It looks like shrinkray couldn't shrink your file as much as you requested.{strreset}")
    printsizes(originalsize, newdisplaysize)
    print(f"{stryellow}If you need it to be smaller, try lowering the target size and running shrinkray again.")
    print(f"The file was still saved.{strreset}")
else:
    logging.info("complete!")
    if send_notifs:
        notif_complete.send()
    print(f"\n{strbold}{strgreen}Shrinking complete!\nCheck the output folder for your file.{strreset}")
    printsizes(originalsize, newdisplaysize)
logging.shutdown()
if open_when_done and not failed:
    showinfm.show_in_file_manager(fileout)
if wait_when_done:
    input(f"\nYou can now press {strbold}[Enter]{strunbold} or {strbold}close this window{strunbold} to exit.")
sys.exit()
