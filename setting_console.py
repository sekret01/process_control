import configparser
import json
import os
import sys
import time
import subprocess
import threading
import logging
from json import JSONDecodeError

logging.basicConfig(
    filename='logs/logs.txt',
    filemode='a',
    level=logging.INFO,
    format=f"%(levelname)s -- %(module)s -- %(asctime)s  ==>  %(message)s"
)


text_main = """
Консоль для управления и настройки процесса

Список команд:
> 1 - включение процесса подсчета
> 2 - завершение процесса подсчета
> 3 - настройка отображения процессов и программ
> 4 - очистка логов
> 5 - сменить путь сохранения файлов

> 0 - выход
"""

text_setting = """
Настройка отображения процессов

Список команд:

> 1 - просмотр отслеживаемых программ
> 2 - настройка отслеживаемых программ

> 3 - просмотр игнорируемых процессов
> 4 - настройка игнорируемых процессов

> 0 - выход
"""


def get_config() -> configparser.ConfigParser:
    configs = configparser.ConfigParser()
    configs.read("configs/config.ini", encoding='utf-8')
    return configs


def save_configs(conf) -> None:
    with open('configs/config.ini', 'w', encoding='utf-8') as f:
        conf.write(f)


def create_process() -> None:
    pwd = os.getcwd() + '\\main.py'
    subprocess.Popen(args=[pwd])


def check_status() -> str:
    conf = get_config()
    if int(conf['STATUS']['calibration']):
        return f"\033[33mCALIBRATION (30 sec)\033[0m"
    return f"\033[32mON\033[0m" if int(conf['STATUS']['working']) else f"\033[31mOFF\033[0m"


# set path saves

def set_save_path() -> None:

    try:
        logging.info("Start set save path")
        os.system('cls')
        print("Смена папки сохранения файла (1 для отмены)")
        new_path = input("Введите новый путь (конец - папка)\n\n> ")
        if new_path == '1':
            _ = input("Оставлен предыдущий путь...")
            logging.info("Path was not change")
            return
        else:
            if os.path.exists(new_path):
                logging.info(f"new path {new_path} was found")
                conf = get_config()
                conf['MAIN_SETTING']['path'] = new_path
                save_configs(conf)
            else:
                _ = input("Путь не найден...")
                logging.warning(f"New path {new_path} was not found")
    except Exception as ex:
        logging.error(f"set_save_path: {ex}")


# start / stop program

def start_program() -> None:
    conf = get_config()
    if not int(conf['STATUS']['working']):

        pwd = os.getcwd() + '\\main.pyw'
        thr = threading.Thread(target=lambda: subprocess.Popen(args=[pwd], shell=True))
        thr.start()
        print("start work...")
        time.sleep(1)

    else:
        logging.warning("attempt to launch a running application")


def finish_program() -> None:
    conf = get_config()
    conf['STATUS']['stop_work'] = '1'
    save_configs(conf)

    print("stop work...")

    while check_status() == f"\033[32mON\033[0m":
        time.sleep(0.5)

    conf = get_config()
    conf['STATUS']['stop_work'] = '0'
    save_configs(conf)


# set processes

def look_marked_apps() -> None:
    with open('data/apps.json', 'r', encoding='utf-8') as f:
        apps = json.load(f)
        text = '\n'
        for val in apps.values():
            text += f"- {val}\n"
        os.system('cls')
        print(text)
        logging.info("look_marked_apps: success")
        _ = input('\n...')


def set_marked_apps() -> None:
    os.system('cls')
    print("Добавление отслеживаемой программы\n")
    process_name = input("Введите название процесса: ")
    name = input("Введите свое название: ")

    try:
        with open("data/apps.json", 'r', encoding='utf-8') as f:
            data: dict = json.load(f)
        data[process_name] = name
        with open("data/apps.json", "w", encoding='utf-8') as f:
            json.dump(data, f)

        logging.info("success adding the marked name")
    except Exception as ex:
        logging.error(f"set_marked_apps: {ex}")
        _ = input("Не удалось добавить процесс...")


def look_ignor_processes() -> None:
    with open('data/process_ignore.json', 'r', encoding='utf-8') as f:
        process_ignore = json.load(f)
        text = '\n'
        for val in process_ignore:
            text += f"- {val}\n"
        os.system('cls')
        print(text)
        logging.info("look_ignor_processes: success")
        _ = input('\n...')


def set_ignor_processes() -> None:
    os.system('cls')
    print("Добавление игнорируемого процесса\n")
    ignor_process_name = input("Введите название процесса: ")
    try:
        with open("data/process_ignore.json", "r", encoding='utf-8') as f:
            data: list = json.load(f)
            data.append(ignor_process_name)
        with open("data/process_ignore.json", "w", encoding='utf-8') as f:
            json.dump(data, f)

        logging.info("success load ignor data")

    except JSONDecodeError as ex:
        with open("data/process_ignore.json", "w", encoding='utf-8') as f:

            logging.warning(f"set_ignor_processes: {ex}")
            json.dump([ignor_process_name], f)

    except Exception as ex:
        logging.error(f"set_ignor_processes: {ex}")


# set logs

def clear_logs() -> None:

    logging.warning("Start clearing logs")
    os.system('cls')
    print("Удаление файла с логами приведет к необратимой потере данных.")
    com = input("1 - удалить логи\n\n> ")
    if com == '1':
        with open("logs/logs.txt", "w", encoding="utf-8") as f:
            logging.info("Logs was clear")
    else:
        logging.info("logs was saved")


#  Consoles

def setting_processes() -> None:
    while True:
        os.system('cls')
        print(f"{text_setting}")

        command = input('set#> ')

        if command == '0':
            break

        elif command == '1':
            look_marked_apps()
        elif command == '2':
            set_marked_apps()

        elif command == '3':
            look_ignor_processes()
        elif command == '4':
            set_ignor_processes()



def main() -> None:
    while True:
        os.system('cls')
        print(f"{text_main}")
        print(f"WORK STATUS: {check_status()}\n")

        command = input('#> ')

        if command == '0':
            sys.exit()

        elif command == '1':
            start_program()
        elif command == '2':
            finish_program()
        elif command == '3':
            setting_processes()
        elif command == '4':
            clear_logs()
        elif command == '5':
            set_save_path()


if __name__ == '__main__':
    main()
