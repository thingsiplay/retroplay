#!/usr/bin/python3

# Copyright (c) 2021 Tuncay D.
# MIT License, see LICENSE

import sys
import os
import select
import subprocess
import argparse
import configparser
import pathlib
import glob
import tempfile
import fnmatch
import re
import json
import datetime


def get_meta(key=None):
    meta = {
        'name': 'retroplay',
        'version': '0.2',
        'date': 'March, 2021',
        'author': 'Tuncay D',
        'license': 'MIT License',
        'minpython': '3.9',
        'isfrozen': '1' if get_isfrozen() else '0'
    }
    if key:
        try:
            return meta[key]
        except KeyError:
            return ''
    else:
        return meta


def get_arguments():

    parser = argparse.ArgumentParser(
        usage='%(prog)s ROM_FILE [options]',
        description='Run RetroArch games from commandline.',
        epilog='<https://github.com/thingsiplay/retroplay/>'
    )

    parser.add_argument(
        'rom',
        metavar='ROM_FILE',
        nargs='*',
        help=('game ROM to play, if multiple files are given then the first is'
             ' selected at default, wildcards are not supported, see option'
             ' "--game" for more info')
    )

    parser.add_argument(
        '--version',
        action='store_true',
        help=('show program name, version and compiler (if any) and exit')
    )

    parser.add_argument(
        '--app',
        metavar='KEY',
        nargs='*',
        help=('print meta information about the program without exiting,'
             ' multiple KEYs can be specified like "--app name version", each'
             ' data is printed on its own line, possible values for KEY: ' +
             ', '.join(get_meta()))
    )

    parser.add_argument(
        '--showconfig',
        action='store_true',
        help=('print location of various configuration files and content of'
              ' current config file')
    )

    parser.add_argument(
        '--config', '-c',
        dest='settings',
        metavar='FILE',
        default='$HOME/.config/retroplay/settings.ini',
        help=('path to master configuration for this program, defaults to'
             ' "$HOME/.config/retroplay/settings.ini"')
    )

    parser.add_argument(
        '--game', '-g',
        metavar='ROM_FILE',
        nargs='+',
        help=('path to the game ROM to play, wildcards are not supported')
    )
    parser.add_argument(
        '--libretro', '-L',
        metavar='FILE',
        help=('force a specific core by real filename or path on the'
             ' filesystem, if FILE begins with a slash "/" then consider it to'
             ' be an absolute path, otherwise if contains any "/" somewhere'
             ' else then consider it to be a relative path, if no "/" is found'
             ' then search the filename in the RetroArch core directory,'
             ' wildcards are not supported, the extension and ending part'
             ' "_libretro.so" is optional')
    )

    parser.add_argument(
        '--core', '-C',
        metavar='ID',
        help=('force a specific core by its custom core id specified in the'
             ' config file, this option will lookup real filename by given'
             ' "ID" under the section "[core]"')
    )

    parser.add_argument(
        '--patch', '-p',
        metavar='FILE',
        help=('path to a patch file to apply to the ROM on the fly, supported'
             ' formats are ".ups", ".bps" and ".ips" files, it will create a'
             ' temporary symbolic link file during the play session, wildcards'
             ' are not supported')
    )

    parser.add_argument(
        '--nopatch', '-P',
        action='store_true',
        help=('disable soft patch system entirely, regardless of any settings')
    )

    parser.add_argument(
        '--nostdin', '-Z',
        action='store_true',
        help=('ignore stdin, usually the stdin is read when something is piped'
             ' into it, each line is assumed to be the path of a ROM file,'
             ' this option will disable the interaction with stdin')
    )

    parser.add_argument(
        '--playlist', '-l',
        metavar='FILE',
        nargs='?',
        const='history',
        help=('read all game entries from a RetroArch playlist in JSON format'
             ' with file extension ".lpl", all entries with a tag "path" are'
             ' added into a temporary list of ROM files, if playlist "FILE"'
             ' does not contain any slash then the filename is searched in the'
             ' playlist folder of RetroArch, if "FILE" starts with a slash "/"'
             ' then it is handled as an absolute path, otherwise any "/" is'
             ' interpreted as a relative path, wildcards are not supported,'
             ' file extension ".lpl" is added automatically if missing, there'
             ' are two special keywords: "history" and "favorites", which'
             ' resolve to RetroArchs configured "content_history_path" and'
             ' "content_favorites_path", default value is "history" if'
             ' argument "FILE" is missing')
    )

    parser.add_argument(
        '--dir', '-d',
        metavar='PATH',
        nargs='+',
        help=('path to a directory to add all files from it and populate the'
            ' temporary internal list of ROM files, wildcards are not'
            ' supported, but multiple paths separated by space can be given')
    )

    parser.add_argument(
        '--ls', '-o',
        action='store_true',
        help=('output a newline separated list of all ROM files and paths that'
             ' have been gathered through various sources, list is printed'
             ' after any filter and sort option and before "--what" and'
             ' "--which", output does not include the current selected game,'
             'see option "--what" to output the current selected ROM file only')
    )

    parser.add_argument(
        '--what', '-w',
        action='store_true',
        help=('output path of current selected ROM file to play, output only'
             ' if emulator run successfully and file exist on the filesystem,'
             ' if option "--norun" is in effect then print path anyway but'
             ' only if file exist, if option "--patch" is in effect then the'
             ' path points to the temporary symbolic link and might not exist'
             ' after program terminates, path is printed after "--ls" but'
             ' before "--which"')
    )

    parser.add_argument(
        '--which', '-W',
        action='store_true',
        help=('output determined emulator core path for the current active ROM'
             ' file in use, output only if emulator run successfully and exist'
             ' on the filesystem, if option "--norun" is in effect then print'
             ' path anyway but only if file exist, this comes after "--ls" and'
             ' "--what" options')
    )

    parser.add_argument(
        '--index', '-i',
        metavar='NUM',
        default=1,
        type=int,
        help=('select a specific game by its position in the collected list if'
             ' more than one ROM path is found or given, negative number will'
             ' count backwards from last position, in general "1" is first'
             ' game, "0" is last and "-1" is one game before the last, this'
             ' have no effect if option "--menu" is in use, defaults to "1"')
    )

    parser.add_argument(
        '--menu', '-m',
        metavar='MODE',
        nargs='?',
        const='dmenu',
        choices=['dmenu', 'rofi'],
        help=('select a specific game by choosing it manually from the list'
             ' through a dynamically created menu, available systems at "MODE"'
             ' are "dmenu" and "rofi", which are external programs and needs'
             ' to be installed separately on the system, "--menu" without'
             ' specifying "MODE" defaults to "dmenu"')
    )

    parser.add_argument(
        '--filter', '-F',
        metavar='PATTERN',
        nargs='+',
        help=('exclude all non matching path entries from the internal list if'
             ' more than one ROM file was found or given, the comparison is'
             ' done against the fullpath of each entry, "PATTERN" supports'
             ' regular expression if any non alphanumerical character is'
             ' detected, case sensitivity is deactivated, multiple "PATTERN"'
             ' can be specified in a row like "--filter mario zelda"')
    )

    parser.add_argument(
        '--filter-names', '-N',
        metavar='PATTERN',
        nargs='+',
        help=('see option "--filter", only difference is the comparison is'
             ' done against basename of the filename, ignoring extension and'
             ' directory')
    )

    parser.add_argument(
        '--filter-ext', '-E',
        metavar='PATTERN',
        nargs='+',
        help=('see option "--filter", only difference is the comparison is'
             ' done against extension of the filename, ignoring basename and'
             ' directory, initial dot "." is not part of the comparison in'
             ' this case')
    )

    parser.add_argument(
        '--validate', '--verify', '-v',
        action='store_true',
        help=('exclude each invalid ROM path before proceeding, entries are'
             ' valid if the file exist on the filesystem and a matching'
             ' pattern for this filetype is configured in the settings')
    )

    parser.add_argument(
        '--invalidate', '-V',
        action='store_true',
        help=('inverse "--validate", exclude valid ROM paths find non working'
             ' ROM path instead')
    )

    parser.add_argument(
        '--uniq', '-U',
        action='store_true',
        help=('filter out duplicate ROM path if more than one file is given')
    )

    parser.add_argument(
        '--sort', '-s',
        action='store_true',
        help=('sort all ROM path by alphabetical order, comparison is based on'
             ' entire fullpath')
    )

    parser.add_argument(
        '--sort-names', '-n',
        action='store_true',
        help=('see option "--sort", only difference is the comparison is done'
             ' against basename of the filename, ignoring extension and'
             ' directory, has higher priority than "--sort"')
    )

    parser.add_argument(
        '--sort-ext', '-e',
        action='store_true',
        help=('see option "--sort", only difference is the comparison is done'
             ' against extension of the filename, ignoring basename and'
             ' directory, has higher priority than "--sort" and "--sort-names"')
    )

    parser.add_argument(
        '--fullscreen', '-f',
        action='store_true',
        help=('force RetroArch to fullscreen, regardless of any other setting')
    )

    parser.add_argument(
        '--norun', '-X',
        action='store_true',
        help=('do not run RetroArch and emulator, other operations are'
             ' executed as normal, useful to simulate the process or for'
             ' output stuff only (in example "--ls")')
    )

    parser.add_argument(
        '--quiet', '-Q',
        action='store_true',
        help=('supress error messages and warnings from stderr, however'
             ' regular output to stdout such as "--ls" is still printed')
    )

    parser.add_argument(
        '--record', '-r',
        metavar='FILE',
        help=('write a video recording file of current play session in MKV'
             ' format, relative and fullpath are supported and the extension'
             ' ".mkv" is replaced or added automatically if missing, if "FILE"'
             ' starts with a percent sign "%%" then replace it with the'
             ' directory of the current active ROM file as output folder, if'
             ' "FILE" contains an at symbol "@" then replace it with the'
             ' basename of current active ROM file excluding its extension, if'
             ' "FILE" contains a hash symbol "#" then replace this with'
             ' current timestamp (format "20210309200315"), if "FILE" is set'
             ' to exactly the value of equal sign "=" and nothing else then'
             ' use the ROM files path with extension replaced to ".mkv",'
             ' example: --record "%%new_filename"')
    )

    parser.add_argument(
        '--record-disable-macros', '-R',
        action='store_true',
        help=('disable the macro functionality for "FILE" at option "--record"'
             ' by taking the special characters "%%", "@", "#" and "=" as'
             ' literal characters without interpretation')
    )

    parser.add_argument(
        '--addfiletype',
        metavar='PATTERN=CORE_ID',
        help=('add a rule to the configuration file to recognize filetypes and'
             ' associate a custom core id to it, "PATTERN" is a file extension'
             ' which is used to test against the fullpath, an asterisk "*"'
             ' will be added in front of the "PATTERN" if missing, "CORE_ID"'
             ' is a custom id for an emulator which should be one of the'
             ' predefined "CORE_ID" in section "[core]", this acts as a link'
             ' to the other section, both values are separated by an equal'
             ' sign or double colon, this option writes to the section'
             ' "[filetype]" in the config file permanently, example:'
             ' --addfiletype "sfc:snes"')
    )

    parser.add_argument(
        '--addcore',
        metavar='CORE_ID=CORE_NAME',
        help=('add a rule to the configuration file to associate a custom id'
             ' for an emulator to its real filename on the system, "CORE_ID"'
             ' can be freely chosen but should match the "CORE_ID" from the'
             ' rule in section "[filetype]", as this is a link to the other'
             ' section, "CORE_NAME" is the actual filename of the emulator'
             ' core from RetroArch, the part "_libretro.so" is optional and'
             ' will be added dynamically at runtime, both values are separated'
             ' by an equal sign or double colon, this option writes to the'
             ' section "[core]" in the config file permanently, example:'
             ' --addcore "snes:snes9x_libretro.so"')
    )

    return parser.parse_args()


