from flask import Flask, render_template, request, redirect, url_for, jsonify, session, abort
from authlib.integrations.flask_client import OAuth
import config
from loginpass import create_flask_blueprint, GitHub, Google, Gitlab, Discord
import databases
import os 

themes = ['3024-day', '3024-night', 'abbott', 'abcdef', 'ambiance-mobile', 'ambiance', 'ayu-dark', 
          'ayu-mirage', 'base16-dark', 'base16-light', 'bespin', 'blackboard', 'cobalt', 'colorforth', 
          'darcula', 'dracula', 'duotone-dark', 'duotone-light', 'eclipse', 'elegant', 'erlang-dark', 
          'gruvbox-dark', 'hopscotch', 'icecoder', 'idea', 'isotope', 'juejin', 'lesser-dark', 'liquibyte', 
          'lucario', 'material-darker', 'material-ocean', 'material-palenight', 'material', 'mbo', 'mdn-like', 
          'midnight', 'monokai', 'moxer', 'neat', 'neo', 'night', 'nord', 'oceanic-next', 'panda-syntax', 
          'paraiso-dark', 'paraiso-light', 'pastel-on-dark', 'railscasts', 'rubyblue', 'seti', 'shadowfox', 
          'solarized', 'ssms', 'the-matrix', 'tomorrow-night-bright', 'tomorrow-night-eighties', 'ttcn', 
          'twilight', 'vibrant-ink', 'xq-dark', 'xq-light', 'yeti', 'yonce', 'zenburn']

languages = ['apl', 'asciiarmor', 'asn.1', 'asterisk', 'brainfuck', 'clike', 'clojure', 'cmake', 'cobol', 
             'coffeescript', 'commonlisp', 'crystal', 'css', 'cypher', 'd', 'dart', 'diff', 'django', 
             'dockerfile', 'dtd', 'dylan', 'ebnf', 'ecl', 'eiffel', 'elm', 'erlang', 'factor', 'fcl', 'forth', 
             'fortran', 'gas', 'gfm', 'gherkin', 'go', 'groovy', 'haml', 'handlebars', 'haskell', 
             'haskell-literate', 'haxe', 'htmlembedded', 'htmlmixed', 'http', 'idl', 'javascript', 'jinja2', 
             'jsx', 'julia', 'livescript', 'lua', 'markdown', 'mathematica', 'mbox', 'mirc', 'mllike', 'modelica', 
             'mscgen', 'mumps', 'nginx', 'nsis', 'ntriples', 'octave', 'oz', 'pascal', 'pegjs', 'perl', 'php', 
             'pig', 'powershell', 'properties', 'protobuf', 'pug', 'puppet', 'python', 'q', 'r', 'rpm', 'rst', 
             'ruby', 'rust', 'sas', 'sass', 'scheme', 'shell', 'sieve', 'slim', 'smalltalk', 'smarty', 'solr', 
             'soy', 'sparql', 'spreadsheet', 'sql', 'stex', 'stylus', 'swift', 'tcl', 'textile', 'tiddlywiki', 
             'tiki', 'toml', 'tornado', 'troff', 'ttcn', 'ttcn-cfg', 'turtle', 'twig', 'vb', 'vbscript', 'velocity', 
             'verilog', 'vhdl', 'vue', 'wast', 'webidl', 'xml', 'xquery', 'yacas', 'yaml', 'yaml-frontmatter', 'z80']

app = Flask(__name__)
oauth = OAuth(app)

app.secret_key = "YOUR SECRET KEY"
app.config.from_pyfile('config.py')
database = databases.Database(app.config['MONGO_URI'], app.config['AIR_TABLE_API_KEY'])

backends = [GitHub, Google, Gitlab, Discord]

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/home')
def home():
    if 'user' in session:
        return render_template('home.html', user = session['user'])
    return redirect(url_for('index'))

@app.route('/new')
def new():
    if 'user' in session:
        return render_template('new.html', user = session['user'], themes = themes, langs = languages)
    return redirect(url_for('index'))
        

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/changeName', methods=['POST'])
def changeName():
    if 'user' in session:
        name = request.form.get('name')
        user = session['user']
        user['username'] = name
        session['user'] = user
        database.updateName(user['email'], name)
        return "Updated!"
    return abort(404)

@app.route('/uploadSnip', methods=['POST'])
def uploadSnip():
    if 'user' in session:
        name = request.form.get('name')
        description = request.form.get('description')
        code = request.form.get('code')
        language = request.form.get('language')
        theme = request.form.get('theme')
        database.uploadSnip(session['user']['email'], code, name, description, language, theme)
        details = request.form.to_dict()
        print(details)
        return "Uploaded!"


def handle_authorize(remote, token, user_info):
    if database.userExists(user_info['email']):
        session['user'] = database.getUser(user_info['email'])
    else:
        database.addUser(user_info['email'])
        session['user'] = database.getUser(user_info['email'])
    return redirect(url_for('home'))


bp = create_flask_blueprint(backends, oauth, handle_authorize)
app.register_blueprint(bp, url_prefix='/')
    
if __name__ == '__main__':
    app.run(debug=True)
