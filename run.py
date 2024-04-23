from canjam.gamerunner import GameRunner
from queue import Queue

if __name__ == "__main__":
    game_runner = GameRunner(Queue(), Queue())
    game_runner.run_game()
