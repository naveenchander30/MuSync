from playwright.sync_api import sync_playwright

Chromium =["A","C","D","E","F"]
Firefox = ["B"]

print("""Supported Browsers:
      [A] Chrome
      [B] Firefox
      [C] Edge
      [D] Brave
      [E] Opera
      [F] Vivaldi
      Please select your default browser to use for logging in to Amazon Music (A/B/C/D/E/F): """)
browser_choice = input().strip().upper()
print("""Now enter the path to your default browser. 
You can find that by right-clicking on the browser's shortcut and selecting Properties.
If you are in Linux or MacOS, you can get it by running `which <browser_name>` in the terminal.
Now enter the path to your browser executable :""")
browser_path = input().strip()
with sync_playwright() as p:
    browser = p.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://music.youtube.com/")
    input("Please log in to Amazon Music and then press Enter...")
    context.storage_state(path="cookies.json")
    browser.close()
    
        