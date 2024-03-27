from selenium import webdriver
from selenium.webdriver import ChromeOptions


def create_web_driver(**kwargs):
    options = ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    )

    return webdriver.Remote(
        "http://selenium:4444",
        True,
        None,
        options,
        **kwargs,
    )
