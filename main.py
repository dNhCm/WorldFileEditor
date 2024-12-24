from datetime import datetime
import os
import sqlite3
from typing import Callable, Optional

import pywintypes
import win32file
import win32con

import pyfiglet as figlet
from colorama import Fore, init
import inquirer
from rich.console import Console
from rich.markdown import Markdown


# Globals
init()
console = Console()
worlds_path = 'worlds'
backup_path = 'backup'


# Interface and Interactive part of project
class UI:
    @classmethod
    def restore_gametick(cls) -> Optional[str]:
        world = cls.choose_world()
        Tech.update_gametick(worlds_path + '/' + world, 0)

    @classmethod
    def set_gametick(cls) -> Optional[str]:
        world = cls.choose_world()

        answer = inquirer.prompt([
            inquirer.Text(
                'game_ticks',
                message="How many game ticks to set?",
                default=0,
                validate=lambda _, x: x.isdigit() or "Please enter a valid number"
            )
        ])

        Tech.update_gametick(worlds_path + '/' + world, int(answer['game_ticks']))

    @staticmethod
    def choose_world() -> str:
        return inquirer.prompt([
            inquirer.List(
                'worlds',
                message="Choose World",
                choices=list(os.listdir(worlds_path))
            )
        ])['worlds']

    @staticmethod
    def help() -> Optional[str]:
        console.print(Markdown("""
Here no text yet
""".strip()))

    @staticmethod
    def exit_func():
        exit_font = figlet.Figlet(font='amc_thin')
        print(Fore.BLUE + exit_font.renderText("Thank you for being with us!"))
        exit()

    @classmethod
    def main(cls):
        functions: dict[str, Callable] = {
            "Restore World's Game Tick": cls.restore_gametick,
            "Set World's Game Tick": cls.set_gametick,
            "Help": cls.help,
            "Exit": cls.exit_func,
        }

        title_font = figlet.Figlet(font='amc_slash')
        print(Fore.CYAN + title_font.renderText("World File Editor") + Fore.RESET)
        subtitle_font = figlet.Figlet(font='amc_thin')
        subtitle_text: Callable = lambda text: subtitle_font.renderText(text)
        print(Fore.WHITE + subtitle_text('for') + Fore.YELLOW + subtitle_text('Scrap') + Fore.LIGHTYELLOW_EX + subtitle_text('Mechanic') + Fore.RESET)

        while True:
            answer = inquirer.prompt([
                inquirer.List(
                    'menu',
                    message="Choose The Action",
                    choices=list(functions.keys())
                )
            ])['menu']
            response = functions[answer]()
            if response:
                print(Fore.RED + response)
            else:
                print(Fore.GREEN + "\n + The Action has been done!")
            print()


# Technical part of project
class Tech:
    @staticmethod
    def get_modified_date(file_path: str) -> tuple[float, float]:
        mod_time = os.path.getmtime(file_path)
        return mod_time, mod_time

    @staticmethod
    def set_modified_date(file_path: str, date: tuple[float, float]):
        os.utime(file_path, date)

    @staticmethod
    def get_creation_date(file_path: str) -> datetime:
        creation_time = os.path.getctime(file_path)
        return datetime.fromtimestamp(creation_time)

    @staticmethod
    def set_creation_date(file_path: str, creation_date: datetime):
        filetime = pywintypes.Time(creation_date)

        handle = win32file.CreateFile(
            file_path,
            win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            0,
            None
        )

        win32file.SetFileTime(handle, filetime, None, None)
        handle.close()

    @classmethod
    def copy_file(cls, file_path: str, desired_path: str):
        desired_path = desired_path + '/' + file_path.split('/')[-1]
        open(desired_path, 'wb').write(open(file_path, 'rb').read())
        creation_date = cls.get_creation_date(file_path)
        cls.set_creation_date(desired_path, creation_date)
        cls.set_modified_date(desired_path, cls.get_modified_date(file_path))

    @classmethod
    def update_gametick(cls, file_path: str, v: int):
        cls.copy_file(file_path, backup_path)
        mod_date = cls.get_modified_date(file_path)
        conn = sqlite3.connect(file_path)
        c = conn.cursor()
        c.execute(f"UPDATE Game SET gametick = {v};")
        conn.commit()
        conn.close()
        cls.set_modified_date(file_path, mod_date)


def main():
    UI.main()


if __name__ == "__main__":
    main()
