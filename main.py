from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException

import time

# Initialize the WebDriver
driver = webdriver.Chrome()

def setup_browser():
    # Open the website
    driver.get("http://sdetchallenge.fetch.com/")
    driver.maximize_window()

def input_number(bowl, cell_index, number):
    # Insert number in the specified cell of the bowl's grid
    input_id = f"{bowl}_{cell_index}"
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, input_id))).clear()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, input_id))).send_keys(str(number))

def click_weigh_button():
    # Press the "Weigh" button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "weigh"))).click()

    

def get_result():
    # Get the result of weighing from the list within 'game-info'
    weighings = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".game-info ol li"))
    )
    # Only return the text of the last weighing result
    return weighings[-1].text.strip() if weighings else ""

def get_result_second():
    game_info_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'game-info'))
    )
    # Find the <ol> element within the game-info element
    ol_element = game_info_element.find_element(By.TAG_NAME, 'ol')
    # Wait for the second <li> element to be present
    second_li_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.game-info ol li:nth-child(2)'))
    )
    return second_li_element.text


def reset(driver):
    try:
        # Execute JavaScript to get the second reset button element
        reset_button = driver.execute_script("return document.querySelectorAll('button#reset')[1];")
        # Simulate a click event on the second reset button element
        driver.execute_script("arguments[0].click();", reset_button)
        print("Second reset button clicked successfully")
    except Exception as e:
        print(f"An error occurred while clicking the second reset button: {e}")



def click_gold_bar_number(driver, number):
    # Click on the button with the suspected fake bar number
    try:
        suspected_fake_bar_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, f"coin_{number}"))
        )
        suspected_fake_bar_button.click()

        # Attempt to catch the alert as quickly as possible
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        print(f"Alert dismissed with text: {alert_text}")
    except NoAlertPresentException:
        print(f"Alert was not present after clicking bar {number}.")
    except Exception as e:
        print(f"An error occurred when trying to click on gold bar number {number}: {e}")



def perform_algorithm():
    # Divide the 9 bars into 3 groups of 3 bars each
    groups = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    
    # Weigh the first two groups against each other
    for i in range(3):
        input_number('left', i, groups[0][i])
        input_number('right', i, groups[1][i])
    click_weigh_button()
    result = get_result()
    time.sleep(2)  # Wait for the result to display
    print(result)  # For debugging
    reset(driver)
    
    # Assuming the result format "1. [1,2,3] = [4,5,6]" and you're looking for "="
    # Determine which group contains the fake bar
    if "=" not in result:
        fake_group = groups[0] if "<" in result else groups[1]
    else:
        fake_group = groups[2]
    
    # Weigh two bars from the fake group against each other
    input_number('left', 0, fake_group[0])
    input_number('right', 0, fake_group[1])
    click_weigh_button()
    result = get_result_second()
    time.sleep(2)  # Wait for the result to display
    print(result)  # For debugging
    reset(driver)
    
    # Determine which bar is the fake bar
    if "=" in result:
        fake_bar = fake_group[2]
    else:
        fake_bar = fake_group[0] if "<" in result else fake_group[1]
    
    # Click on the suspected fake bar number and handle the alert
    alert_message = click_gold_bar_number(driver, fake_bar)
    print(alert_message)

try:
    setup_browser()
    perform_algorithm()
finally:
    # Allow some time to view before closing the browser
    time.sleep(5)
    driver.quit()
