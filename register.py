"""
This file is to register OAuth to database.
The gist is to make it easier configuring the app.
"""

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from configparser import ConfigParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = ConfigParser()
CONFIG.read(BASE_DIR / "config.ini")


# USERNAME = 'dango'
# PASSWORD = 'dango'
NAME = 'lifesync-app'
CLIENT_ID = CONFIG.get("GOOGLE", "client_id")
SECRET = SECRET_KEY = CONFIG.get("GOOGLE", "secret")


options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

driver.get('http://team20.cmu-webapps.com/admin')

username_field = driver.find_element(by='id', value='id_username')
username = input('Please input your superuser name\n> ')
# username = USERNAME
username_field.send_keys(username)

password_field = driver.find_element(by='id', value='id_password')
password = input('Please input your superuser password\n> ')
# password = PASSWORD
password_field.send_keys(password)

form = driver.find_element(by='id', value='login-form')
form.submit()

driver.get('http://team20.cmu-webapps.com/admin/socialaccount/socialapp/add')

provider_selector = Select(driver.find_element(by='id', value='id_provider'))
provider_selector.select_by_index(1)

name_field = driver.find_element(by='id', value='id_name')
client_id_field = driver.find_element(by='id', value='id_client_id')
secret_field = driver.find_element(by='id', value='id_secret')

name_field.send_keys(NAME)
client_id_field.send_keys(CLIENT_ID)
secret_field.send_keys(SECRET)

form = driver.find_element(by='id', value='socialapp_form')
form.submit()

print('SUCC')
