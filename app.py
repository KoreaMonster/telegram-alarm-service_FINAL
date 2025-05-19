from flask import Flask, request, render_template

app = Flask(__name__, template_folder='app/web/templates')

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        pass
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)