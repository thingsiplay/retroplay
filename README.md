% README RETROPLAY

# retroplay for RetroArch

RetroArch run script and playlist extractor on Linux

- **Author**: Tuncay D.
- **License**: [MIT License](LICENSE)
- **Source**: [Github source](https://github.com/thingsiplay/retroplay)

```
            __                __
   _______ / /________  ___  / /__ ___ __
  / __/ -_) __/ __/ _ \/ _ \/ / _ `/ // /
 /_/  \__/\__/_/  \___/ .__/_/\_,_/\_, /
                     /_/          /___/
```

## Introduction

**retroplay** is based on the [emulate](https://github.com/thingsiplay/emulate)
Bash script, but rewritten and enhanced in Python *3.9* for Linux.  It is a
wrapper around [RetroArch](https://www.retroarch.com/) to help running games
via commandline.  This functionality can be used to configure your system to
launch games from RetroArch directly within your file manager by (double)
clicking the ROM files.  The RetroArch GUI is not required to open.  Variety of
options are supported and is designed to run from commandline too.

### Features

- run games with a RetroArch core without opening the RetroArch GUI, in example
  by double clicking the file in your favorit graphical file manager
- play games from RetroArch playlist, in example from the *history*
- filter and sort any playlist before autoselect the first entry
- use *dmenu* or *rofi* to select a game to run
- or do not play a game, but output a list of all ROM files found through the
  options
- play romhacks without creating a permanent patched ROM in a relative safely
  manner
- record video output from your play session

### Quick Start

1. Install and configure RetroArch first, if not done already:
   [RetroArch](https://www.retroarch.com/)
2. Download **retroplay**.  If you have at least Python version *3.9*, then get
   the archive with **-Python** in the filename or otherwise get the archive
   with **-Linux-64Bit** for binary version:
   [Releases](https://github.com/thingsiplay/retroplay/releases)
3. Optionally install it in a directory within *$PATH*.  The default
   *install.sh* script that comes with the archive does it.
4. Optionally register filetype of ROM extensions to this program.
5. Configure the default settings file at
   *$HOME/.config/retroplay/settings.ini* to your needs (for extension and core
   rules).  A default configuration will be generated if **retroplay** is run
   at least once.
6. Read the manpage, if installed: `man retroplay` or the HTML version
   */usr/local/doc/retroplay/MAN.html*

## Usage

There are two common ways to use this program: 1. Implicit through file
extension registering to the program and 2. explicitly running the program from
commandline or in a script.

### File extension registering

If you want to run the ROM file from your favorite file manager without opening
the RetroArch GUI, then register the file extension for the type of ROM to this
program.  Then a double click on the file is enough to run it.

To associate the file extension to the script/program, right mouse click on the
ROM file, select "open with..." and choose **retroplay**.  The default
installation location is */usr/local/bin*, if not altered.  From now on, you
should be able to play the games by double clicking the files in your favorite
graphical file manager.  This step is not required, but it is the entire reason
why I even wrote this little program.

### Commandline

Alternatively you can also run it from commandline without registering file
extensions at system level.  Only the path to the ROM file is required, as the
core will be determined by analyzing the extension.  If multiple files are
given, then the first in the list is run.

Additionally there are a lot of options and features.  In example force a
specific core or play the last game from the history of played games.
Internally the program keeps track of all ROM files it was given to, through
various options or stdin.  Usually the first game from it will be launched, but
there are filters, sorting and selection methods to alter the selection to your
liking.  Or the list could be output to stdout, so it can be piped into another
program for your personal needs.

Have fun exploring.  Use `man retroplay`, if it is installed or the option
`--help` to list all available options.

## Configuration

**retroplay** is configured through the widely known INI format with
sections and keys.  **retroplay** have to run at least once, to create a
default configuration if none exists.

The default location is: *$HOME/.config/retroplay/settings.ini*

The way to configure is by adding rules under section **\[filetype\]**, to
associate a file extension with a core id.  This core id is then linked with
another section under **\[core\]**, which points to the correct emulator core
filename. In example to associate the extension *\*.sfc* with the emulator core
*snes9x* would be done in these two (or three, depending on the view) steps:

1. Open the file *$HOME/.config/retroplay/settings.ini* in your editor.
2. Go to section **\[filetype\]** and add this line to its bottom:
   `*.sfc = snes`
3. Go to section **\[core\]** and add this line to its bottom:
   `snes = snes9x_libretro.so`

In example like this:

```
[core]
gb = sameboy_libretro.so
snes = snes9x_libretro.so

[filetype]
*.gb = gb
*.smc = snes
*.sfc = snes
```

That's it. Run a file that ends with extension *.sfc* with **retroplay** and it
will choose the right core, based on these rules.  But obviously this core
needs to be installed via RetroArch itself too.  The manpage talks in more
detail about the configuration.

## Installation

An installation is optional, as the program runs from any location.  There are
two archives, one for those who have Python *3.9* or newer and for those who
don't have it.  The binary package is bundled and pseudo compiled with the
Python interpreter together.  Choose on of these files and download it, replace
the "x.x" part with the actual version number of the program:

*retroplay-x.x-Python.tar.gz*
: if you have Python *3.9* (or newer)

*retroplay-x.x-Linux-64Bit.tar.gz*
: if you don't have Python *3.9* (or newer)

Just unpack the archive and either run the program directly or use the provided
*install.sh* script (requires `sudo`) to install the executable and
documentation to the systems standard directories.

It should be self explanatory that RetroArch itself is required, as the program
is built upon it.  **dmenu** and **rofi** are optional and only needed, if the
option **--menu** is used.

### Uninstall

If you want remove the program from your system and you have installed it with
the script, then just use the provided *uninstall.sh* script.  If you altered
any path, then off course the script does not work, as the path is hard coded
into the file. The standard files and folders are:

*/usr/local/bin/retroplay*
: the program

*/usr/local/doc/retroplay/*
: direcotry with additional documentation

*/usr/local/man/man6/retroplay.6.gz*
: manpage documentation

*~/.config/retroplay/settings.ini*
: default configuration file

### Flatpak version of RetroArch

Currently the Flatpak version of RetroArch is not supported.  I have to test
and workout what is needed first.  The internal building of the command to run
`retroarch` is based on the *regular* version.

### Make / Source Code

You don't need to build this, as the distributed version is the same Python
script, just renamed to remove the *.py* extension.  The only thing that is
build from source code are the documentation, distribution packages and generic
install scripts.

`make`
: no options will list a few standard targets

`make --all`
: builds the documentation, creates install scripts and the final packages

`make clean`
: removes temporary files and folders created during the make process

`make install`
: just runs the created *install.sh* script

The following tools are required for building from source code:

`pyinstaller`
: to create the binary package

`pandoc`
: to convert the Markdown documentation into Manpage and HTML formats

## Known bugs, limitations and quirks

Look at section **BUGS** in the manpage documentation for more infos.

## Feedback

If you want to report a bug or have any question, then [leave me a
message](https://thingsiplay.game.blog/contact/) on my contact page.

