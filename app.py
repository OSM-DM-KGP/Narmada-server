from flask import Flask
app = Flask(__name__)

# get_resource_class.py's version as an api

@app.route('/')
def hello():
	with open('index.html', 'r') as f:
		txt = f.readlines()
	return ''.join(txt)

# add routes for nodejs backend via here as well

if __name__ == '__main__':
	app.run(debug=True)