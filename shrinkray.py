# shrinkray, by megabyte112
# https://github.com/megabyte112/shrinkray
# see LICENSE for license info

# ----------[~~Settings~~]---------- #

# Here you can find advanced settings for shrinkray.
# Lines prefixed with a hash (#) are comments and are ignored by the interpreter.
# All booleans (True/False) must have the first letter capitalized.

# ----[Colours]---- #
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

# usually highlighted parts of titles, like 'pass 1' or 'mp3'.
# default: "magenta"
othercol = "magenta"

# file size numbers once completed.
# default: "cyan"
numbercol = "cyan"

# file size units once completed.
# default: "yellow"
unitcol = "yellow"

# ----[General]---- #

# enable verbose mode, all logging info will be shown and the screen will not be cleared.
# this also removes the progress bar in favour of the default ffmpeg interface.
# default: False
verbose = False

# string appended to filenames.
# default: "_shrinkray"
filenameSuffix = "_sr"

# amount of allowed items in any of shrinkray's folders before showing a warning.
# these folders can eventually reach very large file sizes.
# set to None to disable.
# default: 100
warningThreshold = 100

# wait for enter key before closing.
# default: True
waitWhenDone = True

# ----[Defaults]---- #

# All of these are the default values for the options shown at runtime.

# download video/audio instead of using a local file.
# default: True
doDownload = True

# default target file size in kB.
# default: 8000
defaultSize = 8000

# don't include video, and store file in audio container.
# default: False
audioOnly = False

# trims the video between two timestamps by default.
# default: False
doTrim = False

# don't include audio.
# doesn't work when audioOnly is True.
# default: False
doMute = False

# ultra-high compression for those moldy shitposts.
# locks video bitrate to 20kbps, and audio bitrate to 10kbps.
# resolution is also smaller and FPS is capped at 10.
# default: False
memeMode = False

# makes the volume louder, and adds some bass.
# this is for those crunchy earrape memes.
# default: False
loudMode = False

# add a slight echo to audio.
# ffmpeg doesn't do a very good job of this, it might not sound like you expect.
# default: False
doReverb = False

# playback speed.
# default: 1.0
playbackSpeed = 1.0

# send desktop notifications by default when shrinkray completes.
# default: True
sendNotifs = True

# open in file manager by default when done.
# default: True
openInFileMgr = True

# add text to the top and bottom of videos.
# default: False
doText = False

# default shrinking speed, a number between 1 and 10, higher is faster.
# lower speeds lead to more accurate file sizes.
# set to 0 to disable ffmpeg speed presets.
# default: 5
encodingSpeed = 5

# amount of 'wiggle room': higher means more chance of file being too big.
# always keep this less than 1, or else your files will be too large.
# default: 0.95
bitrateMultiplier = 0.95

# container for video files.
# default: "mp4"
videoContainer = "mp4"

# video codec to use.
# default: "libx264"
videoCodec = "libx264"

# container for audio files.
# default: "mp3"
audioContainer = "mp3"

# audio codec to use when audioOnly is True.
# default: "libmp3lame"
audioCodec = "libmp3lame"

# fraction of bandwidth dedicated to audio.
# ignored when doMute or audioOnly is True.
# must be less than 1.
# default: 1/4
audioRatio = 1 / 4

# highest allowed audio bitrate (in kbps).
# ignored when audioOnly is True.
# set to None to disable.
# default: 256
maxAudioBitrate = 256

# maximum allowed size of the longest edge (in pixels) before scaling is needed.
# default: 1280
maxResSize = 1280

# framerate limit.
# this is also the framerate that the video can be interpolated to.
# default: 30
maxFramerate = 30

# interpolate frames if playback speed is changed or maxFramerate is higher than source video.
# this makes it look smoother, and is interpolated to target_fps.
# however, this is extremely slow.
# default: False
doInterpolation = False

# ------[Miscellaneous]------ #

# how many times smaller than the width the text padding is.
# higher is smaller.
# default: 10
textDivisor = 10

# amplification.
# only effective when loudMode is True.
# default: 5
volumeMultiplier = 5

# bass boost.
# only effective when loudMode is True.
# default: 2
bassMultiplier = 2

# how "crunchy" the audio should sound.
# only effective when loudMode is True.
# default: 64
crunchiness = 64

# -------[~~End of Settings~~]------- #

# Everything below this point is actual code.
# Only edit if you know exactly what you're doing.


# okay, let's do this.

# import standard libraries
import logging
import math
import os
import shutil
import subprocess
import sys
import time
import webbrowser

# get epoch time, this is used for logging filenames.
# aka seconds since Jan 1 1970 0:00:00.
# this allows multiple instances running at once.
launchTime = int(time.time())

