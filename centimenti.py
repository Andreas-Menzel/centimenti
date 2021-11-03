from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import threading
import time


class Player:
    driver = None
    game_code = ""
    player_name = ""
    answers = []

    def __init__(self, game_code, player_name, answers):
        self.driver = webdriver.Firefox()
        self.driver.set_window_size(400, 600)
        self.game_code = game_code
        self.player_name = player_name
        self.answers = answers

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

    def guess(self, answer):
        print('Player "', self.player_name, '" guesses ', answer, '.',  sep='')
        pass

    def check_result(self):
        # Maybe stop playing if answer was incorrect
        pass

    def cleanup(self):
        self.driver.quit()


def player_thread_function(game_code, player_name, answers):
    print('Creating player "', player_name, '"...', sep='')
    player = Player(game_code, player_name, answers)
    print('Player "', player_name, '" successfully created. Now ready to join the game.', sep='')

    event_join_game.wait()
    print('Player "', player_name, '" is now joining the game...', sep='')
    player.join_game()
    print('Player "', player_name, '" successfully joined the game!', sep='')

    for a in answers:
        player.guess(a)
        player.check_result()

    time.sleep(5)
    player.cleanup()



event_join_game = threading.Event()


if __name__ == "__main__":
    threads = []
    threads.append(threading.Thread(target=player_thread_function, args=("10491429", "Player 1", [0,1,2,3],)))
    threads.append(threading.Thread(target=player_thread_function, args=("10491429", "Player 2", [1,2,3,0],)))
    threads.append(threading.Thread(target=player_thread_function, args=("10491429", "Player 3", [2,3,0,1],)))
    threads.append(threading.Thread(target=player_thread_function, args=("10491429", "Player 4", [3,0,1,2],)))
    for t in threads:
        t.start()

    time.sleep(5)
    event_join_game.set()

    for t in threads:
        t.join()
