import json
import logging
import os.path
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import ipaddress

import paramiko
import yaml

def list_in_list(list_subnet: list) -> list:
    ip_list = []
    for i_subnet in list_subnet:
        prefix = ipaddress.ip_network(i_subnet)
        ip_list.append('ping' + ' ' + f'{prefix.hosts().__next__()}')
    return ip_list

def write_data_command_in_file(data, ip: list) -> None:
    global command
    """
    Функция, сохраняющая полученыые данные в результате опроса по файлам json

    :param data: словарь с данными
    :param ip: ip адрес железки, откуда получены данные
    :return: None
    """
    path = os.path.join(os.getcwd(), 'data', f'data_{ip}')


    if not os.path.isdir(path):
        os.mkdir(path)

    print('DATA:', data)


    with open(f'{path}/data.txt', mode='a+') as file:
        for key, value in data.items():
            print(value)
            if '!' in ''.join(value):
                file.write(f'{key} : !!!!!!!!!!!!!!!!!')
            else:
                file.write(f'{key} : ....')
            file.write('\n')

        #json.dump(result_dict, file, indent=4)


logging.getLogger('paramiko').setLevel(logging.INFO)
logging.basicConfig(
    format='%(threadName)s %(name)s %(levelname)s: %(message)s',
    level=logging.INFO)

def send_show_command(
    ip: list,
    max_bytes=60000,
    short_pause=1,
    long_pause=5,
) -> dict:
    """
    Функция для получения данных с коробки.
    :param ip: IP адрес подключения
    :param username: login Tacacs
    :param password: password Tacacs
    :param command: список команд, которые необходимо выполнить на коробке
    :param max_bytes: размер кусков данных, которые будут складываться в итоговую переменную результат
    :return: результат Dict, полученный с коробки

    P.S. в зависимости от выполняемой команды, данные подлежат дополнительной обработке для корректного вывода.
    """
    global command
    global username
    global password
    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    start_msg = '==> {} Connection: {}'
    recieved_msg = '<== {} Recieved:  {}'
    logging.info(start_msg.format(datetime.now().time(), ip))

    cl.connect(
        hostname=ip,
        username=username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
    )

    with cl.invoke_shell() as ssh:
        ssh.send("terminal length 0\n")
        time.sleep(short_pause)
        ssh.recv(max_bytes)
        result = {}
        for i_command in command:
            ssh.send(f"{i_command}\n")
            ssh.settimeout(5)
            output = ""
            while True:
               try:
                   part = ssh.recv(max_bytes).decode("utf-8")
                   output += part
                   time.sleep(0.5)
               except socket.timeout:
                   break
            result[i_command] = output.split('\r\n')
        logging.info(recieved_msg.format(datetime.now().time(), ip))

        return result




if __name__ == '__main__':

    with open('user_data.yaml') as f:
        data_from_file = yaml.safe_load(f)
        ip_list = data_from_file['ip_list'].split(',')
        username = data_from_file['username']
        password = data_from_file['password']

    with open('in_data.yaml') as f:
        ip_list_network = yaml.safe_load(f)


    start_time = time.time()
    command = list_in_list(ip_list_network.split())[:2]
    with ThreadPoolExecutor(max_workers=5) as executor:
        for ip, data in zip(ip_list, executor.map(send_show_command, ip_list)):

            write_data_command_in_file(data, ip)

    end_time = time.time()
    print(f'Время работы заняло {end_time-start_time}....')
