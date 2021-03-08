# Dependencies
import config
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import datetime
import time
from bs4 import BeautifulSoup
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path


# https://webstore.recsports.umich.edu/booking/f4c5c447-982c-49af-9972-f83844dc74cc/slots/c4dbf8b9-9fb7-4a87-b732-afa156df1483/2021/1/27

def create_driver():
    options = Options()
    #options.add_argument("--headless")
    options.page_load_strategy = 'normal'
    options.add_argument('--user-data-dir=' + config.USER_DATA_DIR)
    #options.add_argument('--remote-debugging-port=45447')
    driver = Chrome(chrome_options=options)
    return driver


def get_sched_date():
    today = datetime.date.today()
    d = datetime.timedelta(days=3)
    return today + d


def login(driver):
    driver.find_element(By.CSS_SELECTOR, "#divLoginOptions > div.modal-body > div:nth-child(3) > div > button").click()
    driver.find_element(By.CSS_SELECTOR, "#login").send_keys(config.USERNAME)
    driver.find_element(By.CSS_SELECTOR, "#password").send_keys(config.PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "#loginSubmit").click()
    return


def parse_openings(driver):
    driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[2]/div[9]/div[2]/div[2]/button[4]').click()
    #/html/body/div[3]/div[1]/div[2]/div[9]/div[2]/div[2]/button[4]
    #//*[@id="divBookingDateSelector"]/div[2]/div[2]/button[4]
    #driver.find_element_by_xpath("//button[@data-button-index='4']").click()
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.html.body.find('div', class_="container-flex")
    slots = div.find_all('p')
    openings = {}
    for s in slots:
        if "Unavailable" not in s.find_previous_sibling('div').button.text:
            openings[str(s)[11:-13]] = s.find_previous_sibling('div').button
    if not openings:
        print("No open slots available :(")
        driver.close()
        driver.quit()
        exit(0)
    return openings


def choose_gym():
    service = calendar_integration()
    schedule_date = (datetime.datetime.now() + datetime.timedelta(days=3)).isoformat() + 'Z'
    schedule_date = schedule_date[:11] + '00:00:00.00Z'
    max_time = (datetime.datetime.now() + datetime.timedelta(days=4)).isoformat() + 'Z'
    gym_events_dict = service.events().list(calendarId=config.CALENDAR_ID, timeMin=schedule_date, timeMax=max_time,
                                            singleEvents=True, orderBy='startTime').execute()
    gym_events = gym_events_dict.get('items', [])
    if not gym_events:
        print("Nothing scheduled :(")
        exit(0)
    event = gym_events[0]
    return event['summary']

def choose_time(driver):  # openings
    service = calendar_integration()
    schedule_date = (datetime.datetime.now() + datetime.timedelta(days=3)).isoformat() + 'Z'
    schedule_date = schedule_date[:11] + '00:00:00.00Z'
    max_time = (datetime.datetime.now() + datetime.timedelta(days=4)).isoformat() + 'Z'
    #print(schedule_date, max_time)
    gym_events_dict = service.events().list(calendarId=config.CALENDAR_ID, timeMin=schedule_date, timeMax=max_time,
                                            singleEvents=True, orderBy='startTime').execute()
    gym_events = gym_events_dict.get('items', [])
    if not gym_events:
        print("Nothing scheduled :(")
        driver.close()
        driver.quit()
        exit(0)
    event = gym_events[0]
    start_time = event['start']['dateTime']
    start_time = start_time[11:16]
    hour = int(start_time[:2])
    minute = start_time[-2:]
    am = True
    if minute == '45':
        min_end = ''
    else:
        min_end = int(minute) + 15
        min_end = ':' + str(min_end)
    # PM
    if hour > 12:
        hour -= 12
        am = False
    elif hour == 12:
        am = False
    if minute == '00':
        minute = ''
    else:
        minute = ':' + minute
    reformatted_time = str(hour) + minute + ' - ' + str(hour) + min_end
    if am:
        reformatted_time += ' AM'
    else:
        reformatted_time += ' PM'
    if hour == 11 and minute == ':45' and am:
        reformatted_time = '11:45 AM - 12 PM'
    return reformatted_time


def calendar_integration():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', config.SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def schedule_slot(start_time, openings, driver):
    if start_time not in openings:
        print("Your desired slot '" + start_time + "' is not available :(")
        driver.close()
        driver.quit()
        exit(0)
    button = openings[start_time]
    # print(button.xpath)
    onclick = button.attrs['onclick']
    child = onclick[-3:-1]
    CSS_id = '/html/body/div[3]/div[1]/div[2]/div[11]/div/div[' + child + ']/div/button'
    xpath = '//*[@id="divBookingSlots"]/div/div[' + child + ']/div/button'
    # print(xpath)
    book = driver.find_element_by_xpath(xpath)
    book.click()
    # buttons = driver.find_elements_by_tag_name('button')
    # for button in buttons:
    #     if onclick in button.text:
    #         button.click()
    return
