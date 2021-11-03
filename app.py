from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return {
        'name' : ["item1", "item2"]
    }


if __name__ == '__main__':
    app.run(debug=True)
