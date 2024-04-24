import pygame
import pyaudio
import numpy as np

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((400, 300))
clock = pygame.time.Clock()

# PyAudio setup
p = pyaudio.PyAudio()

x = SCREEN_WIDTH

def generate_audio(mouse_pos):
    # Scale mouse position to frequency range
    frequency = int((mouse_pos[0] / 400) * 1000) + 100
    # Generate a sine wave
    samples = (np.sin(2 * np.pi * np.arange(22050) * frequency / 44100)).astype(np.float32)
    return samples

def audio_callback(in_data, frame_count, time_info, status):
    mouse_pos = pygame.mouse.get_pos()
    audio_data = generate_audio(mouse_pos)
    return (audio_data.tobytes(), pyaudio.paContinue)

# Open PyAudio stream with callback
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=22050,  # Decreased sample rate
                frames_per_buffer=512,  # Decreased buffer size
                output=True,
                stream_callback=audio_callback)

stream.start_stream()

# Pygame event loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    pygame.display.flip()
    clock.tick(60)

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
