from flask import Flask, request, jsonify
import joblib
from src.api.models.handle_domain import handle_domain
from flask_cors import CORS
import ollama

app = Flask(__name__)
CORS(app)

model_name = "llama3.1:8b"


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
                        "Malicious": result["data"].get(
                            "Malicious"
                        ),  # Malicious eklendi
                        "Data_Breach": {
                            "Company_Name": result["data"].get("Company_Name"),
                            "Breach_Type": result["data"].get("Breach_Type"),
                            "Date_Published": result["data"].get("Date_Published"),
                            "Records_Affected": result["data"].get("Records_Affected"),
                            "Description": result["data"].get("Description"),
                        },
                        "Website_Status": {
                            "UP_Status": result["data"]["Website_Status"].get("status"),
                            "Last_Down": result["data"]["Website_Status"].get(
                                "last_down"
                            ),
                        },
                        "Http_Security": result["data"].get(
                            "Http_Security",
                        ),
                        "DNS_Records": result["data"].get("DNS_Records", {}),
                        "Robots_Disallows": result["data"].get("Robots_Disallows", []),
                        "WHOIS_Data": result["data"].get("WHOIS_Data", {}),
                    }
                ),
                200,
                print(
                    result["data"].get(
                        "Http_Security",
                    )
                ),
            )

        else:
            return jsonify({"status": "error", "message": result["message"]}), 500

    except Exception as e:
        print(f"Hata: {str(e)}")  # Konsolda hatayı yazdırır
        return (
            jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}),
            500,
        )


@app.route("/api/analyze", methods=["POST"])
def analyze_data():
    try:
        data = request.json
        print("Gelen Veri:", data)  # Gelen JSON'u yazdır

        if not data or "analysis_data" not in data:
            return jsonify({"error": "Invalid request data"}), 400

        security_policies = data["analysis_data"]
        formatted_text = "\n".join(
            [f"{item['policy']}: {item['status']}" for item in security_policies]
        )

        query = f"""
        Burada bir web sitesinin güvenlik başlıkları var:
        {formatted_text}

        Bu bilgiler ışığında:
        1. Özet geç
        2. Olası riskleri belirt
        3. Koruma önlemlerini açıkla
        4. Geliştirme önerileri sun
        """

        print("Yapay zekaya gönderilen query:", query)

        response = ollama.chat(
            model=model_name, messages=[{"role": "user", "content": query}]
        )
        print("Yapay Zeka Cevabı:", response)  # Yapay zeka cevabını logla

        return jsonify({"analysis": response["message"]["content"]}), 200

    except Exception as e:
        print("Hata:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
