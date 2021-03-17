% RETROPLAY(1) retroplay %APP\_VERSION%
% %APP\_AUTHOR%
% %APP\_DATE%

# NAME

retroplay - RetroArch run script and playlist extractor on Linux

# SYNOPSIS

**retroplay** *ROM\_FILE* [*OPTIONS*]

[*ROM\_FILES*] | **retroplay** [*ROM\_FILE*]... [*OPTIONS*]...

# DESCRIPTION

**retroplay** is a commandline wrapper of the commandline options from
**retroarch**, to automate a few steps and enhance it with functionality.  It
is designed around RetroArch and requires a working setup of it.  **retroplay**
can run RetroArch games without using the GUI, including a few automated steps;
even assigning it as a default application for file extensions is possible.

# ROM FILES

## INTERNAL LIST

**retroplay** can collect the paths of ROM files from various input options.
If more than one file is detected, then it will create a temporary list that
only exists in the memory of the programs execution.  Normally the first entry
will be automatically selected and run with the emulator.  However there are
filter, sort and selection methodes to narrow down the list.  The document will
refer to it as **the internal temporary list of ROM files**.

## ARGUMENTS

[*ROM_FILE*]...
: Path to a game ROM file to play.  If multiple files are given, then the first
entry in the list is used as the main game.  See option **--game**.
Example: *retroplay "~/roms/snes/Super Mario World (U) [!].smc"*

## STDIN

[*ROM_FILES*]
: List of paths to game ROM files to read from stdin stream.  The list should
be separated by a newline '\\n' character.  Each entry is handled like in
option **--game**.
Example: *"rom1.smc"\\n"rom2.gb"\\n"rom3.md"\\n | retroplay*

# OPTIONS

**-h**, **--help**
: Print help message and exit.

**-v**, **--version**
: Print program name, version, compiler if any and exit.

**--app** [*KEY*...]
: Print pure meta information about the program without exiting.  Accepted
values for *KEY* are: "name", "version", "date", "author", "license",
"minpython", "isfrozen".  Multiple keys can be specified.  Each data is output
to a separate line at the beginning of execution.
Example: *--app version date*

**--showconfig**
: Print location of various configuration files and the content of current
active *settings.ini* file specified in *--config*, then exit.

**-c**, **--config** *FILE*
: Path to the master configuration for this program, also known as the
*settings.ini* file. It defaults to *$HOME/.config/retroplay/settings.ini* if
no *FILE* is specified.

**-g**, **--game** *ROM_FILE*...
: Path to the game ROM to play.  Wildcards are not supported supported.  But
multiple files can be given ove if the wildcards are resolved in the shell, so
the program retrieves multiple files instead.  Multiple files are queued into a
temporary internal list of ROM files.  While only the first file is used to run
in the emulator, this list can be sorted and filtered before
Example: *--game "~/roms/snes/Super Mario World (U)\*"*

**-L**, **--libretro** *FILE*
: Force a specific emulator core by real filename or path on the filesystem.
If *FILE* begins with a slash "/", then consider it to be an absolute path.  If
it contains any "/", but does not start with it, then consider it to be a
relative path and expand it from current working directory.  If no "/" is
present, then search this filename in the RetroArch core directory to see if
one is matching.  Generally the filename ending part *\_libretro.so* can be
left out; they will be added automatically if needed.  Wildcards are not
supported.  This option has higher priority than **--core**.
Example: *--libretro mesen_libretro.so*

**-C**, **--core** *ID*
: Force a specific core by its custom core id specified in the programs
*settings.ini* file.  This option will lookup the filename by given *ID* under
the section **[core]**.  Wildcards are not supported.
Example: *--core snes*

**-p**, **--patch** *FILE*
: Path to a patch file to apply it to the ROM on the fly.  Supported formats
are *.ups*, *.bps* and *.ips* files.  The original ROM file is untouched, it
will just create a temporary symbolic link during the play session.  This will
help to avoid collision for save files of untouched ROMs.  The basename of the
temporary file will have the format *PATCHFILE.EXT\_ROMFILE* and is used for
save files as well.  Wildcards are not supported.
Example: *--patch "./KKQFixedIntros.bps"*