def write_default_settings(settings_file):

    settings = configparser.ConfigParser()
    settings.optionxform = lambda option: option
    settings['retroarch'] = {
            'bin': 'retroarch',
            'dir': '$HOME/.config/retroarch',
            'config': '$HOME/.config/retroarch/retroarch.cfg',
            'force_fullscreen': 'False'
    }

    settings['core'] = {
    #       a) core_identifier  b) filename_of_core
            'a26':              'stella',
            'pce':              'mednafen_pce',
            'nes':              'mesen',
            'snes':             'snes9x',
            'gb':               'sameboy',
            'gbc':              'sameboy',
            'gba':              'mgba',
            'n64':              'mupen64plus_next',
            'sms':              'smsplus',
            'gg':               'smsplus',
            'md':               'genesis_plus_gx',
            'mdwide':           'genesis_plus_gx_wide',
            '32x':              'picodrive'
    }

    settings['filetype'] = {
    #       c) file_pattern     a) core_identifier
            '~/Emulatoren/games/snes/*': 'snes',
            '*.a26':            'a26',
            '*.pce':            'pce',
            '*.nes':            'nes',
            '*.fds':            'nes',
            '*.smc':            'snes',
            '*.sfc':            'snes',
            '*.gb':             'gb',
            '*.gbc':            'gbc',
            '*.gba':            'gba',
            '*.z64':            'n64',
            '*.n64':            'n64',
            '*.sms':            'sms',
            '*.gg':             'gg',
            '*.md':             'md',
            '*.smd':            'md',
            '*.gen':            'md',
            '*.wide.md':        'mdwide',
            '*.32x':            '32x'
    }

    settings_file.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_file, 'w') as file:
        settings.write(file)
    return settings


