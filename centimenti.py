from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class Player:
    driver = None
    game_code = ""
    player_name = ""

    def __init__(self, game_code, player_name):
        self.driver = webdriver.Firefox()
        self.game_code = game_code
        self.player_name = player_name

    def join_game(self):
        self.driver.get("https://menti.com")

        # Enter game code
        elem_vote_key = self.driver.find_element(By.ID, 'enter-vote-key')
        elem_vote_key.send_keys(self.game_code)
        elem_vote_key_submit = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        elem_vote_key_submit.click()

        # Enter name
        elem_quiz_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'quiz-name')))
        elem_quiz_name.send_keys(self.player_name)
        elem_quiz_name_submit = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        elem_quiz_name_submit.click()

    def __del__(self):
        self.driver.close()
