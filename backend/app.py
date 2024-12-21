from flask import Flask, request, jsonify
from src.api.models.handle_domain import handle_domain
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/domain", methods=["POST"])
def domain_handler():
    """
    React frontend'den gelen domain isteklerini işler.
    """
    try:
        data = request.json
        domain = data.get("domain")
        if not domain:
            return jsonify({"status": "error", "message": "Domain is required"}), 400

        # IoC'yi işle
        result = handle_domain(domain)

        if result["status"] == "success":
            # Frontend'in beklediği formatı döndürün
            return (
                jsonify(
                    {
                        "IoC": result["data"]["IoC"],
                        "IP": result["data"].get("IP"),
                        "Type": result["data"]["Type"],
                        "Geometric_Location": result["data"].get("Geometric_Location"),
                        "City": result["data"].get("City"),
                        "Country": result["data"].get("Country"),
                        "Source": result["data"].get("Source"),
                        "Is_Valid": result["data"].get("Is_Valid"),
                        "Malicious": result["data"].get("Malicious"),  # Malicious eklendi
                        "Data_Breach": {
                            "Company_Name": result["data"].get("Company_Name"),
                            "Breach_Type": result["data"].get("Breach_Type"),
                            "Date_Published": result["data"].get("Date_Published"),
                            "Records_Affected": result["data"].get("Records_Affected"),
                            "Description": result["data"].get("Description"),
                        },
                    }
                ),
                200,
            )
        else:
            return jsonify({"status": "error", "message": result["message"]}), 500

    except Exception as e:
        print(f"Hata: {str(e)}")  # Konsolda hatayı yazdırır
        return (
            jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}),
            500,
        )



if __name__ == "__main__":
    app.run(debug=True)
