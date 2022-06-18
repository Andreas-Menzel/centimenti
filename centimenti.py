#!/usr/bin/env python3

#-------------------------------------------------------------------------------
# centimenti
#
# Python bot for playing [mentimeter](https://www.mentimeter.com/) quizzes with
#     brute-force or 'alwaysB' strategy.
#
# https://github.com/Andreas-Menzel/centimenti
#-------------------------------------------------------------------------------
# @author: Andreas Menzel
# @license: MIT License
# @copyright: Copyright (c) 2021 Andreas Menzel
#-------------------------------------------------------------------------------


import argparse
import itertools
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import threading
from time import sleep


# Setup argument parser
parser = argparse.ArgumentParser(description='Bot that plays quizzes on menti.com', prog='centimenti')
parser.add_argument('--version', action='version', version='%(prog)s v1.0.0')
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
parser.add_argument('-n', '--player_names',
    nargs='+',
    default=['Alice', 'Bob', 'Robinson Crusoe', 'Ready Player One', 'I, Robot', 'Excellence'],
    help='Specify a list of names that will be used to create the players.')
parser.add_argument('--slow_start',
    action='store_true',
    help='The players will be created with a small delay.')
parser.add_argument('--headless',
    action='store_true',
    help='Operates the browsers headless.')
args = parser.parse_args()


# Player
#
# Represents a single player and holds information about the game and planned
#     answers. It implements functions for joining a game, answering a question
#     and checking whether the selected answer was correct or not.
class Player:
    driver = None
    game_code = ""
    player_name = ""
    answers = []

    # __init__
    #
    # Initializes variables and browser object.
    def __init__(self, game_code, player_name, answers):
        if args.headless:
            opts = Options()
            opts.headless = True
            self.driver = webdriver.Firefox(options=opts)
        else:
            self.driver = webdriver.Firefox()
        self.driver.set_window_size(400, 600)
        self.game_code = game_code
        self.player_name = player_name
        self.answers = answers

    # join_game
    #
    # Opens the browser and enters the game code and name.
    #
    # @return   None
    def join_game(self):
        self.driver.get("https://menti.com")

        WebDriverWait(self.driver, 600).until(
            EC.presence_of_element_located((By.ID, 'enter-vote-key'))
        )

        # Enter game code
        elem_vote_key = self.driver.find_element(By.ID, 'enter-vote-key')
        elem_vote_key.send_keys(self.game_code)
        elem_vote_key_submit = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        elem_vote_key_submit.click()

        # Enter name
        elem_quiz_name = WebDriverWait(self.driver, 300).until(
            EC.presence_of_element_located((By.ID, 'quiz-name'))
        )
        elem_quiz_name.send_keys(self.player_name)
        elem_quiz_name_submit = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        elem_quiz_name_submit.click()

    # guess
    #
    # Waits until the next question is open and guesses the specified answer.
    #
    # @param    int     answer  The number of the answer. TODO: >=?
    #
    # @return   None
    def guess(self, answer):
        print('Player "', self.player_name, '" is ready to answer.', sep='')
        WebDriverWait(self.driver, 600).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'fieldset'))
        )

        elem_answer_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'fieldset button')
        if(len(elem_answer_buttons) >= answer):
            print('Player "', self.player_name, '" guesses ', answer, '.',  sep='')
            elem_answer_buttons[answer].click()
        else:
            print('Player "', self.player_name, '" could not guess answer ', answer, '. Too few possible answers.',  sep='')

    # check_result
    #
    # Waits until the results have loaded and checks whether the selected answer
    #     was correct.
    #
    # @return   None
    def check_result(self):
        print('Player "', self.player_name, '" is waiting for results.',  sep='')
        WebDriverWait(self.driver, 600).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'h1'), 'Loading result ...')
        )
        WebDriverWait(self.driver, 600).until_not(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'h1'), 'Loading result ...')
        )
        elem_result_text = self.driver.find_element(By.CSS_SELECTOR, 'h1')
        if elem_result_text.text == 'Correct answer!':
            print('Player "', self.player_name, '" chose the correct answer.',  sep='')
        elif elem_result_text.text == 'Wrong answer':
            print('Player "', self.player_name, '" chose the wrong answer.',  sep='')
        else:
            print('Player "', self.player_name, '" does not know wheather the answer was correct or not.',  sep='')
        # TODO: Maybe stop playing if answer was incorrect depending on strategy

    # cleanup
    #
    # Closes the browser
    #
    # @return   None
    def cleanup(self):
        self.driver.quit()


