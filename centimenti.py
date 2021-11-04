import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import threading
import time


# Setup argument parser
parser = argparse.ArgumentParser(description='Bot that plays quizzes on menti.com', prog='centimenti')
parser.add_argument('--version', action='version', version='%(prog)s alpha-0.0.1')
parser.add_argument('-c', '--game_code',
    type=int,
    help='Specify the game code.')
parser.add_argument('-s', '--strategy',
    choices=['alwaysB', 'everythingOnce'],
    default='alwaysB',
    help='Specify the playing strategy.')
parser.add_argument('-q', '--number_of_questions',
    type=int,
    choices=range(1,65),
    default=4,
    metavar='',
    help='Specify the number of questions asked.')
parser.add_argument('-a', '--number_of_answers',
    type=int,
    choices=range(1,16),
    default=4,
    metavar='',
    help='Specify the maximum number of answers the player can choose in each question.')
args = parser.parse_args()


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

    time.sleep(20)
    player.cleanup()



event_join_game = threading.Event()


def end():
    print('Goodbye!')
    exit()


if __name__ == "__main__":
    threads = []

    print('Playing strategy', args.strategy)
    if args.strategy == 'alwaysB':
        if args.number_of_answers < 2:
            print('[ERROR] Not enough answers to choose B!')
            end()

        threads.append(threading.Thread(target=player_thread_function, args=(args.game_code, 'Player', [1]*args.number_of_questions,)))

    while True:
        print('I will now create', len(threads), 'player(s).', end=' ')
        confirmation = input('OK? (yes/no) ')
        if confirmation == 'yes':
            break
        elif confirmation == 'no':
            end()
        else:
            print('Please type "yes" or "no".')

    for t in threads:
        t.start()

    #time.sleep(5)
    event_join_game.set()

    #for t in threads:
    #    t.join()