# check folders, create them if they don't already exist
if not os.path.isdir("logs"):
    os.mkdir("logs")
if not os.path.isdir("output"):
    os.mkdir("output")
if not os.path.isdir("temp"):
    os.mkdir("temp")

tempdir = "temp/" + str(launchTime)
os.mkdir(tempdir)

# don't edit
version = "1.8"

# setup logger
logFormat = '%(asctime)s: %(message)s'
logging.basicConfig(filename=f"logs/shrinkray_{launchTime}.log", filemode="w", level=logging.INFO, format=logFormat)

# show logger in console if using verbose mode
if verbose:
    logging.getLogger().addHandler(logging.StreamHandler())

logging.info("starting")

# determine host OS
if os.name == "nt":  # windows
    logging.info("host is Windows")
    nullFile = "NUL"
    clearCommand = "cls"
else:  # posix
    logging.info("host is non-Windows")
    nullFile = "/dev/null"
    clearCommand = "clear"


# early clear function which requires no dependencies, unlike the other
def earlyclear():
    global clearCommand, version
    os.system(clearCommand)
    print(f"shrinkray {version} | Setup\n")


# check non-standard dependencies
try:
    import ffpb
    import yt_dlp
    import notifypy
    import showinfm
    import colorama

    logging.info("deps already installed")
except ImportError:
    # time to install deps
    earlyclear()
    logging.info("installing deps")
    print("\nInstalling dependencies, you may see some warnings.\n")
    import pip

    pip.main(["install", "--quiet",

              "ffpb",
              "yt-dlp",
              "notify-py",
              "show-in-file-manager",
              "colorama",

              "--exists-action", "i"])

    import ffpb
    import yt_dlp
    import notifypy
    import showinfm
    import colorama

    earlyclear()
    logging.info("done deps, closing")
    print("\nDependencies have been installed,\nPlease restart shrinkray.")
    if waitWhenDone:
        input("\nPress Enter to close.")
    sys.exit()

# check for ffmpeg
if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
    earlyclear()
    print("\nIt seems like FFMPEG isn't installed, or isn't in your system path.")
    print("Refer to shrinkray's guide for more info.")
    print("https://github.com/megabyte112/shrinkray/wiki/shrinkray-wiki")
    if waitWhenDone:
        input("\nWhen you're done, reopen shrinkray, and you're all set.")
    sys.exit()

arg_length = len(sys.argv)

if verbose:
    executable = "ffmpeg"
else:
    executable = "ffpb"

tempFiles = []

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


def getcolourfromtext(text):
    if text == "red":
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


titlecolour = getcolourfromtext(titlecol)
askcolour = getcolourfromtext(inputcol)
errorcolour = getcolourfromtext(warningcol)
othercolour = getcolourfromtext(othercol)
numbercolour = getcolourfromtext(numbercol)
unitcolour = getcolourfromtext(unitcol)


# define clear function
def clearscreen(stage, color):
    global clearCommand, version, verbose
    if verbose:
        return
    os.system(clearCommand)
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
logging.info("wait when done: " + str(waitWhenDone))
logging.info("count threshold: " + str(warningThreshold))

logging.info("initialization complete")

# we're running!!
print(f"\n{titlecolour}Welcome back to {strbold}shrinkray{strreset}.")

logging.info(f"shrinkray {version} is running!")
logging.info("tell megabyte112 about any issues :)")

if memeMode:
    print(f"\n{strbold}{errorcolour}haha shitpost shrinkray go brrrrrrrrr")
    print(f"(meme mode is active by default){strreset}")
if audioOnly:
    print(f"\n{strbold}{errorcolour}WARNING: Output will be audio only by default!{strreset}")
elif doMute:
    print(f"\n{strbold}{errorcolour}WARNING: Video will be muted by default!{strreset}")
if loudMode and not doMute:
    print(f"\n{strbold}{errorcolour}i hope your ears are okay")
    print(f"(loudMode mode enabled by default){strreset}")

if warningThreshold is not None:
    sizewarned = False
    if log_count >= warningThreshold:
        sizewarned = True
        print(f"\n{errorcolour}Logs folder contains {log_count} items!")
        print(f"Consider clearing it once shrinkray is closed.{strreset}")
    if out_count >= warningThreshold:
        sizewarned = True
        print(f"\n{errorcolour}Output folder contains {out_count} items!")
        print(f"Consider clearing it once shrinkray is closed.{strreset}")

    if sizewarned:
        print(f"\n{errorcolour}You can disable these folder warnings in the settings.{strreset}")


def kibiconvert(value):
    return value * 0.9765625


