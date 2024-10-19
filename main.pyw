import subprocess
import sys
import os
import time
import threading
import configparser
import json
import datetime as dt
import pickle
import pathlib
import logging

logging.basicConfig(
    filename='logs/logs.txt',
    filemode='a',
    level=logging.INFO,
    format=f"%(levelname)s -- %(module)s -- %(asctime)s  ==>  %(message)s"
)



CONF_PATH = "configs/config.ini"
PICKLE_PATH = "configs/last_save.pickle"


def get_apps() -> dict:
    with open('data/apps.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def format_date_now():
    d_n = dt.datetime.now()
    return f"{d_n.day:0>2}_{d_n.month:0>2}_{d_n.year:0>2}"


def get_config() -> configparser.ConfigParser:
    try:
        configs = configparser.ConfigParser()
        configs.read(CONF_PATH, encoding='utf-8')
        return configs

    except Exception as ex:
        logging.error(f"get_config:  {ex}")
        raise SystemExit


# ================================================  CALIBRATION  =======================================================

def calibration():

    logging.info("start calibration")

    try:

        global PATH, TIME, CONF_PATH, PICKLE_PATH, CALIBRATION

        conf = get_config()
        conf['STATUS']['calibration'] = '1'
        save_configs(conf)

        PATH = "./configs/for_calibration/data.txt"
        CONF_PATH = "./configs/for_calibration/calibration_config.ini"
        PICKLE_PATH = "./configs/for_calibration/calibration_last_save.pickle"
        TIME = 30

        change_work_status()

        if continuation_of_the_day():
            with open('configs/for_calibration/calibration_last_save.pickle', 'rb') as f:
                processes_time = pickle.load(f)
        else:
            conf = get_config()
            conf['DATE_FILE']['date'] = format_date_now()
            save_configs(conf)
            processes_time = ProcessesTime(looking_for)

        writer = threading.Thread(target=write_time, args=[processes_time], daemon=True)

        start_time = time.time()
        counter = 0

        while counter < TIME:
            process_set = create_processes_names_set()

            if not writer.is_alive():
                writer = threading.Thread(target=write_time, args=[processes_time], daemon=True)
                writer.start()
            processes_time.update(process_set)
            save_pickle(processes_time)

            if is_stop_work():
                write_time(processes_time, pause=0)
                save_pickle(processes_time)
                change_work_status('0')
                raise SystemExit

            time.sleep(1)
            counter += 1

        write_time(processes_time, pause=0)
        save_pickle(processes_time)
        change_work_status('0')

        end_time = time.time()
        diff = int(end_time - start_time)

        CONF_PATH = "configs/config.ini"
        PICKLE_PATH = "configs/last_save.pickle"
        PATH = pathlib.Path(get_config().get('MAIN_SETTING', 'path')) / f"{format_date_now()}.txt"

        conf = get_config()
        conf['STATUS']['calibration'] = '0'
        conf['MAIN_SETTING']['calibration'] = str(round(diff/TIME, 3))
        save_configs(conf)

        TIME = int(get_config().get('MAIN_SETTING', 'pause'))
        CALIBRATION = float(get_config()['MAIN_SETTING']['calibration'])

        logging.info("successful calibration")

    except Exception as ex:
        logging.error(f"calibration:  {ex}")
        sys.exit()

# ======================================================================================================================


PATH = pathlib.Path(get_config().get('MAIN_SETTING', 'path')) / f"{format_date_now()}.txt"
TIME = int(get_config().get('MAIN_SETTING', 'pause'))
CALIBRATION = float(get_config()['MAIN_SETTING']['calibration'])
looking_for = get_apps()


class ProcessesTime:
    def __init__(self, names: dict[str, str]):
        self.processes: dict[str, int] = dict()
        self.markes: dict[str, str]  = names

    def update_names(self, names: dict[str, str]) -> None:
        self.markes: dict[str, str] = names

    def update(self, processes: set):
        for process in processes:
            time_process = self.processes.setdefault(process, 0)
            self.processes[process] = time_process + 1

    def get_info(self) -> tuple:
        marked_processes = ''
        all_processes = ''

        for i, v in self.processes.items():
            all_processes += f"{i:<35s} {self._format_time(v)}\n"
            if i in self.markes:
                marked_processes += f"{self.markes[i]:<35s} {self._format_time(v)}\n"

        return marked_processes, all_processes

    def _format_time(self, sec: int) -> str:
        hours = sec // 60**2
        minutes = (sec - hours*60*60) // 60
        seconds = sec - hours*60*60 - minutes*60
        return f"{hours:0>2}:{minutes:0>2}:{seconds:0>2}"


def continuation_of_the_day() -> bool:

    conf = get_config()
    date_now = format_date_now()
    last_time = conf['DATE_FILE']['date']

    return date_now == last_time


def write_process(data: dict, short: bool = False):

    if short:
        for el in data.values():
            print(f'"{el["name"]}",')
    else:
        for el in data.values():
            for it, val in el.items():
                print(f"{it}  {val}")
            print(f"\n")


def create_processes_names_list() -> list[str]:
    try:
        all_table = []
        proc = subprocess.Popen(["tasklist", "/FO", "CSV", "/FI", "STATUS eq running", "/NH"],
                                shell=True,
                                stdout=subprocess.PIPE
                                )

        for out in proc.stdout.readlines():
            part = out.decode(encoding='utf-8', errors='ignore').strip().split(',')[0].replace('"', '').strip()
            if no_ignore_process_name(part):
                all_table.append(part)

        return all_table
    except Exception as ex:
        logging.error(f"create_processes_names_list:  {ex}")
        raise SystemExit


def create_processes_names_set() -> set:
    processes_list = create_processes_names_list()

    process_set = set()
    for el in processes_list:
        process_set.add(el)
    return process_set


def no_ignore_process_name(process: str):
    with open('data/process_ignore.json', 'r', encoding='utf-8') as f:
        ignore_names = json.load(f)
    return process not in ignore_names


# save times


def write_time(processes_time: ProcessesTime, pause: int = TIME):

    global PATH

    try:
        with open(PATH, 'w', encoding='utf-8') as f:
            marked_proc, all_proc = processes_time.get_info()
            text = f"{'  LOOKING  ':=^40s}\n\n{marked_proc}\n\n{'  ALL  ':=^40s}\n\n{all_proc}"
            f.write(text)
        save_pickle(processes_time)
        time.sleep(pause)
    except Exception as ex:
        logging.error(f"write_time:  {ex}")


def save_pickle(processes: ProcessesTime) -> None:
    try:
        with open(PICKLE_PATH, 'wb') as f:
            pickle.dump(processes, f)
    except Exception as ex:
        logging.error(f"save_pickle:  {ex}")


def save_configs(conf) -> None:
    try:
        with open(CONF_PATH, 'w', encoding='utf-8') as f:
            conf.write(f)
    except Exception as ex:
        logging.error(f"save_configs:  {ex}")

def change_work_status(status = '1') -> None:
    conf = get_config()
    conf['STATUS']['working'] = str(status)
    save_configs(conf)

    logging.info(f"set work status: {status}")


def is_stop_work():
    conf = get_config()
    return int(conf['STATUS']['stop_work'])


def main():

    logging.info("start main program")

    change_work_status()

    if continuation_of_the_day() and os.path.exists(PICKLE_PATH):
        with open(PICKLE_PATH, 'rb') as f:

            try:
                processes_time = pickle.load(f)
                logging.info("successful load pickle")
                processes_time.update_names(looking_for)
                logging.info("continuation of old timer")
            except Exception as ex:
                logging.error(f"main:  {ex}")

    else:
        conf = get_config()
        conf['DATE_FILE']['date'] = format_date_now()
        save_configs(conf)
        processes_time = ProcessesTime(looking_for)
        logging.info("create new timer")

    writer = threading.Thread(target=write_time, args=[processes_time], daemon=True)
    logging.info("create writer")

    try:

        while True:
            process_set = create_processes_names_set()

            if not writer.is_alive():
                writer = threading.Thread(target=write_time, args=[processes_time], daemon=True)
                writer.start()
            processes_time.update(process_set)
            save_pickle(processes_time)

            if is_stop_work():
                write_time(processes_time, pause=0)
                save_pickle(processes_time)
                change_work_status('0')
                raise SystemExit


            time.sleep(round(1/CALIBRATION, 3))




    except KeyboardInterrupt as ex:
        write_time(processes_time, pause=0)
        save_pickle(processes_time)
        change_work_status('0')
        logging.warning("stop program with ctrl+c")


    except Exception as ex:
        write_time(processes_time, pause=0)
        save_pickle(processes_time)
        change_work_status('0')
        logging.error(f"main:  {ex}")

    except SystemExit as ex:
        write_time(processes_time, pause=0)
        save_pickle(processes_time)
        change_work_status('0')
        logging.info("STOP PROGRAM")
        sys.exit()




if __name__ == '__main__':

    logging.info("START PROGRAM")
    try:

        calibration()
        main()
    except Exception as ex:

        logging.error(ex)
