import pygame
from pygame import mixer
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json
from flask import Flask, request, redirect

# Initialize Pygame
pygame.init()
mixer.init()
SCREEN_SIZE = (1920, 1080)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
WHITE = (255, 255, 255)
NAVY_BLUE = (20, 20, 40)
screen = pygame.display.set_mode(SCREEN_SIZE)

# Flask setup for Spotify authorization
app = Flask(__name__)
sp_oauth = SpotifyOAuth(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    redirect_uri='http://localhost:5000/callback',
    scope='user-modify-playback-state user-read-playback-state'
)


@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    # Save token_info for use in the Pygame app
    global access_token
    access_token = token_info['access_token']
    return "Authentication successful, you can now close this tab."


def play_sound(file_path):
    try:
        mixer.music.load(file_path)
        mixer.music.play()
    except pygame.error as e:
        print(f"Error playing sound {file_path}: {e}")


def run(screen, camera_manager):
    global access_token
    sp = spotipy.Spotify(auth=access_token)

    running = True
    circle_radius = 100
    play_button_center = (SCREEN_SIZE[0] // 2 - 200, SCREEN_SIZE[1] // 2)
    pause_button_center = (SCREEN_SIZE[0] // 2 + 200, SCREEN_SIZE[1] // 2)
    home_button_center = (50 + circle_radius, SCREEN_SIZE[1] - 800 - circle_radius)

    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)

    while running:
        if not camera_manager.update():
            continue

        transformed_landmarks = camera_manager.get_transformed_landmarks()
        if transformed_landmarks:
            for hand_landmarks in transformed_landmarks:
                index_pos = (int(hand_landmarks[8][0]), int(hand_landmarks[8][1]))  # INDEX_FINGER_TIP
                if (index_pos[0] - play_button_center[0]) ** 2 + (
                        index_pos[1] - play_button_center[1]) ** 2 <= circle_radius ** 2:
                    play_sound('audio/quick_click.wav')
                    sp.start_playback()  # Use Spotify Connect to start playback on an active device
                elif (index_pos[0] - pause_button_center[0]) ** 2 + (
                        index_pos[1] - pause_button_center[1]) ** 2 <= circle_radius ** 2:
                    play_sound('audio/confirmation.wav')
                    sp.pause_playback()  # Pause the current Spotify track
                elif (index_pos[0] - home_button_center[0]) ** 2 + (
                        index_pos[1] - home_button_center[1]) ** 2 <= circle_radius ** 2:
                    play_sound('audio/back.wav')
                    running = False

        screen.fill(BLACK)

        # Draw play button
        pygame.draw.circle(screen, NAVY_BLUE, play_button_center, circle_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, play_button_center, circle_radius, 5)
        text_surface = font.render('Play', True, WHITE)
        text_rect = text_surface.get_rect(center=play_button_center)
        screen.blit(text_surface, text_rect)

        # Draw pause button
        pygame.draw.circle(screen, NAVY_BLUE, pause_button_center, circle_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, pause_button_center, circle_radius, 5)
        text_surface = font.render('Pause', True, WHITE)
        text_rect = text_surface.get_rect(center=pause_button_center)
        screen.blit(text_surface, text_rect)

        # Draw home button
        pygame.draw.circle(screen, NAVY_BLUE, home_button_center, circle_radius)
        pygame.draw.circle(screen, LIGHT_BLUE, home_button_center, circle_radius, 5)
        text_surface = font.render('Home', True, WHITE)
        text_rect = text_surface.get_rect(center=home_button_center)
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        pygame.time.delay(50)


if __name__ == '__main__':
    from camera_manager import CameraManager  # Assuming CameraManager is in the parent directory

    # Start Flask app in a separate thread or process
    import threading

    flask_thread = threading.Thread(target=lambda: app.run(port=5000))
    flask_thread.start()

    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Spotify Control App')
    camera_manager = CameraManager('./M.npy', 1920, 1080)
    run(screen, camera_manager)
