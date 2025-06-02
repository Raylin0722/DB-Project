import flask

app = flask.Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"


if __name__ == '__main__':
    app.run(host='26.227.33.73', port=5000, debug=True)
