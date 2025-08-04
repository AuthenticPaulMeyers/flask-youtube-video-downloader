from my_app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)


#  <img src="{{ info['thumbnail'] }}" alt="Video thumbnail" class="rounded-t-lg">
# <h2 class="m-2 text-xl font-semibold tracking-tight">{{ info['video_title'] }}</h2>