from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument(r"--user-data-dir=./chrome_profile")  # persistent profile

driver = webdriver.Chrome(options=options)
driver.get("http://beaconhouse.datanext.co/")

# 👉 Manually log in ONCE in the opened browser
# Close the browser after successful login
time.sleep(120)