def mebiconvert(value):
    return round(kibiconvert(value) * 100 / 1024) / 100


def printsizes(size1, size2):
    print()
    print(f"{titlecolour}before:")
    print(
        f"    {numbercolour}{round(size1)}{unitcolour}kB{strwhite}, "
        f"{numbercolour}{round(kibiconvert(size1))}{unitcolour}kiB")
    print(
        f"    {numbercolour}{round(size1 / 10) / 100}{unitcolour}MB{strwhite}, "
        f"{numbercolour}{mebiconvert(size1)}{unitcolour}MiB")
    print()
    print(f"{strbold}{titlecolour}after:")
    print(
        f"    {numbercolour}{round(size2)}{unitcolour}kB{strwhite}, "
        f"{numbercolour}{round(kibiconvert(size2))}{unitcolour}kiB")
    print(
        f"    {numbercolour}{round(size2 / 10) / 100}{unitcolour}MB{strwhite}, "
        f"{numbercolour}{mebiconvert(size2)}{unitcolour}MiB")
    print(strreset)
    shrinkness = round((size2 / size1) * 1000) / 1000
    print(f"{titlecolour}{strbold}File is {othercolour}{shrinkness}x{titlecolour} the original size.{strreset}")
    print()


def validsizeinput(text):
    if 'k' in text:
        text = text[0:len(text) - 1]
    return text.isnumeric() and int(text) >= 0


def validinput(text):
    return text.isnumeric() and int(text) > 0


def validspeedinput(text):
    return text.isnumeric() and 0 <= int(text) <= 10


def validmultiinput(text):
    return text.isnumeric() and 0 < int(text) <= 100


def validratioinput(text):
    text = text.split("/")
    return len(text) == 2 and text[0].isnumeric() and text[1].isnumeric() and int(text[0]) < int(text[1])


def moreoptionschoice():
    text = input(f"\n{strbold}{askcolour}More options?{strreset} [Y/N]\n> ")
    return text.lower() == "y"


def advancedoptionschoice():
    text = input(f"\n{strbold}{askcolour}Advanced options?{strreset} [Y/N]\n> ")
    return text.lower() == "y"


# ask for target file size
def gettargetsize():
    text = "abc"
    while not validsizeinput(text):
        text = input(
            f"\n{strbold}{askcolour}Target file size in MB {strreset}[add k for kB, or enter 0 for no limit]\n> ")
        if text == "":
            return defaultSize
        if not validsizeinput(text):
            logging.warning("rejected input: " + str(text))
            print(f"\n{errorcolour}Make sure your input a whole number!{strreset}")
        if 'k' in text:
            return text[0:len(text) - 1]
    return text + "000"


def getbitratemulti():
    global bitrateMultiplier
    text = "abc"
    while not validmultiinput(text):
        text = input(f"\n{strbold}{askcolour}Bitrate multiplier {strreset}[as percentage, like 95]\n> ")
        if text == "":
            return bitrateMultiplier * 100.0
        if not validmultiinput(text):
            logging.warning("rejected input: " + str(text))
            print(f"\n{errorcolour}Make sure your input a whole number!{strreset}")
    return text


def getaudioratio():
    text = "0"
    while not validratioinput(text):
        text = input(f"\n{strbold}{askcolour}Audio ratio {strreset}[as bottom-heavy fraction of two ints: x/y]\n> ")
        if text == "":
            return audioRatio
        if not validratioinput(text):
            logging.warning("rejected input: " + str(text))
            print(f"\n{errorcolour}Make sure your input a bottom-heavy fraction of two integers, like 1/4.{strreset}")
    text = text.split("/")
    return float(text[0]) / float(text[1])


# ask for speed
def getencodingspeed():
    text = "123"
    while not validspeedinput(text):
        text = input(f"\n{strbold}{askcolour}Encoding speed{strreset} [1-10]\n> ")
        if text == "":
            return encodingSpeed
        if not validspeedinput(text):
            logging.warning("rejected input: " + str(text))
            print(f"\n{errorcolour}Make sure your input a whole number between 1 and 10{strreset}")
    return text


def getaudiocontainer():
    global audioContainer
    text = input(f"\n{strbold}{askcolour}Audio container{strreset}\n> ")
    if text == "":
        return audioContainer
    else:
        return text


def getaudiocodec():
    global audioCodec
    text = input(f"\n{strbold}{askcolour}Audio codec{strreset}\n> ")
    if text == "":
        return audioCodec
    else:
        return text


def getvideocontainer():
    global videoContainer
    text = input(f"\n{strbold}{askcolour}Video container{strreset}\n> ")
    if text == "":
        return videoContainer
    else:
        return text


