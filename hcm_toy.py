import os
import pytest
import time
import json
import re
import yaml
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

class HcmEmployeeSelfService():
    def __init__(self, driver):
        self.driver = driver

    def click(self, controlname, delay=0):
        element = self.get_element_by_controlname(controlname)
        ActionChains(self.driver).move_to_element(element).click(element).perform()
        if delay:
            time.sleep(delay)

    def input(self, controlname, text):
        element = self.get_element_by_controlname(controlname, '/input[@type="text"]')
        element.send_keys(text)

    def refresh(self):
        self.input("NavigationSearchBox_searchBoxInput", Keys.SHIFT + Keys.F5)

    def grid_items_count(self):
        elements = self.driver.find_elements_by_xpath("//*[@data-dyn-controlname='GridView_RowTemplate_Row0']")
        return len(elements)

    def get_element_by_controlname(self, controlname, extra=''):
        print(f'get {controlname}')
        xpath = f"//*[@data-dyn-controlname='{controlname}']{extra}"
        element = self.driver.find_element_by_xpath(xpath)
        return element

def aprove(hcm, args):
    hcm.click('HcmEmployeeSelfServiceWorkspace'),
    hcm.click('TSTimesheetEntryGridViewTimesheetsForMyReview')

    items = hcm.grid_items_count()
    print(items)

    while items:
        hcm.click('TSTimesheetTableWorkflowDropDialog')
        hcm.click('PromotedAction1')
        hcm.click('Action')
        time.sleep(0.5)
        hcm.refresh()
        time.sleep(0.5)
        items -= 1

def submit(hcm, args):
    match = re.match("(\d+) (\d+) ([0-8]) ([0-8]) ([0-8]) ([0-8]) ([0-8])", args.timespec)
    if not match:
        print("Invalid timespec")
        return

    hcm.click('HcmEmployeeSelfServiceWorkspace', 1.0)
    hcm.click('etoTSTimesheetCreate', 1.0)
    if (args.date):
        datefrom = hcm.get_element_by_controlname('DateFrom', '//input[@type="text"]')
        datefrom.clear()
        datefrom.send_keys(args.date)
    hcm.click('OK')
    hcm.click('NewLine')
    hcm.input('ProjId', match.group(1))
    hcm.input('CatergoryName', match.group(2))
    
    for day in range(1, 6):
        hcm.input(f'TSTimesheetLineWeek_Hours_{day}', match.group(2 + day))

    hcm.click('TSTimesheetTableWorkflowDropDialog')
    hcm.click('TSTimesheetTableWorkflowDropDialog')
    hcm.click('PromotedAction1')

    if not args.n:
        hcm.click('Submit')

def main(args):
    options = Options()
    options.add_argument(f"user-data-dir={os.path.expanduser('~')}/.config/chromium/Profile 1/")
    if not args.v:
        options.add_argument("headless")

    driver = webdriver.Chrome(chrome_options=options)
    driver.implicitly_wait(30)

    driver.get("https://nod-prod.operations.dynamics.com/?cmp=PL01&mi=DefaultDashboard")
    time.sleep(1.0)

    try:
        globals()[args.action](HcmEmployeeSelfService(driver), args)
    finally:
        driver.quit()
 
if __name__ == "__main__":
    argparse = ArgumentParser()
    argparse.add_argument('-v', action='store_true', default=False, help='Verbose')
    argparse.add_argument('-n', action='store_true', default=False, help='Dry run')
    subparsers = argparse.add_subparsers(title='action', dest='action')

    parser = subparsers.add_parser('submit')
    parser.add_argument('--date')
    parser.add_argument('timespec')
    
    subparsers.add_parser('aprove')

    args = argparse.parse_args()
    print(args)
    main(args)