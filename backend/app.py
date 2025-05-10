from flask import Flask, request, jsonify
from flask_cors import CORS
from src.api.models.handle_domain import handle_domain
from dotenv import load_dotenv

load_dotenv()
import ollama
import os
import json

# .env dosyasını yükle


app = Flask(__name__)
CORS(app)

# Ollama client'ını .env üzerinden başlat
ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
ollama_client = ollama.Client(host=ollama_host)
model_name = "llama3.1:8b"


@app.route("/api/domain", methods=["POST"])
def domain_handler():
    try:
        data = request.json
        domain = data.get("domain")
        if not domain:
            return jsonify({"status": "error", "message": "Domain is required"}), 400

        result = handle_domain(domain)

        if result["status"] == "success":
            response_data = {
                "IoC": result["data"]["IoC"],
                "IP": result["data"].get("IP"),
                "Type": result["data"]["Type"],
                "Geometric_Location": result["data"].get("Geometric_Location"),
                "City": result["data"].get("City"),
                "Country": result["data"].get("Country"),
                "Source": result["data"].get("Source"),
                "Is_Valid": result["data"].get("Is_Valid"),
                "Malicious": result["data"].get("Malicious"),
                "Data_Breach": {
                    "Company_Name": result["data"].get("Company_Name"),
                    "Breach_Type": result["data"].get("Breach_Type"),
                    "Date_Published": result["data"].get("Date_Published"),
                    "Records_Affected": result["data"].get("Records_Affected"),
                    "Description": result["data"].get("Description"),
                },
                "Website_Status": {
                    "UP_Status": result["data"].get("Website_Status", {}).get("status"),
                    "Last_Down": result["data"]
                    .get("Website_Status", {})
                    .get("last_down"),
                },
                "Http_Security": result["data"].get("Http_Security"),
                "DNS_Records": result["data"].get("DNS_Records", {}),
                "Robots_Disallows": result["data"].get("Robots_Disallows", []),
                "WHOIS_Data": result["data"].get("WHOIS_Data", {}),
            }

            # print("📤 Dönen JSON Yanıtı:")
            # print(json.dumps(response_data, indent=2, ensure_ascii=False))

            return jsonify(response_data), 200
        else:
            return jsonify({"status": "error", "message": result["message"]}), 500

    except Exception as e:
        print(f"Hata: {str(e)}")
        return (
            jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}),
            500,
        )


@app.route("/api/analyze", methods=["POST"])
def analyze_data():
    try:
        data = request.json
        print("Gelen Veri:", data)

        if not data or "analysis_data" not in data:
            return jsonify({"error": "Invalid request data"}), 400

        security_policies = data["analysis_data"]
        formatted_text = "\n".join(
            [f"{item['policy']}: {item['status']}" for item in security_policies]
        )

        query = f"""
You are a senior cybersecurity threat intelligence analyst.

Provide a **structured** and **well-formatted** report in **Markdown** format. Use clear headings (##), bullet points, and bold text where necessary to improve readability.

Structure your analysis using the following format:

---

## 🔍 Executive Summary  
_A brief overview of the situation._

## 📌 Observations  
- Point out critical configurations and missing headers.  
- Use bullet points for clarity.

## 📉 Threat Level Assessment  
Explain severity (Low, Moderate, High, Critical) and why.

## ⚙ Technical Insights  
Summarize the technical reasons why the system is at risk.

## 🛡 Recommendations  
1. Recommendation 1  
2. Recommendation 2  
3. Recommendation 3

---

**ONLY return the Markdown-formatted analysis** with no extra commentary.

Data to analyze:
{formatted_text}
"""

        print("Yapay zekaya gönderilen query:", query)

        response = ollama_client.chat(
            model=model_name, messages=[{"role": "user", "content": query}]
        )

        print("Yapay Zeka Cevabı:", response)

        return jsonify({"analysis": str(response["message"]["content"])}), 200


    except Exception as e:
        print("Hata:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