def get_suffixes(path):
    suffixes = pathlib.PurePath(path).suffixes
    return ''.join(suffixes)


def add_settings_filetype(settings_file, settings, addfiletype):
    addfiletype = addfiletype.replace(':', '=')
    if '=' in addfiletype:
        pattern = addfiletype.split('=')[0]
        core = addfiletype.split('=')[1]
    else:
        pattern = ''
        core = ''
    if pattern and core:
        if '/' in pattern:
            settings.set('filetype', pattern, core)
        else:
            suffixes = get_suffixes(pattern)
            if not suffixes:
                suffixes = pattern
                if not suffixes[:1] == '.':
                    suffixes = '.' + suffixes
            if not '*' in suffixes:
                suffixes = '*' + suffixes
            settings.set('filetype', suffixes, core)
        return True
    return False


def add_settings_core(settings_file, settings, addcore):
    addcore = addcore.replace(':', '=')
    if '=' in addcore:
        core_id = addcore.split('=')[0]
        core_file = addcore.split('=')[1]
    else:
        core_id = ''
        core_file = ''
    if core_id and core_file:
        settings.set('core', core_id, core_file)
        return True
    return False


def get_path(path, useglob=False):
    if str(path).startswith('file://'):
        path = path[7:]
    try:
        fullpath = os.path.expandvars(path)
        fullpath = pathlib.Path(fullpath).expanduser()
        if useglob:
            path = fullpath.as_posix()
            path = re.sub(r'\[(.+?)\]', r'[[]\1[]]', path)
            fullpath = glob.glob(path)
            if fullpath:
                fullpath = pathlib.Path(fullpath[0])
            else:
                fullpath = ''
        else:
            fullpath = pathlib.Path(fullpath).resolve()
    except (KeyError, RuntimeError, PermissionError):
        fullpath = None
    return fullpath


