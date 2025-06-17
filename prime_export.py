import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


print("Select your default browser:")
print("[A] Chrome")
print("[B] Firefox")
print("[C] Edge")
print("[D] Brave")
choice = input("Enter the option: ").strip().lower()

def get_brave_binary():
    if os.name == 'nt':
        return "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    elif os.name == 'posix':
        return "/usr/bin/brave-browser"

def launch_browser():
    if choice == 'a':
        options = ChromeOptions()
        return webdriver.Chrome(options=options)

    elif choice == 'b':
        options = FirefoxOptions()
        return webdriver.Firefox(options=options)

    elif choice == 'c':
        options = EdgeOptions()
        return webdriver.Edge(options=options)

    elif choice == 'd':
        options = ChromeOptions()
        options.binary_location = get_brave_binary()
        return webdriver.Chrome(options=options)

    else:
        raise Exception("Invalid choice")

driver = launch_browser()
print("Launching browser for authentication...")
driver.get("https://music.youtube.com/")
def wait_for_callback():
    input("Press Enter after logging in to Amazon Music...")
wait_for_callback()
print("Getting authentication tokens...")
cookies = driver.get_cookies()
with open("cookies.json", 'w') as f:
    json.dump(cookies, f)
print("Authentication successful!")
driver.quit()


