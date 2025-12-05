from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/api/data', methods=['GET'])
def get_data():
    """REST API endpoint that returns static HTML text"""
    html_content = """
    <html>
        <head>
            <title>API Response</title>
        </head>
        <body>
            <h1>REST API Response</h1>
            <p>Dies ist ein statischer HTML-Text von der API.</p>
            <p>This is static HTML text from the API.</p>
        </body>
    </html>
    """
    return html_content


if __name__ == '__main__':
    app.run()