def get_settings(settings_file):
    if settings_file and settings_file.exists():
        settings = configparser.ConfigParser()
        settings.optionxform = lambda option: option
        settings.read(settings_file)
        if not settings.has_section('filetype'):
            settings.add_section('filetype')
        if not settings.has_section('core'):
            settings.add_section('core')
    else:
        settings = write_default_settings(settings_file)
    return settings


def get_retroarch_config_vars(ra_config_file, filter_list):
    retroarch_config = {}
    try:
        with open(ra_config_file, 'rt') as file:
            for line in file:
                for var in filter_list:
                    if var in line:
                        m = re.match(r'^' + var + r'\s*\=\s*"(.+)"', line)
                        retroarch_config[var] = m.group(1)
    except FileNotFoundError:
        return {}
    return retroarch_config


def get_playlist_file(playlist, ra_config):
    if playlist is not None:
        if playlist == 'history':
            playlist_file = get_path(ra_config['content_history_path'])
        elif playlist == 'favorites':
            playlist_file = get_path(ra_config['content_favorites_path'])
        else:
            if '/' in playlist:
                playlist_file = pathlib.PurePath(playlist)
                playlist_file = playlist_file.with_suffix('.lpl')
                playlist_file = get_path(playlist)
            else:
                pl_dir= pathlib.PurePath(ra_config['playlist_directory'])
                playlist_file = pathlib.PurePath(playlist)
                playlist_file = get_path(
                        pl_dir / playlist_file.with_suffix('.lpl')
                )
        return playlist_file
    else:
        return ''


