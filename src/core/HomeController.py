import os
import random
import shutil
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import requests
import undetected_chromedriver as uc
import time
from src.core.SeleniumFunctions import BrowserFunctions
from selenium.webdriver.common.by import By
import datetime,traceback
sys.path.append(os.getcwd()) 

class ProxyExtensionNew:
    def __init__(self,profile_path, ip, port, username=None, password=None,mode = None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.mode = mode
        self.directory = os.path.join(profile_path, "proxy_extension")
        print(f"==>> self.directory: {self.directory}")
        self.create_extension()

    def create_extension(self):
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)
        os.makedirs(self.directory)

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = f"""
        var config = {{
                mode: "fixed_servers",
                rules: {{
                  singleProxy: {{
                    scheme: "{self.mode}",
                    host: "{self.ip}",
                    port: parseInt({self.port})
                  }},
                  bypassList: ["localhost"]
                }}
              }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{self.username}",
                    password: "{self.password}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {{urls: ["<all_urls>"]}},
                    ['blocking']
        );
        """

        with open(os.path.join(self.directory, 'manifest.json'), 'w') as f:
            f.write(manifest_json)
        
        with open(os.path.join(self.directory, 'background.js'), 'w') as f:
            f.write(background_js)

    def remove_extension(self):
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)


class GetInfomationThread(QThread):
    update_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    BASE_URL = 'https://trends.google.com/trends/'

    def __init__(self,mode,kw):
        super().__init__()
        modes = {
            'one_day': f'https://trends.google.com.vn/trends/explore?date=now%201-d&geo=US&q={kw}&hl=en',
            'one_hour': f'https://trends.google.com.vn/trends/explore?date=now%201-H&geo=US&q={kw}&hl=en',
            'four_hours': f'https://trends.google.com.vn/trends/explore?date=now%204-H&geo=US&q={kw}&hl=en',
            'seven_days': f'https://trends.google.com.vn/trends/explore?date=now%207-d&geo=US&q={kw}&hl=en'
        }
        self.mode = mode
        self.kw = kw
        self.DOWNLOAD_DIRECTORY = os.path.join(os.getcwd(), 'downloads',f'downloads_{mode}')
        self.__clear_download_folder()
        self.proxy = self.checkProxyBeforeStart()
        self.profilePath = os.path.join(os.getcwd(), 'profiles_browser',mode)
        self.url = modes[mode]
        self.telegram = {
            'shirt': -1001561938466,
            'sweatshirt': -328245863,
            't shirt': -321258537,
            'hoodie': -382089497,
            'coffee mug': -231741228,
            'poster': -374400899,
            'sticker': -353860197,
            'hat': -324682703,
            'sweater': -393764434,
            'blanket': -296954526,
            'mug' : -377721611
        }
        self.isForceClosed = False
        self.browser = None
        
        
        

    
    def run(self):
        while not self.isForceClosed:
            driver = self.startBrowser()
            try:
                self.error_signal.emit(f'Luồng {self.mode} - Khởi tạo trình duyệt thất bại bởi vì: <br>{driver[1]}')
                return
            except:
                pass
            browser = BrowserFunctions(driver)
            self.browser = browser
            browser.get('http://gooogle.com/')
            browser.get(self.url)
            time.sleep(3)
            browser.driver.refresh()
            time.sleep(2)
            
            while not self.isForceClosed:
                oops = browser.find(By.XPATH,"//p[contains(text(), 'Oops! Something went wrong')]")
                if oops:
                    time.sleep(5)
                    browser.driver.refresh()
                else:
                    break

            relatedq = browser.find(By.XPATH,"//div[contains(text(), 'Related queries')]")
            if not relatedq:
                self.error_signal.emit(f'Luồng {self.mode} - Không tìm được vùng Related queries từ Google Trends')
                return
            browser.scrollToElement(relatedq)
            nodata = browser.find(By.XPATH,"""//p[text()="Hmm, your search doesn't have enough data to show here."]""")
            if nodata:
                self.error_signal.emit(f'Luồng {self.mode} - Vùng Related queries từ Google Trends không hề có dữ liệu!')
                return
            # btnDownload = browser.find(By.XPATH,"""//div[contains(text(), 'Related queries')]/..//button[@class="widget-actions-item export"]""")
            # btnDownload.click()
            # time.sleep(3)
            # new_name = f'{self.kw}_{self.mode}.csv'
            # # Rename the file
            # os.rename(os.path.join(self.DOWNLOAD_DIRECTORY, self.__latest_download_file()),
            #             os.path.join(self.DOWNLOAD_DIRECTORY, new_name))
            # self.send_message_to_telegram(
            #         file_directory=os.path.join(self.DOWNLOAD_DIRECTORY, new_name),
            #         time_frame=self.mode,
            #         chat_id=self.telegram[self.kw]
            #     )
        
    
    def send_message_to_telegram(self,file_directory: str, time_frame: str, chat_id):
        def __parse_message():
            with open(file_directory, 'r', encoding='utf8') as f:
                text = f.read()

            if text.find('RISING') == -1:
                return f'Không có từ khóa nào trong vòng {time_frame} qua'

            # If exist RISING keyword
            rising_part = text[text.find('RISING'):]

            # Remove RISING
            rising_part = rising_part.replace('RISING', '')
            rising_part = rising_part.strip()

            # Split data
            data = rising_part.split('\n')

            # Extract keywords and percentages
            keywords = [row.split(',')[0] for row in data]
            percentages = [row.split(',')[-1] for row in data]

            # Create a list of lists for the table
            table_data = [[keyword, percentage]
                        for keyword, percentage in zip(keywords, percentages)]

            # Create the table in MarkdownV2 format for Telegram message
            table_md = "```\n"  # Start MarkdownV2 code block
            # Table headers
            table_md += "{:<30} {:<10}\n".format("Keywords", "Trending")
            table_md += "-" * 42 + "\n"  # Separator line
            for row in table_data:
                table_md += "{:<30} {:<10}\n".format(row[0], row[1])  # Table rows
            table_md += "```"  # End MarkdownV2 code block

            return table_md
        time_now = datetime.datetime.now().strftime("%d/%m/%Y ---- %H:%M:%S")
        data = f'Send at: {time_now}\n' + \
            __parse_message()
        response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', data={
            'chat_id': chat_id,
            'text': data,
            "parse_mode": "Markdown"
        })

        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(
                f"Failed to send the message. Status code: {response.status_code}")

    def checkProxyBeforeStart(self):
        path = os.path.join(os.getcwd(), 'proxies', 'proxies.txt')
        listProxies = self.get_proxies_list(path)
        while True:
            proxy = random.choice(listProxies)
            res = self.proxy_check(proxy,timeout=5)
            if res:
                return proxy
        
    def startBrowser(self):
        opts = uc.ChromeOptions()
        opts.add_argument(f"--window-size={random.randint(1024,1600)},{random.randint(768,960)}")
    
        opts.add_argument(f"--disable-features=PrivacySandboxSettings4")
        opts.add_argument("--mute-audio")
        opts.add_argument('--password-store=basic')
        

        # opts.add_argument('--disable-features=PrivacySandboxSettings4')
        opts.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            },
        )

        rtcBlockExts = r'.\webrtcblockext'
        usernameProxy = self.proxy[2]
        print(f"==>> usernameProxy: {usernameProxy}")
        passwordProxy = self.proxy[3]
        print(f"==>> passwordProxy: {passwordProxy}")
        proxy_extension = ProxyExtensionNew(self.profilePath,self.proxy[0], int(self.proxy[1]), usernameProxy, passwordProxy,'http')
        opts.add_argument(f"--load-extension={proxy_extension.directory},{os.path.abspath(rtcBlockExts)}")
        try:
            driver = uc.Chrome(options=opts,user_data_dir=self.profilePath,driver_executable_path=os.path.abspath('chromedriver.exe'),keep_alive=False,no_sandbox=False,use_subprocess=False)
        except:
            print(traceback.format_exc())
            return [False,traceback.format_exc()]
        return driver

    def __clear_download_folder(self):
        try:
            shutil.rmtree(self.DOWNLOAD_DIRECTORY)
        except:
            pass
        os.makedirs(self.DOWNLOAD_DIRECTORY)
    
    def proxy_check(self,proxy: tuple, timeout: int) -> tuple:
        protocols = ['http', 'socks4', 'socks5']

        if len(proxy) not in (2, 4):
            return (proxy, 'Wrong format', None)
        else:
            for protocol in protocols:
                ok_proxy = False
                if len(proxy) == 2:
                    ip = proxy[0]
                    port = proxy[1]
                    proxy_config = {
                        'https': f'{protocol}://{ip}:{port}',
                        'http': f'{protocol}://{ip}:{port}',
                    }
                else:
                    ip = proxy[0]
                    port = proxy[1]
                    username = proxy[2]
                    password = proxy[3]
                    proxy_config = {
                        'https': f'{protocol}://{username}:{password}@{ip}:{port}',
                        'http': f'{protocol}://{username}:{password}@{ip}:{port}',
                    }

                try:
                    response = requests.get(
                        'https://ipinfo.io/ip',
                        proxies=proxy_config,
                        timeout=timeout
                    )
                except Exception:
                    continue

                if response.text == ip:
                    ok_proxy = True
                    proxy_type = protocol
                    break
            
            if ok_proxy:
                return True
                return (proxy, 'OK', proxy_type)
                
            else:
                return False
                return (proxy, 'Not working', None)
    
    def get_proxies_list(self,proxies_dir: str, separate=':') -> list:
        """
        This function helps us to divide ip, port [username, password] from a list of proxies of any type of protocol (http)
        Args:
            proxies_dir (str): directory of proxies list

        Kwargs: 
            separate (str): separator between components of a proxy. Default to ':'

        Returns:
            A list of proxies   
        """  # noqa: {max_length+5}1
        proxies_list = []

        with open(proxies_dir, 'r') as f:
            lst = f.readlines()
            for line in lst:
                tmp = line.strip()
                proxies_list.append(tuple(tmp.split(separate)))

        return proxies_list

    def __latest_download_file(self) -> str:
        path = self.DOWNLOAD_DIRECTORY
        os.chdir(path)
        files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
        newest = files[-1]
        return newest

    def forceStop(self):
        self.isForceClosed = True
        self.browser.quit()

def pushNotification(title):
    msg = QMessageBox()
    msg.setWindowTitle('Thông báo!')
    msg.setTextFormat(Qt.RichText)
    msg.setText(title)
    msg.activateWindow()
    msg.exec_()
    return