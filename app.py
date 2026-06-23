from flask import Flask, jsonify
from flask_cors import CORS
import psycopg
import os

app = Flask(__name__)
CORS(app)

def get_db():
    url = os.environ.get("DATABASE_URL")
    if url:
        return psycopg.connect(url)
    return psycopg.connect(
        host="localhost",
        dbname="park",
        user="postgres",
        password="Betochin2683"
    )

@app.route("/api/zonas", methods=["GET"])
def get_zonas():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, estado, bbox_x, bbox_y, bbox_width, bbox_height, puntos, updated_at FROM zonas ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    zonas = [
        {
            "id": r[0],
            "estado": r[1],
            "bbox_x": r[2],
            "bbox_y": r[3],
            "bbox_width": r[4],
            "bbox_height": r[5],
            "puntos": r[6],
            "updated_at": r[7].isoformat() if r[7] else None,
        }
        for r in rows
    ]
    return jsonify(zonas)

@app.route("/api/zonas/<int:zona_id>/toggle", methods=["PUT"])
def toggle_zona(zona_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT estado FROM zonas WHERE id = %s", [zona_id])
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Zona no encontrada"}), 404

    nuevo_estado = "ocupado" if row[0] == "libre" else "libre"
    cur.execute(
        "UPDATE zonas SET estado = %s, updated_at = NOW() WHERE id = %s",
        [nuevo_estado, zona_id]
    )
    conn.commit()
    conn.close()
    return jsonify({"id": zona_id, "estado": nuevo_estado})

@app.route("/api/bardas", methods=["GET"])
def get_bardas():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, x1, y1, x2, y2 FROM bardas ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "x1": r[1], "y1": r[2], "x2": r[3], "y2": r[4]} for r in rows])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