**-P**, **--nopatch**
: Disable soft patch system entirely, regardless of any other setting.  This
will also disable RetroArchs automatic patching of ROMs, if there is a file
with same name but different extension.

**-Z**, **--nostdin**
: Ignore and disable interaction with stdin.  Usually the stdin is read if
something is piped into it.  Without this option each line is assumed to be a
path of a ROM file.

**-l**, **--playlist** [*FILE*]
: Read and load all game entries from a RetroArch playlist file.  Supported
format is JSON type with extension *.lpl* .  *FILE* will be parsed and all
entries with a tag **path** are read and added to the internal temporary list
of ROM files.  If *FILE* does not contain any slash "/", then the playlist file
will be looked up in the playlist folder of your RetroArch configuration.  If
*FILE* starts with a "/", then it is handled as an absolute path.  If any "/"
is found somewhere in *FILE*, then it is considered to be a relative path and
will be extended to fullpath from current working directory.  Wildcards are not
supported.  File extension *.lpl* is optional and is added if missing.  The
special keywords **history** and **favorites** on their own will be
automatically resolved to what is specified in RetroArchs own configuration at
**content_history_path** or **content_favorites_path** variables.  Defaults to
**history** if no *FILE* was specified.
Example: *--playlist "\*Game Boy"*

**-d**, **--dir** *PATH*...
: Path to a directory to read all files from and populate the programs internal
temporary list of ROM files.  Multiple *PATH* can be specified.  Wildcards are
not supported.
Example: *--dir . "~/Emulators/\*/snes\*"*

**-o**, **--ls**
: Print a newline separated listing of all ROM files and paths which have been
gathered through various sources by the other options.  The output happens
after any filter and sort mechanism, but before **--what** and **--which**.
Output does not include the current selected game.  See option **--what** to
output the current selection.

**-w**, **--what**
: Print the current selected ROM path that is in use to run with the emulator.
Output only if the emulator run successfully and the file exist on the
filesystem.  In case option **--norun** is in effect, then print the path only
if it exists on the filesystem.  In case option **--patch** is in effect, then
the path points to the temporary symbolic link, which might not exist anymore
after program exit.  Path is printed after **--ls** but before **--which**.

**-W**, **--which**
: Print the determined emulator core path for the current selected ROM that is
in use to run with the emulator.  Output only if the emulator run successfully
and the file exist on the filesystem.   In case option **--norun** is in
effect, then print the path only if it exists on the filesystem.  Path is
printed after **--ls** and **--which**.

**-i**, **--index** *NUM*
: Select a game by it's position in the internal working list of all ROM files.
*NUM* must be an integer.  A positive number is counted from beginning of the
list, in general "1" translates to the first entry.  A negative number starts
counting backwards from the last, where "0" points to the last and
"-1" to one before the last entry.
This option have no effect, if **--menu** is in use.
Example: *--index 2*

**-m**, **--menu** [*MODE*]
: Select a game from the internal working list of all ROM files by a menu
driven system, using separate tools.  *MODE* specifies which menu to run.
Available systems are: "dmenu" and "rofi".  The applications are required to be
in *$PATH*, otherwise this option reports that nothing has been selected.  If
**--menu** is used without specifying *MODE* then it defaults to *dmenu*.  This
option have higher priority than **--index**.
Example: *--menu rofi*

**-F**, **--filter** PATTERN...
: Exclude all non matching paths from the internal list of ROM files.
*PATTERN* supports regular expressions too, if any non alphanumerical character
is detected.  Comparison is done against fullpath of each file.  Case
sensitivity is deactivated.  Multiple pattern can be specified if separated by
space.
Example: *--filter "mario|zelda" "!" "-"*

**-N**, **--filter-names** PATTERN...
: See option **--filter**.  Only difference is the comparison is done against
the basename of the filename.  The directory portion and extension are not
compared.
Example: *--filter "!"*

