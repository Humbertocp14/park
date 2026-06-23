from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import psycopg
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

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

    # Emitir a todos los clientes conectados
    socketio.emit("zona_actualizada", {"id": zona_id, "estado": nuevo_estado})

    return jsonify({"id": zona_id, "estado": nuevo_estado})

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
