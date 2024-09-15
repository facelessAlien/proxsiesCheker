import os
import sys

from art import text2art
from download_proxies import download
from proxy_check import main_check


class ProxiesChecker:
    DEFAULT_URL: str = 'https://google.com/'
    DEFAULT_SRC_PROXIES_LIST: str = 'proxies.txt'
    DEFAULT_OUTPUT_PROXIES_LIST: str = 'good_proxies.txt'
    MODE: str = 'w'

    WORKING_MODE_DICT: dict = {'DOWNLOAD_AND_CHECK': False,
                               'ONLY_CHECK': False,
                               'ONLY_DOWNLOAD': False
                               }

    def start_menu(self):
        try:
            working_mode = input('1. Download and check\n'
                                 '2. Only check\n'
                                 '3. Only Download\n'
                                 )
            if working_mode == '1':
                self.WORKING_MODE_DICT['DOWNLOAD_AND_CHECK'] = True
            elif working_mode == '2':
                self.WORKING_MODE_DICT['ONLY_CHECK'] = True
            elif working_mode == '3':
                self.WORKING_MODE_DICT['ONLY_DOWNLOAD'] = True
            else:
                self.start_menu()
        except KeyboardInterrupt:
            sys.exit('Exit...')


    def customisation(self):
        if self.WORKING_MODE_DICT.get('DOWNLOAD_AND_CHECK') or self.WORKING_MODE_DICT.get('ONLY_CHECK'):
            url = input('Site for checking (default https://google.com/): https://')
            user_url = url if url else 'google.com/'
            site_to_check = 'https://' + user_url if user_url else self.DEFAULT_URL
            return site_to_check, self.WORKING_MODE_DICT
        if self.WORKING_MODE_DICT.get('ONLY_DOWNLOAD'):
            return None, self.WORKING_MODE_DICT


def cmd_clear():
    system_name = os.name
    clear_console = 'cls' if system_name == 'nt' else 'clear'
    os.system(clear_console)


def main():
    # Создание баннера с использованием текста
    banner = text2art("ProxiesChecker", font="lucky1")
    print(banner)

    proxy_checker = ProxiesChecker()
    proxy_checker.start_menu()
    site_to_check, work_mode = proxy_checker.customisation()
    if work_mode.get('DOWNLOAD_AND_CHECK') is True:
        cmd_clear()
        print('DOWNLOAD AND CHECK\n')
        download('proxies.txt')
        main_check(site_to_check)
    if work_mode.get('ONLY_CHECK') is True:
        cmd_clear()
        print('ONLY CHECK\n')
        try:
            main_check(site_to_check)
        except:
            print("No such file: 'proxies.txt'")
    if work_mode.get('ONLY_DOWNLOAD') is True:
        cmd_clear()
        print('ONLY DOWNLOAD\n')
        download('proxies.txt')


if __name__ == '__main__':
    main()