**-E**, **--filter-ext** PATTERN...
: See option **--filter**.  Only difference is the comparison is done against
the extension of the filename.  The directory portion and basename are not
compared.  The initial dot "." is not part of the extension for this
comparison.
Example: *--filter "sfc|smc" "gb$"*

**-v**, **--validate**
: Filter out each invalid entry from the internal temporary list of ROM files.
Each path must exist on the filesystem and a matching pattern and core for it's
filetype in the *settings.ini* configuration is required.

**-V**, **--invalidate**
: Inverse **--validate**.  Exclude valid entries.  This option have higher
priority than **--validate**.

**-U**, **--uniq**
: Filter out duplicate entries from the internal temporary list of ROM files.

**-s**, **--sort**
: Sort all entries in the internal temporary list of ROM files by alphabetical
order, based on the entire fullpath.  Case sensitivity is deactivated.

**-n**, **--sort-names**
: See option **--sort**.  Only difference is the comparison is done against
the basename of the filename.  The directory portion and extension are not
compared.  This option have higher priority than **--sort**.

**-e**, **--sort-ext**
: See option **--sort**.  Only difference is the comparison is done against the
extension of the filename.  The directory portion and basename are not
compared.  This option have higher priority than **--sort-names** and
**--sort**.

**-f**, **--fullscreen**
: Force RetroArch and the emulator to run in fullscreen, regardless of any
other setting.

**-X**, **--norun**
: Do not run emulator.  Any other operation is executed as normal.  Useful to
simulate the process or when printing only is required.

**-Q**, **--quiet**
: Supress error messages and warnings from stderr.  However, regular output to
stdout such as **--ls** is still printed.

**-r**, **--record** *FILE*
: Write a video recording file of the current play session in MKV format.
Relative and fullpath are supported and the extension is added or replaced to
*.mkv* automatically.  If *FILE* starts with a "%", then the directory of
current active ROM file is used as output folder, otherwise default to current
working directory.  If *FILE* contains an "@", then add the base filename of
the ROM file at this position, excluding the extension.  If *FILE* contains a
"#", then add the current timestamp at this position in the format
"20210309200315".  However, if *FILE* is set to the exact string "=" without
any other part, then use the directory and filename of the current ROM file,
but with replaced extension to *.mkv*.
Example: *--record "%new_filename"*

**-R**, **--record-disable-macros**
: Disable the macro functionalities of **--record** option.  This will prevent
the expansion of the special characters "%", "@", "#" and "=" in argument
*FILE* at option **--record**.

**--addfiletype** *PATTERN=CORE_ID*
: Add a rule to the configuration file specified at **--config** to recognize
filetypes and associate it with a custom id for a core.  This option writes to
the section "[filetype]" in the file and is permanent.  *PATTERN* is a file
extension.  An asterisk "\*" will be added in front of the extension, if
missing.  *CORE_ID* is a custom id for an emulator, to link it with the same
*CORE_ID* specified at section "[core]", such as "snes".  Both values are
separated by an equal sign or double colon.
Example: *--addfiletype "sfc:snes"*

**--addcore** *CORE_ID=CORE_NAME*
: Add a rule to the configuration file specified at **--config** to associate
an emulator filename with a custom *CORE_ID*.  This option writes to the
section "[core]" in the file and is permanent.  *CORE_ID* is used within
section "[core]" and is linked with section "[filetype]".  This can be any name
you want to use for this system, like a shortcut.  *CORE_NAME* is the actual
filename of the emulator core, such as *mesen_libretro.so*.  The part
*_libretro.so* is optional and will be added dynamically at runtime.  Both
values are separated by an equal sign or double colon.
Example: *--addcore "snes:snes9x_libretro.so"*

# CONFIG

Basic configuration is done in *~/.config/retroplay/settings.ini*, if not
otherwise specified at commandline option **--config**.  If the file does not
exist, then a default *settings.ini* is created when running **retroplay** at
least once.  It is not to be confused with the settings files from RetroArch
itself.

