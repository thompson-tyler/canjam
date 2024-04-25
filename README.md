# Canjam

Roger Burtonpatel, Cecelia Crumlish, Skylar Gilfeather, Tyler Thompson

## Installation Requirements
`canjam` requires Python >= 3.12. After cloning this repository, you'll need
to install the `FluidSynth` C library. Follow the instructions in the
[FluidSynth GitHub repository](https://github.com/FluidSynth/fluidsynth/wiki/Download#distributions) to install `FluidSynth` on your machine using your favorite package manager.

Then, you can install the `canjam` requirements via `pip3 install -r requirements.txt`

```
pip3 install numpy
pip3 install pygame
pip3 install pyaudio
pip3 install pyfluidsynth
```

To run `canjam`, run `python3 run.py`. The `canjam` executable takes the
following arguments:

`-n / --name [NAME]`: Your displayed name to other CanJam peers.

`-j / --join [HOST:PORT]`: The hostname and port of another CanJam user,
to join their CanJam canvas.

`-p / --port [PORT]`: The port that your CanJam program should use for internet communication. If `-p` is not specified, the OS will assign you one.

`-v / --verbose`: Verbosity flag, to print debugging messages to the console.

## Testing

To run the test suite, `cd` into the root directory of this project and run:
`python -m unittest`

Or, to run a specific test, invoke the following with your chosen test name:
`python -m unittest tests/<test_name>.py`
