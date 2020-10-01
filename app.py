import os

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify

from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "trafficdatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Camera(db.Model):	
	tracking_id = db.Column(db.String(10), unique=True, nullable=False, primary_key=True)
	frame_number = db.Column(db.String(10), nullable=False)
	lane = db.Column(db.String(10), nullable=False)
	datetime = db.Column(db.String(10), nullable=False)
	image_path = db.Column(db.String(100), nullable=False)

	def __repr__(self):
		return "<Tracking ID: {}>".format(self.tracking_id)
		return "<Frame Number: {}>".format(self.frame_number)
		return "<Lane: {}>".format(self.lane)
		return "<Date-Time: {}>".format(self.datetime)
		return "<Image: {}>".format(self.image_path)

@app.route("/", methods=["GET", "POST"])
def home():
	if request.form:
		if request.form["submit_button"] == "Go to Configurations":
			return redirect(url_for('config'))
		if request.form["submit_button"] == "Go to OFE Application":
			return redirect(url_for('camera'))
		if request.form["submit_button"] == "Go to OFE Records":
			return redirect(url_for('ofe_views'))
	return render_template("home.html")

@app.route("/config/", methods=["GET", "POST"])	
def config():
	if request.form:
		if request.form["submit_button"] == "Submit":

			with open('road.txt', 'r') as file:   # input file of the frame extractor application
				data = file.readlines()
			data[0] = str('x11 ') + str(request.form.get("x11")) + str('\n')
			data[1] = str('x12 ') + str(request.form.get("x12")) + str('\n')
			data[2] = str('x13 ') + str(request.form.get("x13")) + str('\n')
			data[3] = str('x14 ') + str(request.form.get("x14")) + str('\n')
			data[4] = str('x21 ') + str(request.form.get("x21")) + str('\n')
			data[5] = str('x22 ') + str(request.form.get("x22")) + str('\n')
			data[6] = str('x23 ') + str(request.form.get("x23")) + str('\n')
			data[7] = str('x24 ') + str(request.form.get("x24")) + str('\n')
			data[8] = str('y11 ') + str(request.form.get("y11")) + str('\n')
			data[9] = str('y22 ') + str(request.form.get("y22")) + str('\n')
			data[10] = str('y1 ') + str(request.form.get("y1")) + str('\n')
			data[11] = str('y2 ') + str(request.form.get("y2"))
			with open('road.txt', 'w') as file:
				file.writelines(data)
				
			with open('camera.txt', 'r') as file:   # input file of the frame extractor application
				data = file.readlines()
			data[0] = str('username ') + str(request.form.get("username")) + str('\n')
			data[1] = str('password ') + str(request.form.get("password")) + str('\n')
			data[2] = str('ipaddress ') + str(request.form.get("ipaddress"))
			with open('camera.txt', 'w') as file:
				file.writelines(data)

			with open('radar.txt', 'r') as file:   # input file of the frame extractor application
				data = file.readlines()
			data[0] = str('baudrate ') + str(request.form.get("baudrate")) + str('\n')
			data[1] = str('samplefrequency ') + str(request.form.get("samplefrequency")) + str('\n')
			data[2] = str('speedunit ') + str(request.form.get("speedunit")) + str('\n')
			data[3] = str('direction ') + str(request.form.get("direction")) + str('\n')
			data[4] = str('fftmode ') + str(request.form.get("fftmode")) + str('\n')
			data[5] = str('jsonmode ') + str(request.form.get("jsonmode")) + str('\n')
			data[6] = str('rawdata ') + str(request.form.get("rawdata")) + str('\n')
			data[7] = str('numberreport ') + str(request.form.get("numberreport")) + str('\n')
			data[8] = str('rangereport ') + str(request.form.get("rangereport")) + str('\n')
			data[9] = str('speedreport ') + str(request.form.get("speedreport")) + str('\n')
			data[10] = str('reportunit ') + str(request.form.get("reportunit"))
			with open('radar.txt', 'w') as file:
				file.writelines(data)

			return redirect(url_for('camera'))

		if request.form["submit_button"] == "Use Defaults":
			return redirect(url_for('camera'))

	return render_template("config.html")

@app.route("/camera/", methods=["GET", "POST"])	
def camera():
	if request.form:
		if request.form["submit_button"] == "Add Vehicle Record":
			optimal_frame = Camera(tracking_id=request.form.get("tracking_id"))
			optimal_frame.frame_number = request.form.get("frame_number")
			optimal_frame.lane = request.form.get("lane")
			optimal_frame.datetime = request.form.get("datetime")
			optimal_frame.image_path = request.form.get("image_path")
			db.session.add(optimal_frame)
			db.session.commit()
		if request.form["submit_button"] == "Start Application":
			os.system("cd /opt/nvidia/deepstream/deepstream-5.0/sources/deepstream_python_apps/apps/ofe_datetime_db_test")
			os.system("python3 ofe.py file:///home/jetsonuser/Videos/vid301_cropped.264 frames")
			return redirect(url_for('ofe_views'))
		if request.form["submit_button"] == "Stop Application":
			os.system("exit()")
			return redirect(url_for('home'))
		if request.form["submit_button"] == "View OFE Records":
			return redirect(url_for('ofe_views'))
	return render_template("camera.html")

@app.route("/camera_post/<uuid>", methods=['GET', 'POST'])
def camera_post(uuid):
	content = request.json
	optimal_frame = Camera(tracking_id=content['tracking_id'])
	optimal_frame.frame_number = content['frame_number']
	optimal_frame.lane = content['lane']
	optimal_frame.datetime = content['datetime']
	optimal_frame.image_path = content['image_path']
	db.session.add(optimal_frame)
	db.session.commit()
	return jsonify({"uuid":uuid})
	
@app.route("/ofe_views/", methods=["GET", "POST"])
def ofe_views():
	if request.form:
		if request.form["submit_button"] == "Home":
			return redirect(url_for('home'))
		if request.form["submit_button"] == "Delete Records":
			Camera.query.delete()
			db.session.commit()
			return redirect(url_for('ofe_views'))
	optimal_frames = Camera.query.all()
	return render_template("ofe_views.html", optimal_frames=optimal_frames)
 
if __name__ == "__main__":
    app.run(debug=True)
