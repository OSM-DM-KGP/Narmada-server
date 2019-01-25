import os
from flask import Flask
app = Flask(__name__)

# get_resource_class.py's version as an api

@app.route('/')
def base():
	with open('index.html', 'r') as f:
		txt = f.readlines()
	return ''.join(txt)

@app.route('/hello')
def empty():
	return "Hello World!"
# add routes for nodejs backend via here as well

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)