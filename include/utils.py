import trio
from selenium import webdriver
from selenium.webdriver import ChromeOptions


def write_page_source(name: str, page_source: str):
    """
    Writes the page source to a file.

    Args:
        url (str): The URL of the page.
        page_source (str): The page source to be written.

    Returns:
        None
    """
    # Replace special characters in the URL to create a valid file name
    file_name = f"outputs/{name}.html"
    # Write the page source to the file
    with open(file_name, "w") as file:
        file.write(page_source)


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


async def create_web_driver_trio():
    return await trio.to_thread.run_sync(
        webdriver.Remote,
        "http://selenium:4444",
        True,
        None,
        webdriver.ChromeOptions(),
    )
