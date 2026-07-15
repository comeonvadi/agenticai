from flask import Flask, render_template

app = Flask(__name__, template_folder='template')

@app.route('/')
def home():
    return render_template('index.html', title='Home Page')
@app.route('/about')
def about():
    return render_template('about.html', title='About Page')
if __name__ == '__main__':
    app.run(debug=True)
    