def get_playlist_data(playlist_file):
    if playlist_file and playlist_file.exists():
        with open(playlist_file, 'r') as file:
            data = file.read()
        try:
            playlist_data = json.loads(data)
        except JSONDecodeError:
            return {}
        return playlist_data
    else:
        return {}


def get_playlist_item(playlist_data, tagname):
    try:
        return [item[tagname] for item in playlist_data['items']]
    except KeyError:
        return []


def get_dir_files(dir_path):
    files = []
    for path in dir_path:
        path = get_path(path)
        if path and path.is_dir():
            files.extend(path.glob('*.*'))
    if files:
        return [p for p in files if p.is_file()]
    else:
        return []


def get_roms_list(arguments_nostdin, arguments_rom, arguments_game,
         playlist_item_path, dir_files):
    if arguments_game:
        arguments_rom.extend(arguments_game)
    roms_list = [rom for rom in arguments_rom]
    roms_list.extend(playlist_item_path)
    roms_list.extend(dir_files)
    #if arguments_nostdin and not os.isatty(0):
    if not arguments_nostdin and select.select([sys.stdin,],[],[],0.0)[0]:
        roms_list.extend([line for line in sys.stdin.read().splitlines()])
    return [pathlib.PurePath(path) for path in roms_list]


def get_core_name(settings, rom_path):
    rompath_lower = str(rom_path).lower()
    items = settings.items('filetype')
    items.reverse()
    for item in items:
        pattern = item[0]
        core_name = settings.get('filetype', pattern)
        if '/' in pattern:
            pattern = get_path(pattern, True)
        if fnmatch.fnmatch(rompath_lower, str(pattern).lower()):
            return core_name
    return ''


def get_core_path(settings, core_name, libretro_dir):
    try:
        core_path = settings.get('core', core_name)
    except (configparser.NoOptionError, configparser.NoSectionError):
        return ''
    else:
        if '_libretro' not in core_path:
            core_path += '_libretro.so'
        if not core_path.endswith('.so'):
            core_path += '.so'
        return get_path(libretro_dir / core_path)


def get_core_path_byfilename(core_path, libretro_dir):
    if '_libretro' not in core_path:
        core_path += '_libretro.so'
    if not core_path.endswith('.so'):
        core_path += '.so'
    return get_path(libretro_dir / core_path)


def get_record_file(path, rom_path):
    if path == '=':
        record_file = rom_path.with_suffix('.mkv')
    else:
        if '#' in path:
            timestamp = datetime.datetime.now()
            timestamp = timestamp.strftime('%Y%m%d%H%M%S')
            path = path.replace('#', timestamp)
        if '@' in path:
            path = path.replace('@', rom_path.stem)
        if path.startswith('%'):
            path = path[1:]
            if path == '':
                path = rom_path
            else:
                path = rom_path.parent / path
        record_file = pathlib.PurePath(path).with_suffix('.mkv')
    return get_path(record_file)


def get_patch_file(path):
    patch_file = get_path(path)
    if patch_file:
        try:
            patch_format = patch_file.suffix[1:].lower()
        except AttributeError:
            patch_format = ''
        if not patch_format in ['ups', 'bps', 'ips']:
            patch_format = ''
        return (patch_file, patch_format)
    else:
        return ('', '')


def get_command(retroarch_bin_path,
                arguments,
                core_path,
                rom_path,
                ra_config_file,
                record_file,
                patch_file,
                patch_format,
                fullscreen
    ):
    command = ['retroarch']
    command.extend(['--config', ra_config_file.as_posix()])
    command.extend(['--libretro', core_path.as_posix()])
    if arguments.record:
        command.extend(['--record', record_file.as_posix()])
    if patch_file and patch_format:
        command.extend([f'--{patch_format}', patch_file.as_posix()])
    if fullscreen:
        command.append('--fullscreen')
    command.append(rom_path.as_posix())
    return command


def get_existing_roms_list(rom_path, roms_list):
    existing_roms_list = []
    if rom_path.exists():
        existing_roms_list.append(rom_path)
    if len(roms_list) > 1:
        for path in roms_list[1:]:
            if pathlib.Path(path).exists():
                existing_roms_list.append(path)
    return existing_roms_list


