from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import pandas as pd
import uuid

app = Flask(__name__)

# Charger les données depuis le fichier Excel au démarrage
data_file = "Inventaire_Matos_DJ_Codes.xlsx"
df = pd.read_excel(data_file)
df.fillna("", inplace=True)

# Ajouter un identifiant unique à chaque ligne si non présent
if 'ID' not in df.columns:
    df.insert(0, 'ID', [str(uuid.uuid4()) for _ in range(len(df))])
    df.to_excel(data_file, index=False)

# Route GET pour lister tous les items
@app.route("/api/items", methods=["GET"])
def get_items():
    return jsonify(df.to_dict(orient="records"))

# Route GET pour un seul item par ID
@app.route("/api/items/<item_id>", methods=["GET"])
def get_item(item_id):
    item = df[df['ID'] == item_id]
    if item.empty:
        abort(404)
    return jsonify(item.iloc[0].to_dict())

# Route POST pour ajouter un nouvel item
@app.route("/api/items", methods=["POST"])
def add_item():
    new_item = request.json
    new_item['ID'] = str(uuid.uuid4())
    global df
    df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
    df.to_excel(data_file, index=False)
    return jsonify(new_item), 201

# Route PUT pour modifier un item existant
@app.route("/api/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    global df
    index = df.index[df['ID'] == item_id].tolist()
    if not index:
        abort(404)
    for key, value in request.json.items():
        if key in df.columns and key != 'ID':
            df.at[index[0], key] = value
    df.to_excel(data_file, index=False)
    return jsonify(df.iloc[index[0]].to_dict())

# Route DELETE pour supprimer un item
@app.route("/api/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    global df
    index = df.index[df['ID'] == item_id].tolist()
    if not index:
        abort(404)
    df = df.drop(index[0])
    df.to_excel(data_file, index=False)
    return '', 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)