# player_thread_function
#
# Creates a player which will automatically join the game and guess the given
#     answers. The player will exist for another 5 minutes after it is finished
#     playing (to show the victory screen).
#
# @param    string  game_code       The mentimeter game code.
# @param    string  player_name     The name of the player that will be
#                                       generated here.
# @param    [int]   answers         A list representing the sequence of ansers
#                                       the player will select.
#
# @return   None
#
# @note:    This function should be called from within a separate thread.
def player_thread_function(game_code, player_name, answers):
    print('Creating player "', player_name, '"...', sep='')
    player = Player(game_code, player_name, answers)
    print('Player "', player_name, '" successfully created. Now ready to join the game.', sep='')

    print('Player "', player_name, '" is now joining the game...', sep='')
    player.join_game()
    print('Player "', player_name, '" successfully joined the game!', sep='')

    for a in answers:
        player.guess(a)
        player.check_result()

    sleep(600)
    player.cleanup()


# get_player_names
#
# Creates a list of correct length containing player names.
#
# @param    int         number_of_players   The number of players that will be
#                                               created.
#
# @return   [string]    Returns a list with the correct length containing player
#                           names.
def get_player_names(number_of_players):
    player_names = []
    for i in range(0, number_of_players):
        player_names.append(args.player_names[i % (len(args.player_names))])
    return player_names


# end
#
# Terminates the script
#
# @return   None
def end():
    print('Goodbye!')
    exit()


# main
#
# Main function. Creates the players.
#
# @return   None
def main():
    threads = []

    if args.game_code == None:
        args.game_code = input('Please specify the game code: ')

    print('------- MAIN SETTINGS --------')
    print('game code:\t\t', args.game_code, sep='')
    print('strategy:\t\t', args.strategy, sep='')
    print('number of questions:\t', args.number_of_questions, sep='')
    print('number of answers:\t', args.number_of_answers, sep='')
    print('------------------------------')
    print('--- AVAILABLE PLAYER NAMES ---')
    for i in range(0,len(args.player_names)):
        print('"', args.player_names[i], '"', sep='', end='')
        if i < (len(args.player_names) - 1):
            print(', ', end='')
    print('\n------------------------------')

    if args.strategy == 'alwaysB':
        if args.number_of_answers < 2:
            print('[ERROR] Not enough answers to choose B!')
            end()

        player_names = get_player_names(1)
        threads.append(threading.Thread(target=player_thread_function, args=(args.game_code, player_names[0], [1]*args.number_of_questions,)))

    elif args.strategy == 'everythingOnce':
        if args.number_of_questions != args.number_of_answers:
            print('[ERROR] Number of questions must be equal to number of answers!')
            end()

        one_answer = list(range(0, args.number_of_questions))
        all_answers = list(itertools.permutations(one_answer))

        player_names = get_player_names(len(all_answers))

        for i in range(0, len(all_answers)):
            threads.append(threading.Thread(target=player_thread_function, args=(args.game_code, player_names[i], all_answers[i],)))


    while True:
        print('I will now create', len(threads), 'player(s).', end=' ')
        confirmation = input('OK? (yes/no) ')
        if confirmation == 'yes':
            break
        elif confirmation == 'no':
            while True:
                print('Which players should be created? (0/x;y - x >= 0 && y <= ', len(threads), ')', sep='', end=' ')
                which_players = input('> ')
                if which_players == '0':
                    end()
                else:
                    which_players_sep = which_players.split(';')
                    first_player = int(which_players_sep[0])
                    last_player = int(which_players_sep[1])
                    if first_player < 0 or first_player > len(threads) or last_player < 0 or last_player > len(threads) or first_player == last_player:
                        continue
                    else:
                        threads = threads[first_player : last_player]
                        break
        else:
            print('Please type "yes" or "no".')

    for t in threads:
        if args.slow_start:
            sleep(2)
        t.start()

    #for t in threads:
    #    t.join()


if __name__ == "__main__":
    main()
    end()
