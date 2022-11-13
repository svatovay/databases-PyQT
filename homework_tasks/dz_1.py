import ipaddress
import platform
import subprocess
import chardet


def host_ping(hosts_list: list) -> None:
    param = "-n" if platform.system().lower() == 'windows' else "-c"
    for host in hosts_list:
        try:
            ipv4 = ipaddress.ip_address(host)
            command = ['ping', param, '3', ipv4.exploded]
        except ValueError:
            command = ['ping', param, '3', host]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        if process.returncode == 0:
            print(f'Узел {host} доступен')
        else:
            print(f'Узел {host} недоступен')


def host_range_ping():
    pass


def host_range_ping_tab():
    pass


if __name__ == '__main__':
    hosts = ['192.168.0.1', '192.168.0.8', '127.0.0.1', '0.0.0.0', 'yandex.ru', 'rutracker.org', ]
    host_ping(hosts)
    # host_range_ping()
    # host_range_ping_tab()
