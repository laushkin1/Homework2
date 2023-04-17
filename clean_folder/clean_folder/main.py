from pathlib import Path
import shutil
import sys
import re

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")


TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()

KN_EXT = set()
UN_EXT = set()

EXTANSIONS = {
    'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
    'video': ['AVI', 'MP4', 'MOV', 'MKV'],
    'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
    'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
    'archives': ['ZIP', 'GZ', 'TAR'],
    'unknown_extansions': []
}

ALL_FILES = {
    'images': [],
    'video': [],
    'documents': [],
    'audio': [],
    'archives': [],
    'unknown_extansions': []
}


def run():
    global path_to_folder
    try:
        path_to_folder = Path(sys.argv[1])
        scan_folder(path_to_folder)
        show_all_files()
        print('\nSorting was successful!')
    except IndexError:
        print('Enter the full path to a folder you want to sort just after command "clean-folder"!')
    finally:
        print('Thank`s!')


def scan_folder(path_to_folder: Path) -> None:
    for element in path_to_folder.iterdir():
        if element.is_dir() and element in EXTANSIONS.keys():
            continue
        elif element.is_dir():
            if any(element.iterdir()):
                scan_folder(element)
            else:
                element.rmdir()  
        else:
            sort_file(element)
            handle_file(element)
            if not any(element.parent.iterdir()): element.parent.rmdir()


def normalize_name(path_to_file: Path) -> str:  
    if not bool(path_to_file.suffix):
        path_to_file = path_to_file.parent / f'space{path_to_file.name}'
    name = path_to_file.name.split('.')
    name[0] = re.sub(r'\W', '_', name[0].translate(TRANS))
    new_name = '.'.join(name)
    return new_name


def unpack_archive(path_to_archive: Path, folder: str) -> None:  
    new_folder = path_to_folder / folder
    if not new_folder.exists():
        new_folder.mkdir(exist_ok=True, parents=True)
    ALL_FILES[folder].append(normalize_name(path_to_archive))
    shutil.unpack_archive(path_to_archive, new_folder / normalize_name(path_to_archive).split('.')[0])
    Path.unlink(path_to_archive)


def get_ext(path_to_file: Path) -> str:
    if bool(path_to_file.suffix):
        ext = path_to_file.suffix[1:].upper()
        return ext
    else:
        ext = path_to_file.name[1:].upper()
        return ext


def handle_file(path_to_file: Path) -> None:  
    ext = get_ext(path_to_file)
    for key, value in EXTANSIONS.items():
        if ext in value:
            ALL_FILES[key].append(normalize_name(path_to_file))
            return
    ALL_FILES['unknown_extansions'].append(normalize_name(path_to_file))


def sort_file(path_to_file: Path) -> None:  
    ext = get_ext(path_to_file)
    for key, value in EXTANSIONS.items():
        if ext in value:
            KN_EXT.add(ext)
            if key == 'archives':
                unpack_archive(path_to_file, key)
                return
            else:
                move_file(path_to_file, key)
                return
    UN_EXT.add(ext)
    move_file(path_to_file, 'unknown_extansions')


def move_file(path_to_file: Path, folder: str) -> None:
    new_folder = path_to_folder / folder
    if not new_folder.exists():
        new_folder.mkdir(exist_ok=True, parents=True)
    try:
        shutil.copyfile(path_to_file, new_folder / Path(normalize_name(path_to_file)))
        Path.unlink(path_to_file)
    except:
        print(f'Can`t move this file: {normalize_name(path_to_file)}!')


def show_all_files() -> None:
    print(f"Images: {' ** '.join(ALL_FILES['images'])}\n")
    print(f"Video: {' ** '.join(ALL_FILES['video'])}\n")
    print(f"Documents: {' ** '.join(ALL_FILES['documents'])}\n")
    print(f"Audio: {' ** '.join(ALL_FILES['audio'])}\n")
    print(f"Archives: {' ** '.join(ALL_FILES['archives'])}\n")
    print(f"Unknown_extansions: {' ** '.join(ALL_FILES['unknown_extansions'])}\n")
    print('*' * 60)
    print(f'\nUNKNOWN EXTANSIONS: {UN_EXT}\n')
    print(f'KNOWN EXTANSIONS: {KN_EXT}')


if __name__ == '__main__':
    run()