def get_duplicates_removed(oldlist):
        newlist = []
        for line in oldlist:
            if line not in newlist:
                newlist.append(line)
        return  newlist


def get_filtered_list(pathlist, pattern):
    if pattern.isalnum():
        pattern = pattern.lower()
        return [path for path in pathlist if
                pattern in path.as_posix().lower()]
    else:
        return [path for path in pathlist if
                re.search(pattern, path.as_posix().lower(), re.IGNORECASE)]


def get_filtered_list_names(pathlist, pattern):
    if pattern.isalnum():
        pattern = pattern.lower()
        return [path for path in pathlist if
                pattern in path.stem.lower()]
    else:
        return [path for path in pathlist if
                re.search(pattern, path.stem.lower(), re.IGNORECASE)]


def get_filtered_list_ext(pathlist, pattern):
    if pattern.isalnum():
        pattern = pattern.lower()
        return [path for path in pathlist if
                pattern in path.suffix.lower().removeprefix('.')]
    else:
        return [path for path in pathlist if
                re.search(pattern, path.suffix.lower().removeprefix('.'),
                    re.IGNORECASE)]


def get_valid_list(roms_list, settings, valid_mode):
    newlist = []
    for path in roms_list:
        path = get_path(path)


def get_valid_list(roms_list, settings, valid_mode):
    newlist = []
    for path in roms_list:
        path = get_path(path)
        valid = bool(get_core_name(settings, path) and path.exists())
        # validate
        if valid_mode == 1 and valid:
            newlist.append(path)
        # invalidate
        elif valid_mode == 2 and not valid:
            newlist.append(path)
    return newlist


def get_rom_byindex(roms_list, index=1):
    if index == 0:
        index = len(roms_list)
    index -= 1
    try:
        return roms_list[index]
    except IndexError:
        return ''


def get_rom_bydmenu(roms_list):
    stdin_data = '\n'.join(str(i) for i in roms_list)
    command = ['dmenu', '-i', '-l', '15']
    return get_rom_byshellpipe(command, stdin_data)


def get_rom_byrofi(roms_list):
    stdin_data = '\n'.join(str(i) for i in roms_list)
    command = ['rofi', '-dmenu', '-i']
    return get_rom_byshellpipe(command, stdin_data)


def get_rom_byshellpipe(command, stdin_data=''):
    try:
        p = subprocess.run(command,
                stdout=subprocess.PIPE,
                input=stdin_data,
                text=True
        )
        selection = p.stdout.strip('\n')
        if p.returncode == 0 and len(selection):
            return selection
        else:
            return ''
    except FileNotFoundError:
        return ''

def get_mimetype(path, brief=False):
    command = []
    command.append('file')
    command.append('--mime-encoding')
    command.append('--brief')
    command.append(str(path))
    try:
        completed_process = subprocess.run(command,
                capture_output=True,
                text=True,
                check=True)
        if completed_process.returncode == 0:
            return str(completed_process.stdout).strip('\n')
    except Exception:
        return ''
    return ''


def check_requirements(meta):
    minpython = meta['minpython'].split('.')
    if (sys.version_info[0] < int(minpython[0])
        or sys.version_info[1] < int(minpython[1])):
        stderr(f'ERROR! At least Python {meta["minpython"]} required.', False)
        sys.exit(2)
    return True


def stderr(message, quiet):
    if not quiet:
        if message is None:
            message = ''
        sys.stderr.write(str(message) + '\n')

def get_retroarch_bin_path(command):
    command = ['which', command]
    try:
        completed_process = subprocess.run(command,
                capture_output=True,
                check=True,
                text=True)
        if completed_process.returncode == 0:
            retroarch_bin_path = completed_process.stdout.rstrip('\n')
            if retroarch_bin_path.startswith('which:'):
                retroarch_bin_path = None
        else:
            retroarch_bin_path = None
    except subprocess.CalledProcessError:
        retroarch_bin_path = None
    return retroarch_bin_path


def get_isfrozen():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


