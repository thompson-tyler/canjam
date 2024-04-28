# CanJam

![Canjam running with three users simultaneously sharing sound](summary-image.png)

## About

Canjam is a multiplayer Pygame for sharing sounds, and playing on unique synths created using *soundfonts*.

At the start of each game a player will get a randomly generated synth, color, and instrument grid that they will be able to interact with using their mouse.

Each column on the grid corresponds to a key, and each row corresponds to an octave. The grid will display the players color and play a sound when a player clicks on square.

Once connected to other players they will be able to see and hear other players' sounds on their grid. Canjam supports up to 4 players per game.

## How to play

Once all of the package requirements have been installed, run Canjam with the following:

- Start an instance of Canjam by running `python run.py -n NAME` in the root directory. It should print out your local IP and the port Canjam is running on.
- Then, other users on the same Wi-Fi network may join your room using the command `python run.py -n NAME -j HOST:PORT`, where `HOST:PORT` is the IP and port that was printed out by the first Canjam instance.

## Other features

- Canjam operates using a peer-to-peer model, which means that there is no central server managing rooms. When players leave a room, the rest of the players will still be able to stay in the room, and continue to play the game. How exciting!
- Soundfont is a technology that uses a sample based synthesis to play MIDI files, essentially providing the user with fonts or different "instruments" to play MIDI notes with. Future work on this project will include loading in more sound fonts as choices.
- Canjam uses the Fluidsynth library which uses to the synthesizer chip on your computer, so you can interact indirectly with hardware on your very own computer!