The file is in the widely known **INI** format.  The keys distinguish between
lowercase and uppercase characters, but some options maybe case insensitive.
For file extensions, the general thumb of rule is to use lowercase only.

The configuration file consist of a general section **\[retroarch\]**, a
section **\[core\]** and the section for defining the actual file extension
rules at **\[filetype\]**.  Rules for file extensions is done in two steps:

1. add a custom **CORE_ID** as a shortcut to a **CORE_FILENAME** and
2. add a **CORE_PATTERN** rule to determine which files should be associated
   with that custom **CORE_ID**.

## Example

```
[retroarch]
bin = retroarch
dir = $HOME/.config/retroarch
config = $HOME/.config/retroarch/retroarch.cfg

[core]
snes = snes9x
gb = sameboy
gbc = sameboy

[filetype]
~/Emulatoren/games/snes/* = snes
*.smc = snes
*.sfc = snes
*.gb = gb
*.gbc = gbc
```

## \[retroarch\]

**KEY = VALUE**

**bin**
: Path to the **retroarch** executable from RetroArch installation.  Usually it
is installed in **$PATH** and the default value of *retroarch* should be
enough.

**dir**
: Path to the main RetroArch home directory, where usually all settings and
configuration files are stored.  Normally this is found at
*$HOME/.config/retroarch* and should be fine in most cases.  The commandline
option **--dir** can point to a different file.

**config**
: Path to the main default RetroArch configuration file.  Usually this is named
*retroarch.cfg* and is found under the RetroArch home directory.  The
commandline option **--config** can point to a different file.

**force_fullscreen**
: Start the emulation window in fullscreen mode, regardless of any other
settings. If this option is missing or set to off, then it has no effect and
the fullscreen behaviour is determined by commandline options or the original
settings found in RetroArch itself.  Any value of *1*, *yes*, *true*, and *on*
sets this setting to on.  The commandline option **--fullscreen** can force to
fullscreen as well.

## \[core\]

**CORE_ID = CORE_FILENAME**

Associate a custom chosen id to a core filename.  A custom id is easier to
remember than the filename of the actual emulator core and will be used by
other commands instead of the real filename.
Example: *snes = snes9x\_libretro.so*

**CORE_ID**
: Custom identification as a shortcut for an emulator core from RetroArch.
This ID  can be chosen freely and will be used by other commands instead of the
real filename.  Multiple ids can point to the same emulator core.
Example: *snes*

**CORE_FILENAME**
: The actual filename of the emulator core, found under the cores folder of
RetroArch.  This must be the basename without any directory portion.  The
*\_libretro.so* part is optional and will be added if missing.
Example: *snes9x\_libretro.so*

## \[filetype\]

**FILE_PATTERN = CORE_ID**

Create a rule to determine which file extension should be detected and
associate this rule to a specific emulator core id.  Internally the program
will expand any ROM file path to its fullpath, which the pattern rule is
compared against.  If a match is found, then its associated core id is looked
up from section **\[core\]**.  Usually wildcards such as "\*" are used as part
of the pattern.
Example: *\*.smc = snes*

**FILE_PATTERN**
: This pattern is what will be compared to the ROM file path, to see if it
matches.  This is usually a file extension and contains wildcards, so it can be
applied to all files with that extension.  The **FILE_PATTERN** can include a
directory too, in which case only files from that directory can match.
Example: *\*.smc*

**CORE_ID**
: The custom id of the core from section **\[core\]** to associate the
**FILE_PATTERN** to.  This practically links to the other section, in order to
find the real filename of the core to use.

There are two comparison behaviours, file extension-mode and directory-mode.

### "file extension"-mode

If no slash "/" is in the pattern, then it is assumed to be an extension.  It
is best practice to include a star wildcard "\*" in front of the pattern, so it
matches any path with that extension.  In example the rule *\*.smc* would match
*/file/to/mygame/Mario\_World.smc*.

### "directory"-mode

