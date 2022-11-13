import ipaddress
import platform
import subprocess
import tabulate


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


def host_range_ping(hosts_list: list, hosts_range: int) -> None:
    param = "-n" if platform.system().lower() == 'windows' else "-c"
    for host in hosts_list:
        try:
            main_chunk = host.split('.')[:3]
            start = _ - 1 if (_ := int(*host.split('.')[-1:])) > 0 else _
            subnet = list(ipaddress.ip_network(f'{".".join(main_chunk)}.0/24').hosts())
            for i, subnet_host in enumerate(subnet[start:]):
                if i == hosts_range:
                    break
                command = ['ping', param, '1', subnet_host.exploded]
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate()
                if process.returncode == 0:
                    print(f'Узел {subnet_host} доступен')
                else:
                    print(f'Узел {subnet_host} недоступен')
            else:
                print('Запрашиваемый диапазон превышает допустимые условия: требуется изменение предпоследнего октета')
        except ValueError:
            pass


def host_range_ping_tab(hosts_list: list, hosts_range: int) -> None:
    param = "-n" if platform.system().lower() == 'windows' else "-c"
    for host in hosts_list:
        tested_hosts = {
            'reachable': [],
            'unreachable': [],
        }
        try:
            main_chunk = host.split('.')[:3]
            start = _ - 1 if (_ := int(*host.split('.')[-1:])) > 0 else _
            subnet = list(ipaddress.ip_network(f'{".".join(main_chunk)}.0/24').hosts())
            for i, subnet_host in enumerate(subnet[start:]):
                if i == hosts_range:
                    break
                command = ['ping', param, '1', subnet_host.exploded]
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate()
                if process.returncode == 0:
                    tested_hosts['reachable'].append(subnet_host.exploded)
                else:
                    tested_hosts['unreachable'].append(subnet_host.exploded)
            else:
                print('Запрашиваемый диапазон превышает допустимые условия: требуется изменение предпоследнего октета')
            print(tabulate.tabulate(tested_hosts, headers='keys', tablefmt='grid'))
        except ValueError:
            pass


if __name__ == '__main__':
    hosts = ['192.168.0.1', '192.168.0.8', '127.0.0.1', '0.0.0.0', 'yandex.ru', 'rutracker.org', ]
    # host_ping(hosts)
    # host_range_ping(hosts, 3)
    host_range_ping_tab(hosts, 3)
