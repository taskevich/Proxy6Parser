import re
import time

from typing import Optional, Callable
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver


class SeleniumWorker:
    def __init__(self, proxy: str = None):
        self.selenium_wire_options = {
            "disable_capture": True,
            "proxy": {"no_proxy": "localhost,127.0.0.1,dev_server:8080"}
        }

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_experimental_option("detach", True)

        if proxy:
            self.selenium_wire_options.update({"http": proxy, "https": proxy, })

        self.driver: Optional[webdriver.Chrome] = None

        self._initialize_driver()

    def _initialize_driver(self):
        try:
            self.driver = webdriver.Chrome(
                seleniumwire_options=self.selenium_wire_options,
                options=self.chrome_options
            )
        except Exception as ex:
            raise RuntimeError(f"Ошибка инициализации драйвера: {ex}")

    def get(self, url: str):
        """Открытие ссылки"""
        return self.driver.get(url)

    def _wait_for_element(
            self,
            ec_func: Callable,
            by: str,
            find_value: str,
            wait_time: int = 20
    ) -> Optional[WebElement]:
        element = WebDriverWait(self.driver, wait_time).until(
            ec_func((by, find_value))
        )
        return element

    def login(self, email: str, password: str):
        """Авторизация в личный кабинет"""
        self.driver.find_element(By.CLASS_NAME, "icon-login").click()

        self._wait_for_element(
            ec_func=EC.presence_of_element_located,
            by=By.NAME,
            find_value="email"
        ).send_keys(email)

        password_element = self._wait_for_element(
            ec_func=EC.presence_of_element_located,
            by=By.NAME,
            find_value="password"
        )
        password_element.send_keys(password)

        print("Жду прохождения капчи и авторизации")
        while True:
            try:
                self._wait_for_element(
                    ec_func=EC.presence_of_element_located,
                    by=By.NAME,
                    find_value="password"
                )
            except:
                break
            time.sleep(0.1)
        print("Капча пройдена, авторизация успешна")

    # self.driver.save_screenshot("screenshot.png")

    def get_proxies(self):
        table_element = self._wait_for_element(
            ec_func=EC.presence_of_element_located,
            by=By.CLASS_NAME,
            find_value="user_proxy_table"
        )

        rows: list[WebElement] = table_element.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            proxy = re.findall(r"\d{2,3}.\d{2,3}.\d{2,3}.\d{2,3}:\d{0,5}", row.text)
            date = re.findall(r"\d{2}.\d{2}.\d{2}, \d{2}:\d{2}", row.text)
            if proxy and date:
                print(proxy[0], "-", date[0])
