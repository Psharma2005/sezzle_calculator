import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request


app = Flask(__name__)
app.config['SECRET_KEY'] = "SUPERSECRETKEY"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'calculations.db')
db = SQLAlchemy(app)


class Entry(db.Model):
	id = db.Column('id', db.Integer, primary_key=True)
	result = db.Column(db.String(200))


def get_calculations():
	farh = []
	calculations = Entry.query.all()

	if len(calculations) > 10:
		calculations = calculations[-10:]
	calculations.reverse()

	oprerations = ["+", "-", "/", "*"]
	for i in calculations:
		i = i.result
		i = i.replace(" ", "").split("=")
		result = i[1]
		meta_data = i[0]
		for operator in oprerations:
			if operator in meta_data:
				temp = meta_data.split(operator)
				first_var = temp[0]
				second_var = temp[1]
				farh.append({
					"first_var": first_var,
					"second_var": second_var,
					"operator": operator,
					"result": result
				})
	return farh


def _calculate_results(arg1, op, arg2):
	result = 0
	if op == '+':
		result = arg1 + arg2
	elif op == '-':
		result = arg1 - arg2
	elif op == '*':
		result = arg1 * arg2
	elif op == '/':
		result = arg1 / arg2
	return str(arg1)+" "+op+" "+str(arg2)+" = "+str(result)


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == "GET":
		res = get_calculations()
		return jsonify(res)
	elif request.method == "POST":
		input_req = request.get_json()
		print("input requests", input_req)
		first_var = input_req.get("first_var")
		second_var = input_req.get("second_var")
		operator = input_req.get("operator")
		required = [first_var, second_var, operator]
		if not all(required):
			return jsonify({
				"result": False,
				"message": "Required params are missing"
			})
		try:
			exception = False
			if type(first_var) not in [float, int]:
				exception = True
			if type(second_var) not in [float, int]:
				exception = True
			if operator not in ["+", "-", "/", "*"]:
				exception = True

			if exception:
				float("=")
		except:
			return jsonify({
				"result": False,
				"message": "Only Integers and Floats are allowed and operator should be in +, -, /, *"
			})

		print(first_var, operator, second_var)
		result = _calculate_results(first_var, operator, second_var)
		print(result)
		newEntry = Entry(result=result)
		db.session.add(newEntry)
		db.session.commit()
		return jsonify({
			"result": True,
			"message": "record inserted into db successfully",
			"data": get_calculations()
		})

if __name__ == '__main__':
	db.create_all()
	app.run(debug=True, port=80, host="0.0.0.0")