def getvideocodec():
    global videoCodec
    text = input(f"\n{strbold}{askcolour}Video codec{strreset}\n> ")
    if text == "":
        return videoCodec
    else:
        return text


def getmaxaudiobitrate():
    global maxAudioBitrate
    text = "0"
    while not validinput(text):
        text = input(f"\n{strbold}{askcolour}Max audio bitrate {strreset}[in kbps]\n> ")
        if text == "":
            return maxAudioBitrate
        if not validinput(text):
            logging.warning("rejected input: " + str(text))
            print(f"\n{errorcolour}Make sure your input is a whole number greater than 0.{strreset}")
    return text


def getmaxres():
    global maxResSize
    text = "0"
    while not validinput(text):
        text = input(f"\n{strbold}{askcolour}Max resolution {strreset}[in pixels, longest edge]\n> ")
        if text == "":
            return maxResSize
        if not validinput(text):
            logging.warning("rejected input: " + str(text))
            print(f"\n{errorcolour}Make sure your input is a single whole number greater than 0.{strreset}")
    return text


def getmaxfps():
    global maxFramerate
    text = "0"
    while not validinput(text):
        text = input(f"\n{strbold}{askcolour}Max framerate {strreset}[in fps]\n> ")
        if text == "":
            return maxFramerate
        if not validinput(text):
            logging.warning("rejected input: " + str(text))
            print(f"\n{errorcolour}Make sure your input is a whole number greater than 0.{strreset}")
    return text


