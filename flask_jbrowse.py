from flask import Flask,render_template,request,redirect,url_for,Markup
from api.tools import jbrowse_javascript
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
STATIC = Path().joinpath(BASE_DIR,'jbrowse')
app = Flask(__name__,static_folder = STATIC)

@app.route('/<string:species>')
def hello(species):
    js = jbrowse_javascript(species=species)
    return render_template('jbrowse/Cuscuta_australis.html',js=js)

if __name__ == '__main__':
    app.run(debug=True)