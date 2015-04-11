from flask import Flask, url_for, render_template, request
app = Flask(__name__)

# Set to 0.0.0.0 for www (NOT SAFE !)
addr = '127.0.0.1'
port = 5000


@app.route("/")
def hello():
    return render_template('index')


if __name__ == "__main__":
    app.run(host=addr, port=port, debug=True)