If a slash "/" is detected in the pattern, then it is assumed to be a path
including a directory part.  Relative paths are expanded, the "~" is expanded
to users home directory and even system varialbes are resolved, such as
"$HOME".  It is best practice to include any sort of wildcard at the end, so it
can match files in that directory.  In example the rule *~/roms/snes/\** would
match all files in the directory */home/usr/roms/snes*.

### The order of rules

The order of pattern under **\[filetypes\]** matters.  If two rules matches
same file, then the bottom pattern from configuration file have the higher
priority.  This means, the program is looking up and comparing from bottom
first.  If no match is found, then it will go one line up and check the next
pattern until a match is found.

This behaviour can be used as a default directory, if no other rule matches.
Also it can come in handy for generic file extensions for various different ROM
formats, such as *.chd* or *.zip*.

# EXIT STATUS

**0**
: No problem

**1**
: File not found

**2**
: Minimal requirements not fulfilled.

**3**
: Not supported.

# ENVIRONMENT

Most paths used with the program will expand any environmental variable, like
*\$HOME*.  Any variable in the format starting with a dollar symbol "$" and
followed by the name of the variable (in most cases all uppercase) will be
expanded to its value.  Even those added temporarily for the current session.
As a sidenote, the tilde "~" is also expanded to current users home directory.
Example: *\$HOME/.config/retroarch*

# FILES

The location of the files can vary depending on the settings.  These are places
where the application will look at default.

- *$HOME/.config/retroplay/settings.ini*
- *$HOME/.config/retroarch/retroarch.cfg*

## Additional playlist files

The following files are only read when using the **--playlist** option.  And
their location highly depends on the settings found in the *retroarch.cfg*.

- *content_history.lpl* (in the retroarch directory)
- *content_favorites.lpl* (in the retroarch directory)
- various *\*.lpl* files in the retroarch playlists directory

# NOTES

As this program is built open the RetroArch framework and its commandline
application, it is off course required to be installed and fully functional.
**retroplay** will just run **retroarch** with the right options and read a few
files from it.

**dmenu** is a minimalistic tool to dynamically create a menu system with
filter and selection features.  This is in **retroplay** only utilized when the
option **--menu** is in use.  Otherwise it is not required to be installed on
the system.  **rofi** is an alternative to **dmenu**.

# BUGS

A few RetroArch settings are read from its base configuration file
*retroarch.cfg* (at default) only.  This is not an issue with most setups, but
it can be if those settings appear in a core specific configuration file.
These settings are read:

- **libretro\_directory**
- **playlist\_directory**
- **content\_history\_path**
- **content\_favorites\_path**
- **savefile\_directory**

Not all commandline options and features from original **retroarch** program
are supported.

There is no handling of systems that work differently than regular game console
systems like SNES or Genesis.  This program is not tested and created in mind
with arcade systems such as MAME or a cd based console.  So use it with
caution.

A lot of error checking is not done, in example the user privileges.  Also it
is best to use lowercase file extensions only, while any mixed case should work
in most scenarios, it is still a potential source of problems.

# EXAMPLES

**retroplay**
: Print program name and simple arguments structure, then exit.

**retroplay "Super Mario World (U) [!].smc"**
: Loads up RetroArch with the ROM from current working directory and the
predefined core based on the file extension and rules in the *settings.ini* .

**retroplay --playlist**
: Loads up RetroArch with the last played game from default **history**
playlist.  The core will be chosen based on the ROM file extension, regardless
of the playlist content.

**retroplay --norun --ls --playlist "*Game Boy*" | wc -l**
: Search in the standard playlist directory for a ".lpl" that contains
"Game Boy" in the filename.  Read all *path* entries from it and count how
many entries are available.

**retroplay -Xosv -l history -E "smc|sfc"**
: Using short format of options.  Read all *path* entries from standard
**history** playlist, validate each entry and sort the list.  Filter out all
path, which do not have a file extension that matches the regular expression
(no case sensitivity).  Only "*.smc" and "*.sfc" files are included in the
final list.  Print the list to stdout without running the emulator.

# SEE ALSO

**dmenu**(1), **rofi**(1), **retroarch**(6)

