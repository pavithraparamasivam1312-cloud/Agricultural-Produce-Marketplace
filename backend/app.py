from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
CORS(app)
DB = os.path.join(os.path.dirname(__file__), "marketplace.db")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS produce (
          id INTEGER PRIMARY KEY AUTOINCREMENT, farmer TEXT NOT NULL,
          name TEXT NOT NULL, category TEXT, quantity REAL NOT NULL,
          unit TEXT DEFAULT 'kg', price REAL DEFAULT 0, location TEXT,
          status TEXT DEFAULT 'Available', created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS requests (
          id INTEGER PRIMARY KEY AUTOINCREMENT, buyer TEXT NOT NULL,
          produce_id INTEGER NOT NULL, requested_qty REAL NOT NULL,
          agreed_qty REAL, notes TEXT, status TEXT DEFAULT 'Pending',
          collection_status TEXT DEFAULT 'Not scheduled', created_at TEXT,
          FOREIGN KEY(produce_id) REFERENCES produce(id)
        );
        """)

@app.get("/api/health")
def health():
    return jsonify(status="ok", service="Agricultural Produce Marketplace API")

@app.get("/api/produce")
def get_produce():
    with db() as con:
        rows = con.execute("SELECT * FROM produce ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/produce")
def add_produce():
    d = request.get_json(force=True)
    required = ["farmer", "name", "quantity"]
    if not all(str(d.get(k, "")).strip() for k in required):
        return jsonify(error="Farmer, produce name and quantity are required"), 400
    with db() as con:
        cur = con.execute("""INSERT INTO produce
          (farmer,name,category,quantity,unit,price,location,created_at)
          VALUES (?,?,?,?,?,?,?,?)""",
          (d["farmer"], d["name"], d.get("category","Vegetables"),
           float(d["quantity"]), d.get("unit","kg"), float(d.get("price",0)),
           d.get("location",""), datetime.now().isoformat(timespec="seconds")))
        item = con.execute("SELECT * FROM produce WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(item)), 201

@app.post("/api/requests")
def create_request():
    d = request.get_json(force=True)
    try:
        qty = float(d["requested_qty"])
        produce_id = int(d["produce_id"])
    except (KeyError, ValueError, TypeError):
        return jsonify(error="A valid produce lot and quantity are required"), 400
    if qty <= 0 or not d.get("buyer","").strip():
        return jsonify(error="Buyer name and positive quantity are required"), 400
    with db() as con:
        lot = con.execute("SELECT * FROM produce WHERE id=?", (produce_id,)).fetchone()
        if not lot:
            return jsonify(error="Produce lot not found"), 404
        if qty > lot["quantity"]:
            return jsonify(error="Requested quantity exceeds listed availability"), 400
        cur = con.execute("""INSERT INTO requests
          (buyer,produce_id,requested_qty,notes,created_at)
          VALUES (?,?,?,?,?)""",
          (d["buyer"], produce_id, qty, d.get("notes",""),
           datetime.now().isoformat(timespec="seconds")))
        row = con.execute("""SELECT requests.*, produce.name AS produce_name,
          produce.farmer FROM requests JOIN produce ON produce.id=requests.produce_id
          WHERE requests.id=?""", (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201

@app.get("/api/requests")
def get_requests():
    with db() as con:
        rows = con.execute("""SELECT requests.*, produce.name AS produce_name,
          produce.farmer FROM requests JOIN produce ON produce.id=requests.produce_id
          ORDER BY requests.id DESC""").fetchall()
    return jsonify([dict(r) for r in rows])

@app.patch("/api/requests/<int:request_id>")
def update_request(request_id):
    d = request.get_json(force=True)
    allowed = {"status", "agreed_qty", "collection_status"}
    updates = {k:v for k,v in d.items() if k in allowed}
    if not updates:
        return jsonify(error="No valid fields supplied"), 400
    if "agreed_qty" in updates:
        try:
            updates["agreed_qty"] = float(updates["agreed_qty"])
            if updates["agreed_qty"] <= 0: raise ValueError()
        except (TypeError, ValueError):
            return jsonify(error="Agreed quantity must be positive"), 400
    sql = ", ".join(f"{k}=?" for k in updates)
    with db() as con:
        cur = con.execute(f"UPDATE requests SET {sql} WHERE id=?",
                          (*updates.values(), request_id))
        if cur.rowcount == 0: return jsonify(error="Request not found"), 404
        row = con.execute("""SELECT requests.*, produce.name AS produce_name,
          produce.farmer FROM requests JOIN produce ON produce.id=requests.produce_id
          WHERE requests.id=?""", (request_id,)).fetchone()
    return jsonify(dict(row))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
