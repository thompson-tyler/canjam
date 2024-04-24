from queue import Queue
from canjam.gamerunner import GameRunner

if __name__ == "__main__":
    game_runner = GameRunner(Queue(), Queue())
    game_runner.run_game()