if __name__ == '__main__':

    meta = get_meta()
    check_requirements(meta)
    arguments = get_arguments()

    settings_file = get_path(arguments.settings)
    settings = get_settings(settings_file)

    if len(sys.argv) == 1:
        #print(meta['name'] + ' v' + meta['version'] + ' by ' + meta['author'])
        print(pathlib.Path(sys.argv[0]).name + ' ROM_FILE [OPTIONS]')
        sys.exit(0)

    if arguments.version:
        if get_isfrozen():
            print(meta['name'] + ' v' + meta['version'] + ' (pyinstaller)')
        else:
            print(meta['name'] + ' v' + meta['version'])
        #print(meta['version'])
        sys.exit(0)

    if arguments.app:
        for key in arguments.app:
            print(get_meta(key))

    temp_dir = tempfile.TemporaryDirectory(prefix='retroplay_')

    retroarch_bin = settings.get('retroarch', 'bin', fallback='')
    retroarch_bin_path = get_retroarch_bin_path(retroarch_bin)
    if retroarch_bin_path is None:
        message = f'Could not find RetroArch executable: "{retroarch_bin}"'
        stderr(message, arguments.quiet)
        sys.exit(1)

    if arguments.addfiletype:
        added = add_settings_filetype(settings_file, settings,
                                      arguments.addfiletype)
        if added:
            with open(settings_file, 'w') as file:
                settings.write(file)
        else:
            message = f'Could not add filetype: "{arguments.addfiletype}"'
            stderr(message, arguments.quiet)

    if arguments.addcore:
        added = add_settings_core(settings_file, settings,
                                  arguments.addcore)
        if added:
            with open(settings_file, 'w') as file:
                settings.write(file)
        else:
            message = f'Could not add core: "{arguments.core}"'
            stderr(message, arguments.quiet)

    if arguments.invalidate:
        valid_mode = 2
    elif arguments.validate:
        valid_mode = 1
    else:
        valid_mode = 0

    ra_dir = get_path(settings.get(
        'retroarch', 'dir',
        fallback='$HOME/.config/retroarch'))

    ra_config_file = get_path(settings.get(
        'retroarch', 'config',
        fallback='$HOME/.config/retroarch/retroarch.cfg'))

    ra_config = get_retroarch_config_vars(
        ra_config_file, [
            'libretro_directory',
            'playlist_directory',
            'content_history_path',
            'content_favorites_path'
        ]
    )

    if arguments.showconfig:
        print('CURRENT ACTIVE CONFIG FILES')
        print()
        print(f'\tScript config file: "{settings_file}"')
        print(f'\tRetroArch directory: "{ra_dir}"')
        print(f'\tRetroArch config file: "{ra_config_file}"')
        print()
        print('RETROARCH CONFIG (partially) CONTENT')
        print()
        if ra_config:
            for var in ra_config:
                print(f'\t{var}: ', '"' + ra_config[var] + '"')
        print()
        print('SCRIPT CONFIG CONTENT')
        print()
        if settings_file:
            with open(settings_file, 'r') as data:
                for line in data.readlines():
                    print('\t' + line, end='')
        sys.exit(0)

    if not ra_dir or not ra_dir.is_dir():
        message = f'Could not find RetroArch config folder: "{ra_dir}"'
        stderr(message, arguments.quiet)
        sys.exit(1)

    elif not ra_config:
        message = 'Could not find or load RetroArch config: "{ra_config_file}"'
        stderr(message, arguments.quiet)
        sys.exit(1)

    if arguments.fullscreen:
        fullscreen = True
    else:
        fullscreen = settings.get('retroarch', 'force_fullscreen',
                                  fallback=False)

    playlist_file = get_playlist_file(arguments.playlist, ra_config)
    playlist_data = get_playlist_data(playlist_file)
    playlist_item_path = get_playlist_item(playlist_data, 'path')

    if arguments.dir:
        dir_files = get_dir_files(arguments.dir)
    else:
        dir_files = []

    roms_list = get_roms_list(arguments.nostdin, arguments.rom, arguments.game,
            playlist_item_path, dir_files)

    if roms_list:
        if arguments.uniq:
            roms_list = get_duplicates_removed(roms_list)
        if arguments.filter_ext:
            for romfilter in arguments.filter_ext:
                roms_list = get_filtered_list_ext(roms_list, romfilter)
        if arguments.filter_names:
            for romfilter in arguments.filter_names:
                roms_list = get_filtered_list_names(roms_list, romfilter)
        if arguments.filter:
            for romfilter in arguments.filter:
                roms_list = get_filtered_list(roms_list, romfilter)
        if arguments.sort_ext:
            roms_list.sort(key=lambda path: path.suffix.lower())
        elif arguments.sort_names:
            roms_list.sort(key=lambda path: path.stem.lower())
        elif arguments.sort:
            roms_list.sort(key=lambda path: path.as_posix().lower())
        if valid_mode:
            roms_list = get_valid_list(roms_list, settings, valid_mode)

        if arguments.ls:
            for path in roms_list:
                print(path.as_posix())

        if arguments.menu == 'rofi':
            rom_path = get_rom_byrofi(roms_list)
        elif arguments.menu == 'dmenu':
            rom_path = get_rom_bydmenu(roms_list)
        else:
            rom_path = get_rom_byindex(roms_list, arguments.index)

        if rom_path:
            rom_path = get_path(rom_path)
            if arguments.libretro:
                if '/' in arguments.libretro:
                    core_path = get_path(arguments.libretro)
                else:
                    core_path = get_core_path_byfilename(
                            arguments.libretro,
                            pathlib.Path(ra_config['libretro_directory'])
                    )
                core_name = ''
            else:
                if arguments.core:
                    core_name = arguments.core
                else:
                    core_name = get_core_name(settings, rom_path)

                core_path = get_core_path(
                        settings,
                        core_name,
                        pathlib.Path(ra_config['libretro_directory']))
        else:
            rom_path = ''
            core_path = ''
            core_name = ''
    else:
        rom_path = ''
        core_path = ''
        core_name = ''

    if arguments.record:
        if arguments.record_disable_macros:
            record_file = get_path(arguments.record)
        elif rom_path:
            record_file = get_record_file(arguments.record, rom_path)
        else:
            record_file = ''
    else:
        record_file = ''

    if arguments.nopatch:
        patch_file = ''
        patch_format = ''
    elif arguments.patch:
        patch_file, patch_format = get_patch_file(arguments.patch)
        if patch_file:
            real_rom_path = rom_path
            link_name = patch_file.name + '_' + rom_path.name
            rom_path = pathlib.Path(temp_dir.name + '/' + link_name)
            rom_path.symlink_to(real_rom_path)
        else:
            patch_file = ''
            patch_format = ''
            link_name = ''
    else:
        patch_file = ''
        patch_format = ''

    if arguments.ls and not roms_list:
        message = f'Could not find rom or playlist is empty: "{playlist_file}"'
        stderr(message, arguments.quiet)
        sys.exit(1)
    elif not rom_path or not rom_path.exists():
        message = f'Could not find rom: "{rom_path}"'
        stderr(message, arguments.quiet)
        sys.exit(1)
    elif not get_mimetype(rom_path) == 'binary':
        message = f'Path to rom file is not in a binary format: "{rom_path}"'
        stderr(message, arguments.quiet)
        sys.exit(1)
    elif not core_path or not core_path.exists():
        if arguments.libretro:
            message = ('Could not find core path:'
                      f' "{core_path}"')
        else:
            message = ('Could not find core name and path:'
                      f' "{core_name}={core_path}"')
        stderr(message, arguments.quiet)
        sys.exit(1)
    elif arguments.patch and not patch_file.exists():
        message = f'Could not find patch: "{patch_file}"'
        stderr(message, arguments.quiet)
        sys.exit(1)
    elif patch_file and not patch_format:
        message = f'Unsupported patch format: "{patch_file}"'
        stderr(message, arguments.quiet)
        sys.exit(3)

    command = get_command(retroarch_bin_path,
                          arguments,
                          core_path,
                          rom_path,
                          ra_config_file,
                          record_file,
                          patch_file,
                          patch_format,
                          fullscreen
    )
    if not arguments.norun:
        try:
            completed_process = subprocess.run(command,
                    capture_output=True,
                    check=True)
            #stderr(completed_process, arguments.quiet)
            if completed_process.returncode == 0:
                if arguments.what:
                    print(rom_path.as_posix())
                if arguments.which:
                    print(core_path.as_posix())
        except subprocess.CalledProcessError:
            pass
    else:
        if arguments.what:
            print(rom_path.as_posix())
        if arguments.which:
            print(core_path.as_posix())

    sys.exit(0)

