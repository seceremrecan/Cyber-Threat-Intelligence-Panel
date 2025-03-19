import "./domain.css";
import React, { useState } from "react";
import aiIcon from "./assets/images/icons8-ai-24.png";

const renderNestedData = (data) => {
  if (typeof data === "object" && data !== null) {
    return (
      <ul>
        {Object.entries(data).map(([key, value]) => (
          <li key={key}>
            <strong>{key.replace(/_/g, " ")}:</strong> {renderNestedData(value)}
          </li>
        ))}
      </ul>
    );
  }
  return data ? data.toString() : "Unknown";
};
const DomainCard = ({ results }) => {
  console.log("API Results: ", results);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  // Yapay zeka analiz fonksiyonu
  const handleAiAnalyze = async (dataToAnalyze, category) => {
    if (!dataToAnalyze || Object.keys(dataToAnalyze).length === 0) {
      console.error(`❌ [Hata] ${category} için geçerli bir veri yok!`);
      return;
    }

    let formattedData;

    if (Array.isArray(dataToAnalyze)) {
      if (typeof dataToAnalyze[0] === "string") {
        // 📌 Eğer gelen veri düz metinlerden oluşuyorsa (örneğin robots.txt)
        formattedData = dataToAnalyze.map((rule, index) => ({
          policy: `Rule ${index + 1}`, // Her kural için "Rule 1", "Rule 2" şeklinde isim ver
          status: rule, // İçeriği olduğu gibi status olarak kaydet
        }));
      } else {
        // 📌 Eğer JSON formatındaysa, doğrudan al
        formattedData = dataToAnalyze.map((item) => ({
          policy: item.key || item.policy,
          status: item.value || item.status,
        }));
      }
    } else {
      // 📌 Gelen veri bir nesne ise (örneğin WHOIS Data gibi)
      formattedData = Object.entries(dataToAnalyze).map(([key, value]) => ({
        policy: key,
        status: typeof value === "object" ? JSON.stringify(value) : value,
      }));
    }

    console.log(`📤 [Gönderilen Veri] (${category}):`, formattedData);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ analysis_data: formattedData }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log(`📥 [Yapay Zeka Cevabı] (${category}):`, result.analysis);
        setAiAnalysis(result.analysis);
      } else {
        console.error(`❌ [Hata] ${category} analizi başarısız.`);
      }
    } catch (error) {
      console.error(
        `❌ [Hata] ${category} analiz sırasında bir sorun oluştu:`,
        error
      );
    }

    setLoading(false);
  };

  if (!results) return null;

  const groupedCards = [
    {
      title: "Possible Threat",
      items: [
        { key: "Address Status", value: results.Is_Valid },
        { key: "Malicious", value: results.Malicious },
        { key: "Source", value: results.Source },
      ],
    },
    {
      title: "Location Details",
      items: [
        { key: "City", value: results.City },
        { key: "Country", value: results.Country },
        { key: "Geometric Location", value: results.Geometric_Location },
      ],
    },
    {
      title: "Website Status",
      items: [
        { key: "UP Status", value: results.Website_Status?.UP_Status },
        { key: "Last Down", value: results.Website_Status?.Last_Down },
      ],
    },

    {
      title: "Data Breach Details",
      items: [
        { key: "Company Name", value: results.Data_Breach?.Company_Name },
        { key: "Breach Type", value: results.Data_Breach?.Breach_Type },
        { key: "Date Published", value: results.Data_Breach?.Date_Published },
        {
          key: "Records Affected",
          value: results.Data_Breach?.Records_Affected,
        },
      ],
    },
  ];

  // Varsayılan HTTP Security verileri
  const defaultHttpSecurity = [
    { policy: "Content Security Policy", status: "No" },
    { policy: "Strict Transport Policy", status: "No" },
    { policy: "X-Content-Type-Options", status: "No" },
    { policy: "X-Frame-Options", status: "No" },
    { policy: "X-XSS-Protection", status: "No" },
  ];

  const httpSecurity = results.Http_Security?.length
    ? results.Http_Security
    : defaultHttpSecurity;

  const dnsRecords = results.DNS_Records;
  const robotsDisallows = results.Robots_Disallows || [];
  const whoisData = results.WHOIS_Data;
  return (
    <div className="results-card">
      {groupedCards.map((group, index) => (
        <div key={index} className="card-item">
          <button
            className="ai-analyze-btn"
            onClick={() => handleAiAnalyze(group.items, group.title)}
          >
            {" "}
            <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
          </button>

          <div>
            {group.items.map((item, idx) => (
              <div key={idx} className="popup-item">
                <strong>{item.key}:</strong> {item.value}
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* HTTP Security Card */}
      <div className="card-item http-security-card">
        <button
          className="ai-analyze-btn"
          onClick={() => handleAiAnalyze(httpSecurity, "HTTP Security")}
        >
          {" "}
          <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
        </button>
        <h4>HTTP Security</h4>
        <table className="http-security-table">
          <tbody>
            {httpSecurity.map((item, index) => (
              <tr key={index} className={item.status === "Yes" ? "yes" : "no"}>
                <td>{item.policy}</td>
                <td>{item.status === "Yes" ? "✔️ Yes" : "❌ No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* WHOIS Data */}
      <div className="card-item">
        <button
          className="ai-analyze-btn"
          onClick={() => handleAiAnalyze(results.WHOIS_Data, "WHOIS Data")}
        >
          {" "}
          <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
        </button>
        <h4>WHOIS Data</h4>
        <div>
          {whoisData ? renderNestedData(whoisData) : "No WHOIS data found."}
        </div>
      </div>
      {/* DNS Records Card */}
      {dnsRecords && (
        <div className="card-item dns-records-card">
          <button
            className="ai-analyze-btn"
            onClick={() => handleAiAnalyze(results.DNS_Records, "DNS Records")}
          >
            {" "}
            <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
          </button>
          <h4>DNS Records</h4>
          <div>
            <table className="dns-records-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Host</th>
                  <th>IP</th>
                  <th>ASN</th>
                  <th>ASN Name</th>
                </tr>
              </thead>
              <tbody>
                {["a", "mx", "ns"].map((recordType) =>
                  dnsRecords[recordType]?.map((record, idx) => (
                    <tr key={`${recordType}-${idx}`}>
                      <td>{recordType.toUpperCase()}</td>
                      <td>{record.host || "-"}</td>
                      <td>
                        {record.ips?.map((ip) => ip.ip).join(", ") || "-"}
                      </td>
                      <td>
                        {record.ips?.map((ip) => ip.asn).join(", ") || "-"}
                      </td>
                      <td>
                        {record.ips?.map((ip) => ip.asn_name).join(", ") || "-"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Robots.txt Disallow Rules */}
      <div className="card-item robots-card">
        <button
          className="ai-analyze-btn"
          onClick={() =>
            handleAiAnalyze(
              results.Robots_Disallows,
              "Robots.txt Disallow Rules"
            )
          }
        >
          {" "}
          <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
        </button>
        <h4>robots.txt Disallow Rules</h4>
        <ul>
          {robotsDisallows.length > 0 ? (
            robotsDisallows.map((rule, index) => <li key={index}>{rule}</li>)
          ) : (
            <li>No disallow rules found</li>
          )}
        </ul>
      </div>
      {/* Yapay Zeka Analiz Popup */}
{aiAnalysis && (
  <div className={`ai-popup ${isExpanded ? "ai-popup-fullscreen" : ""}`}>
    <div className="ai-popup-header">
      <h3>🔍 AI Analysis Result</h3>
      <button className="expand-btn" onClick={toggleExpand}>
        {isExpanded ? "↩ Küçült" : "🖥 Tam Ekran"}
      </button>
    </div>
    <div className="ai-analysis-text">
      {aiAnalysis.split("**").map((section, index) => (
        <p key={index}>
          {section.includes(":") ? <strong>{section.split(":")[0]}:</strong> : ""}
          {section.includes(":") ? section.split(":")[1] : section}
        </p>
      ))}
    </div>
    <div className="popup-footer">
      <button className="close-btn" onClick={() => setAiAnalysis(null)}>Kapat</button>
    </div>
  </div>
)}


      {/* Loading Spinner */}
      {loading && <div className="loading-overlay">Analyzing...</div>}
    </div>
  );
};

export default DomainCard;
