# from flask import Flask, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # React ile çalışmak için CORS etkinleştirildi

# @app.route('/api/malicious-domains', methods=['GET'])
# def get_domains():
#     data = [
#         {"domain": "malicious-site.com", "threat_level": "high"},
#         {"domain": "phishing-site.net", "threat_level": "medium"}
#     ]
#     return jsonify(data)

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)
