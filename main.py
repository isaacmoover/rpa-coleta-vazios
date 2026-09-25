from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time

load_dotenv()

driver = webdriver.Chrome()
driver.get('http://websag.windrose.com.br/arearestrita')


field_email = driver.find_element(By.ID, 'login')
field_email.send_keys(os.environ['WINDROSE_LOGIN'])

field_password = driver.find_element(By.NAME, 'senha')
field_password.send_keys(os.environ['WINDROSE_PASSWORD'])


# ----------- IA | Slide Submit Button -----------

button = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CLASS_NAME, 'ui-draggable-handle'))
)

track = button.find_element(By.XPATH, '..')
distance = track.size['width'] - button.size['width']

ActionChains(driver, duration=0) \
    .click_and_hold(button) \
    .move_by_offset(1, 0) \
    .move_by_offset(distance + 5, 0) \
    .release() \
    .perform()

# ----------- END IA | Slide Submit Button END -----------

time.sleep(8)