from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import math

app = Flask(__name__)
CORS(app)

users = {}

MAX_ENERGY = 100
REGEN_RATE = 6
BASE_RATE = 0.02

@app.route("/")
def home():
    return "API RUNNING"

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "energy": MAX_ENERGY,
            "last": time.time(),
            "level": 1,
            "multiplier": 1.0
        }
    return users[user_id]

@app.route("/sync", methods=["POST"])
def sync():
    user_id = str(request.json.get("user_id"))
    u = get_user(user_id)

    now = time.time()
    dt = now - u["last"]

    regen = REGEN_RATE * (1 - (u["energy"]/MAX_ENERGY)**2)
    u["energy"] = min(MAX_ENERGY, u["energy"] + regen * dt)

    passive = dt * BASE_RATE * u["level"] * u["multiplier"]
    u["balance"] += passive

    u["last"] = now

    return jsonify({
        "balance": round(u["balance"], 4),
        "energy": int(u["energy"]),
        "level": u["level"]
    })

@app.route("/tap", methods=["POST"])
def tap():
    user_id = str(request.json.get("user_id"))
    u = get_user(user_id)

    if u["energy"] > 5:
        u["energy"] -= 5
        reward = (2 + math.sqrt(u["level"])) * u["multiplier"]
        u["balance"] += reward
        return jsonify({"gain": round(reward, 2)})

    return jsonify({"gain": 0})

@app.route("/upgrade", methods=["POST"])
def upgrade():
    user_id = str(request.json.get("user_id"))
    u = get_user(user_id)

    cost = (u["level"] ** 2) * 25

    if u["balance"] >= cost:
        u["balance"] -= cost
        u["level"] += 1
        u["multiplier"] += 0.2

    return jsonify({
        "level": u["level"],
        "balance": round(u["balance"], 2)
    })
