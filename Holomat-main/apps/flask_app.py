from flask import Flask, request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

sp_oauth = SpotifyOAuth(
    client_id='c61a5a6db05d4666a4db7a6ec4ed43bb',
    client_secret='cd57f32e6b1649e29612048f00c082f1',
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
    # Store token_info['access_token'] and token_info['refresh_token']
    return "Authentication successful, you can now close this tab."

if __name__ == '__main__':
    app.run(port=5000)
