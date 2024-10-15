import configparser
import json
import os
import sys
import time
import subprocess
import threading
import logging

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
    configs.read("configs/config.ini")
    return configs


def save_configs(conf):
    with open('configs/config.ini', 'w') as f:
        conf.write(f)


def create_process():
    pwd = os.getcwd() + '\\main.py'
    subprocess.Popen(args=[pwd])


def check_status():
    conf = get_config()
    if int(conf['STATUS']['calibration']):
        return f"\033[33mCALIBRATION (30 sec)\033[0m"
    return f"\033[32mON\033[0m" if int(conf['STATUS']['working']) else f"\033[31mOFF\033[0m"



def start_program():
    conf = get_config()
    if not int(conf['STATUS']['working']):

        pwd = os.getcwd() + '\\main.pyw'
        thr = threading.Thread(target=lambda: subprocess.Popen(args=[pwd], shell=True))
        thr.start()
        print("start work...")
        time.sleep(1)

    else:
        logging.warning("attempt to launch a running application")



def finish_program():
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

def look_marked_apps():
    with open('data/apps.json', 'r', encoding='utf-8') as f:
        apps = json.load(f)
        text = '\n'
        for val in apps.values():
            text += f"- {val}\n"
        os.system('cls')
        print(text)
        logging.info("look_marked_apps: success")
        _ = input('\n...')


def set_marked_apps():
    ...


def look_ignor_processes():
    with open('data/process_ignore.json', 'r', encoding='utf-8') as f:
        process_ignore = json.load(f)
        text = '\n'
        for val in process_ignore:
            text += f"- {val}\n"
        os.system('cls')
        print(text)
        logging.info("look_ignor_processes: success")
        _ = input('\n...')


def set_ignor_processes():
    ...


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
            ...

        elif command == '3':
            look_ignor_processes()
        elif command == '4':
            ...



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


if __name__ == '__main__':
    main()