def gettrimchoice():
    global doTrim
    text = input(f"\n{strbold}{askcolour}Trim video?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return doTrim


def getreverbchoice():
    global doReverb
    text = input(f"\n{strbold}{askcolour}Reverb audio?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return doReverb


def getinterpolatechoice():
    global doInterpolation
    text = input(f"\n{strbold}{askcolour}Interpolate video?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return doInterpolation


def validspeedfloat(text):
    try:
        a = float(text)
    except ValueError:
        return False
    if 0.5 <= a <= 2.0:
        return True
    return False


def getplaybackspeed():
    global playbackSpeed
    text = "abc"
    while not validspeedfloat(text):
        text = input(f"\n{strbold}{askcolour}Playback speed {strreset}[normal speed = 1]\n> ")
        if text == "":
            return playbackSpeed
        if not validspeedfloat(text):
            logging.warning("rejected input: " + str(text))
            print(f"\n{errorcolour}Make sure your input is a decimal number between 0.5 and 2.0.{strreset}")
    return text


def getopenchoice():
    global openInFileMgr
    text = input(f"\n{strbold}{askcolour}Open file manager when completed?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return openInFileMgr


def getaudiochoice():
    global audioOnly
    text = input(f"\n{strbold}{askcolour}Get audio only?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return audioOnly


def getnotifchoice():
    global sendNotifs
    text = input(f"\n{strbold}{askcolour}Send notifications?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return sendNotifs


def getmemechoice():
    global memeMode
    text = input(f"\n{strbold}{askcolour}Meme mode?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return memeMode


def getloudchoice():
    global loudMode
    text = input(f"\n{strbold}{askcolour}Loud mode?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return loudMode


def gettextchoice():
    global doText
    text = input(f"\n{strbold}{askcolour}Add text?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return doText


def getmutechoice():
    global doMute
    text = input(f"\n{strbold}{askcolour}Mute audio?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return doMute


def getdownloadchoice():
    global doDownload
    text = input(f"\n{strbold}{askcolour}Download media?{strreset} [Y/N]\n> ")
    if text.lower() == "n":
        return False
    elif text.lower() == "y":
        return True
    return doDownload


music_sites = [
    "music.youtube.com",
    "bandcamp.com",
    "soundcloud.com",
    "spotify.com",
    "deezer.com"
]

start_time = 0
end_time = -1
text1 = ""
text2 = ""


def ismusicsite(urlinput):
    return any(website in urlinput for website in music_sites)


# check if the url actually leads to media
def checkvideo(link):
    print(f"\n{titlecolour}Fetching...{strreset}")
    titlecommand = "yt-dlp -e --no-playlist --no-warnings " + link
    logging.info("fetching title with the following command")
    logging.info(titlecommand)
    process = subprocess.getstatusoutput(titlecommand)
    if process[0] != 0:
        logging.info("title grab failed with return code " + str(process[0]))
        print(
            f"{errorcolour}There was an issue with your video URL.{strreset}")
        return None
    title = process[1].replace("\"", "'")
    title = title.replace("/", "#")
    logging.info("title: " + str(title))
    print(f"{strgreen}Found - {strbold}{othercolour}\"{title}\"{strreset}")
    return title


# check whether the file is valid
def checkfile(file):
    if not os.path.isfile(file):
        print(f"\n{errorcolour}File doesn't exist.{strreset}")
        return False
    return True


# download a video
def download(self):
    clearscreen("Downloading...", strpurple)
    link = self.Source
    # find filename
    if self.DoAudioOnly:
        filename_command = "yt-dlp --get-filename -x -o \"%(title)s.%(ext)s\" --no-playlist --no-warnings " + link
    else:
        filename_command = "yt-dlp --get-filename -o \"%(title)s.%(ext)s\" --no-playlist --no-warnings " + link

    logging.info("fetching filename with the following command")
    logging.info(filename_command)
    filename = subprocess.getoutput(filename_command)
    logging.info("filename: " + filename)
    splitfile = filename.split(".")
    extension = splitfile[len(splitfile) - 1]
    logging.info("extension: " + extension)
    dlname = f"{tempdir}/dl_{launchTime}.{extension}"
    link = link.replace("\"", "\\\"")
    if verbose:
        dlcommand = f"yt-dlp \"{link}\" -v --no-playlist -o \"{dlname}\""
    else:
        dlcommand = f"yt-dlp \"{link}\" --quiet --progress --no-playlist --no-warnings -o \"{dlname}\""
    print(f"\n{titlecolour}Downloading...{strreset}")
    logging.info("downloading with the following command")
    logging.info(dlcommand)
    os.system(dlcommand)
    return [tempdir + "/" + os.listdir(tempdir)[0], filename]


def getlength(inputfile):
    lencmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{inputfile}\""
    logging.info("fetching length with the following command")
    logging.info(lencmd)
    length = math.ceil(float(subprocess.getoutput(lencmd)))
    logging.info(f"video length: {length}s")
    return length


# bitrate (in Mbps) = Size / Length
# divide target size by length in seconds
def getbitrate(targetsize, length, bitmult):
    targetSizeKB = targetsize * bitmult
    logging.info("target size: " + str(targetSizeKB) + "KB")
    totalbitrate = targetSizeKB * 8 / length
    return totalbitrate


# get sample rate
def getsamplerate(inputfile):
    if not doMute:
        getratecmd = f"ffprobe -v error -select_streams a -of default=noprint_wrappers=1:nokey=1 -show_entries " \
                     f"stream=sample_rate \"{inputfile}\" "
        logging.info("fetching sample rate with the following command")
        logging.info(getratecmd)
        samplerate = float(subprocess.getoutput(getratecmd))
        logging.info(f"audio is {samplerate}Hz")
    else:
        samplerate = 0
    return samplerate


# get resolution
def getresolution(inputfile):
    if not audioOnly:
        rescmd = f"ffprobe -v error -select_streams v:0 " \
                 f"-show_entries stream=width,height -of csv=s=x:p=0 \"{inputfile}\""
        logging.info("fetching resolution with the following command")
        logging.info(rescmd)
        fullresolution = subprocess.getoutput(rescmd)
        logging.info("video is " + fullresolution)
        splitres = fullresolution.split("x")
        width = int(splitres[0])
        height = int(splitres[1])
        if width > height:
            orientation = 'l'
            logging.info("video is landscape")
        else:
            orientation = 'p'
            logging.info("video is portrait")
    else:
        orientation = "n"
        height = 0
        width = 0
    return [width, height, orientation]


# get fps
def getfps(inputfile):
    if not audioOnly:
        fpscmd = f"ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries " \
                 f"stream=r_frame_rate \"{inputfile}\" "
        logging.info("fetching framerate with the following command")
        logging.info(fpscmd)
        fullfps = subprocess.getoutput(fpscmd).split("/")
        fps = float(int(fullfps[0]) / int(fullfps[1]))
        logging.info(f"video is {fps}fps")
        return fps
    else:
        return 0


# figure out valid file name
def getfilename(inputfile, container):
    fullname = inputfile.split("/")
    fullname = fullname[len(fullname) - 1].split("\\")
    name = fullname[len(fullname) - 1].split(".")
    if len(name) == 1:
        fileout = "output/" + name[0] + filenameSuffix + "." + container
    else:
        name.pop(len(name) - 1)
        newname = ""
        for eachitem in name:
            newname += eachitem
        fileout = "output/" + newname + filenameSuffix + "." + container
    return fileout


class ShrinkTask:
    def __init__(self):
        logging.info("initialising new shrink task")

        # woah, that's a lotta variables
        self.Length = 0
        self.Bitrate = 0.0
        self.VideoBitrate = 0.0
        self.AudioBitrate = 0.0
        self.ProtoFileName = ""
        self.Orientation = ""
        self.Height = 0
        self.Width = 0
        self.SplitResolution = [0, 0]
        self.LowerFps = False
        self.FrameRate = 30
        self.SampleRate = 48000
        self.OriginalSize = 0
        self.Args = []
        self.Filters = [[], []]
        self.InputFileName = ""
        self.IsMusic = False
        self.DoTrim = doTrim
        self.DoMute = doMute
        self.DoMeme = memeMode
        self.DoLoud = loudMode
        self.DoReverb = doReverb
        self.PlaybackSpeed = playbackSpeed
        self.DoText = doText
        self.EncodingSpeed = encodingSpeed
        self.BitrateMultiplier = bitrateMultiplier
        self.AudioContainer = audioContainer
        self.AudioCodec = audioCodec
        self.VideoContainer = videoContainer
        self.VideoCodec = videoCodec
        self.AudioRatio = audioRatio
        self.MaxAudioBitrate = maxAudioBitrate
        self.MaxResSize = maxResSize
        self.MaxFramerate = maxFramerate
        self.DoInterpolation = doInterpolation
        self.StartTime = start_time
        self.EndTime = end_time
        self.Text1 = text1
        self.Text2 = text2

        self.DoDownload = getdownloadchoice()

        # get media download info
        if self.DoDownload:
            validvideo = False
            while not validvideo:
                self.Source = input(f"\n{strbold}{askcolour}Paste a video link.{strreset}\n> ")
                logging.info(f"input: \"{self.Source}\"")
                self.Title = checkvideo(self.Source)
                if self.Title is not None:
                    validvideo = True
                    if "never gonna give you up" in self.Title.lower() or "rickroll" in self.Title.lower():
                        webbrowser.open("https://youtu.be/dQw4w9WgXcQ")     # easter egg
                        print(f"\n{othercolour}{strbold}you rickroll me, i rickroll you{strreset}")
            self.IsMusic = ismusicsite(self.Source)
            if self.IsMusic:
                logging.info("links to audio site")
                print(f"\n{othercolour}This URL links to a music site, your download will be audio-only.{strreset}")

        # or ask for file location and validate it
        else:
            logging.info("prepare file...")
            validfile = False
            while not validfile:
                self.Source = input(f"\n{strbold}{askcolour}Paste a file path.{strreset}\n> ")
                logging.info(f"input: \"{self.Source}\"")
                self.Title = os.path.basename(self.Source)
                if checkfile(self.Source):
                    validfile = True

        self.TargetSize = int(gettargetsize())

        if self.DoDownload and self.IsMusic:
            self.DoAudioOnly = True
            self.VideoContainer = self.AudioContainer
            self.VideoCodec = self.AudioCodec
        else:
            self.DoAudioOnly = getaudiochoice()

        if moreoptionschoice():
            self.DoTrim = gettrimchoice()
            if self.DoTrim:
                self.StartTime = input(f"\n{strbold}{askcolour}Start time {strreset}[hh:mm:ss] / [m:ss] / [s]\n> ")
                self.EndTime = input(f"\n{strbold}{askcolour}End time {strreset}[hh:mm:ss] / [m:ss] / [s]\n> ")
                if self.StartTime == "":
                    self.StartTime = 0
                if self.EndTime == "":
                    self.EndTime = -1
                logging.info(f"time range between {self.StartTime} and {self.EndTime}")

            if not self.DoAudioOnly:
                self.DoMute = getmutechoice()

            self.DoMeme = getmemechoice()

            if not self.DoMute:
                self.DoLoud = getloudchoice()

            self.DoReverb = getreverbchoice()

            self.PlaybackSpeed = float(getplaybackspeed())

            if not self.DoAudioOnly:
                self.DoText = gettextchoice()
            else:
                self.DoText = False
            if self.DoText:
                self.Text1 = input(f"\n{strbold}{askcolour}Top text{strreset}\n> ")
                logging.info("text1: " + self.Text1)
                self.Text2 = input(f"\n{strbold}{askcolour}Bottom text{strreset}\n> ")
                logging.info("text2: " + self.Text2)

            if advancedoptionschoice():
                print(f"\n{errorcolour}{strbold}Warning: Changing these may result in errors and crashes.{strreset}")

                self.EncodingSpeed = int(getencodingspeed())

                self.BitrateMultiplier = float(getbitratemulti()) / 100.0

                if self.DoAudioOnly:
                    self.AudioContainer = getaudiocontainer()
                    self.AudioCodec = getaudiocodec()
                else:
                    self.VideoContainer = getvideocontainer()
                    self.VideoCodec = getvideocodec()

                if not self.DoAudioOnly and not self.DoMeme:

                    self.AudioRatio = float(getaudioratio())

                    self.MaxAudioBitrate = int(getmaxaudiobitrate())

                    self.MaxResSize = int(getmaxres())

                    self.MaxFramerate = int(getmaxfps())

                    self.DoInterpolation = getinterpolatechoice()

        if self.DoAudioOnly and self.DoMute:
            self.DoMute = False

        # log everything
        logging.info("source: " + self.Source)
        logging.info("doDownload: " + str(self.DoDownload))
        logging.info("doTrim: " + str(self.DoTrim))
        logging.info("audioOnly: " + str(self.DoAudioOnly))
        logging.info("doMute: " + str(self.DoMute))
        logging.info("meme: " + str(self.DoMeme))
        logging.info("loudMode: " + str(self.DoLoud))
        logging.info("doReverb: " + str(self.DoReverb))
        logging.info("playbackSpeed: " + str(self.PlaybackSpeed))
        logging.info("text: " + str(self.DoText))
        logging.info("speed: " + str(self.EncodingSpeed))
        logging.info("bitratemulti: " + str(self.BitrateMultiplier))
        logging.info("container: " + str(self.VideoContainer))
        logging.info("codec: " + str(self.VideoCodec))
        logging.info("audioRatio: " + str(self.AudioRatio))
        logging.info("maxaudiorate: " + str(self.MaxAudioBitrate))
        logging.info("maxres: " + str(self.MaxResSize))
        logging.info("maxfps: " + str(self.MaxFramerate))
        logging.info("doInterpolation: " + str(self.DoInterpolation))

    def shrink(self):
        logging.info("shrink started")

        if self.DoDownload:
            splitfilenames = download(self)
            self.InputFileName = splitfilenames[0]
            self.ProtoFileName = splitfilenames[1]
        else:
            self.InputFileName = self.Source

        # let's go
        clearscreen("Running...", strblue)

        # determine ffmpeg preset based on speed
        if encodingSpeed != 0:
            speeds = ["placebo", "veryslow", "slower", "slow", "medium",
                      "fast", "faster", "veryfast", "superfast", "ultrafast"]
            self.Args.append("-preset " + speeds[encodingSpeed - 1])
            logging.info(f"preset: {speeds[encodingSpeed - 1]}")

        self.OriginalSize = os.path.getsize(self.InputFileName) / 1000  # in KB
        self.Length = getlength(self.InputFileName)
        self.Bitrate = getbitrate(self.InputFileName, self.Length, self.BitrateMultiplier)
        self.SampleRate = getsamplerate(self.InputFileName)
        self.SplitResolution = getresolution(self.InputFileName)
        self.Width = self.SplitResolution[0]
        self.Height = self.SplitResolution[1]
        self.Orientation = self.SplitResolution[2]
        self.FrameRate = getfps(self.InputFileName)

        # check loud or reverb
        if self.DoLoud:
            self.Args[1].append(f"volume={volumeMultiplier}")
            self.Args[1].append(f"acrusher=.1:1:{crunchiness}:0:log")
            self.Args[1].append(f"bass=g={bassMultiplier}")
        elif self.DoReverb:
            self.Args[1].append(f"aecho=1.0:0.3:35:1,bass=g=2")

        # check for meme mode
        if self.DoMeme:
            self.MaxResSize = 640
            self.MaxFramerate = 10

        # check for framerate and interpolation
        if self.DoInterpolation:
            self.Args[0].append(f"minterpolate='mi_mode=mci:mc_mode=obmc:fps={self.MaxFramerate}'")
        elif self.FrameRate < self.MaxFramerate:
            self.Args[0].append("fps=" + str(self.MaxFramerate))

        # check for resolution
        if self.Width > self.MaxResSize or self.Height > self.MaxResSize:
            if self.Orientation == "l":
                self.Args[0].append(f"scale={self.MaxResSize}:-1")
            else:
                self.Args[0].append(f"scale=-1:{self.MaxResSize}")

        # figure out bitrates for audio and video
        if self.DoAudioOnly:
            self.VideoBitrate = 0
            self.AudioBitrate = self.Bitrate
        elif self.DoMute:
            self.VideoBitrate = self.Bitrate
            self.AudioBitrate = 0
        elif self.DoMeme:
            self.AudioBitrate = 10
            self.VideoBitrate = 10
            self.Bitrate = self.AudioBitrate + self.VideoBitrate
        else:
            self.AudioBitrate = self.Bitrate * self.AudioRatio
            if self.MaxAudioBitrate is not None and self.AudioBitrate > self.MaxAudioBitrate:
                self.AudioBitrate = self.MaxAudioBitrate
            self.VideoBitrate = self.Bitrate - self.AudioBitrate

        # if each birtate is greater than 1, append "k" for kilobits
        if self.VideoBitrate >= 1 and not self.DoAudioOnly:
            self.VideoBitrate = str(int(math.ceil(self.VideoBitrate))) + "k"
        elif self.VideoBitrate < 1 and not self.DoAudioOnly:
            self.VideoBitrate *= 1000
            self.VideoBitrate = str(int(math.ceil(self.VideoBitrate)))
        if self.AudioBitrate >= 1 and not self.DoMute:
            self.AudioBitrate = str(int(math.ceil(self.AudioBitrate))) + "k"
        elif self.AudioBitrate < 1 and not self.DoMute:
            self.AudioBitrate *= 1000
            self.AudioBitrate = str(int(math.ceil(self.AudioBitrate)))
        self.Bitrate = round(self.Bitrate)

        logging.info(f"audio bitrate: {self.AudioBitrate}")
        logging.info(f"video bitrate: {self.VideoBitrate}")
        logging.info(f"total bitrate: {self.Bitrate}kbps")

        # calculate args
        self.Args = [executable, "-y", "-i", self.InputFileName]
        if self.DoTrim:
            if self.EndTime == -1:
                self.EndTime = self.Length
            self.Args.append(f"-ss {self.StartTime * (1/self.PlaybackSpeed)}")
            self.Args.append(f"-to {self.EndTime * (1/self.PlaybackSpeed)}")

        if self.Filters[0] is not None and self.Filters[1] is not None:
            self.Args.append(f"-filter_complex [0:v]{','.join(self.Args[0])}[v];[0:a]{','.join(self.Args[1])}[a]")
            self.Args.append("-map '[v]' -map '[a]'")
        elif self.Filters[1] is not None:
            self.Args.append("-filter:a " + ",".join(self.Filters[1]))
        elif self.Filters[0] is not None:
            self.Args.append("-filter:v " + ",".join(self.Filters[0]))

        if not self.DoAudioOnly:
            self.Args.append("-b:v " + self.VideoBitrate)

        if self.DoMute:
            self.Args.append("-an")
        else:
            self.Args.append("-b:a " + self.AudioBitrate)


shrink = ShrinkTask()
shrink.shrink()


# MUTE
# SHRINK

# we have everything, let's do this!!
if not doMute and not audioOnly:
    args = [executable, "-y", "-i", filein, "-filter_complex",
            "[0:v]"+",".join(videoFilters)+"[v];[0:a]"+",".join(audioFilters)+"[a]", "-map", "'[v]'",
            "-map", "'[a]'", "-b:v", videobitrate, "-b:a", audiobitrate, fileout]


# delete temp files
shutil.rmtree(tempdir)

if countfiles("temp") == 0:
    os.rmdir("temp")

# done!
clearscreen("Complete!", strgreen)
newdisplaysize = round(os.path.getsize(fileout) / 1000)  # in kB
newkibisize = kibiconvert(newdisplaysize)
logging.info(f"size of output file: {newdisplaysize}kB, or {newkibisize}kiB")
expected = target_size
failed = False
if newdisplaysize == 0:
    failed = True
    logging.warning("failed!")
    if sendNotifs:
        notif_failed.send()
    print(f"\n{strred}{strbold}Shrinking failed!{strunbold} Try adjusting some settings.")
    print(f"If you can't fix it, tell megabyte112 or open a GitHub issue.")
    print(f"https://github.com/megabyte112/shrinkray/issues{strreset}")
elif newdisplaysize > expected != 0:
    logging.info("file is larger than expected!")
    if sendNotifs:
        notif_toobig.send()
    print(
        f"\n{strbold}{stryellow}It looks like shrinkray couldn't shrink your file as much as you requested.{strreset}")
    printsizes(originalsize, newdisplaysize)
    print(f"{stryellow}If you need it to be smaller, try lowering the target size and running shrinkray again.")
    print(f"The file was still saved.{strreset}")
else:
    logging.info("complete!")
    if sendNotifs:
        notif_complete.send()
    print(f"\n{strbold}{strgreen}Shrinking complete!\nCheck the output folder for your file.{strreset}")
    printsizes(originalsize, newdisplaysize)
logging.shutdown()
if openInFileMgr and not failed:
    showinfm.show_in_file_manager(fileout)
if waitWhenDone:
    input(f"\nYou can now press {strbold}[Enter]{strunbold} or {strbold}close this window{strunbold} to exit.")
sys.exit()
