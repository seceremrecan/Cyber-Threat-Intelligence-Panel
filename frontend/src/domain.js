import "./domain.css";
import React, { useState, useEffect } from "react";
import aiIcon from "./assets/images/icons8-ai-24.png";
import ReactMarkdown from "react-markdown";

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
  // Ek state
  const [showPanel, setShowPanel] = useState(false);

  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loadingCategory, setLoadingCategory] = useState(null);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    if (isExpanded && aiAnalysis?.content) {
      console.log("AI POPUP VERİSİ:", aiAnalysis.content);
    }
  }, [isExpanded, aiAnalysis]);

  // AI sonucu geldiğinde popup'ı otomatik göster
useEffect(() => {
  if (notification?.category) {
    const result = analysisResults.find(r => r.category === notification.category);
    if (result) {
      setAiAnalysis(result);
      setIsExpanded(true); // otomatik popup aç
      setNotification(null); // bildirimi sıfırla
    }
  }
}, [notification, analysisResults]);


  const handleAiAnalyze = async (dataToAnalyze, category) => {
    if (!dataToAnalyze || Object.keys(dataToAnalyze).length === 0) {
      console.error(`❌ [Hata] ${category} için geçerli bir veri yok!`);
      return;
    }

    let formattedData;

    if (Array.isArray(dataToAnalyze)) {
      if (typeof dataToAnalyze[0] === "string") {
        formattedData = dataToAnalyze.map((rule, index) => ({
          policy: `Rule ${index + 1}`,
          status: rule,
        }));
      } else {
        formattedData = dataToAnalyze.map((item) => ({
          policy: item.key || item.policy,
          status: item.value || item.status,
        }));
      }
    } else {
      formattedData = Object.entries(dataToAnalyze).map(([key, value]) => ({
        policy: key,
        status: typeof value === "object" ? JSON.stringify(value) : value,
      }));
    }

    setLoadingCategory(category);

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
        const newResult = {
          category,
          content:
            typeof result.analysis === "string"
              ? result.analysis
              : result.analysis.content || JSON.stringify(result.analysis),
        };

        setAnalysisResults((prev) => {
          const alreadyExists = prev.find((r) => r.category === category);
          return alreadyExists
            ? prev.map((r) => (r.category === category ? newResult : r))
            : [...prev, newResult];
        });

        setNotification({ category }); // Bildirim için
      } else {
        console.error(`❌ [Hata] ${category} analizi başarısız.`);
      }
    } catch (error) {
      console.error(
        `❌ [Hata] ${category} analiz sırasında bir sorun oluştu:`,
        error
      );
    }

    setLoadingCategory(null);
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

  const httpSecurity = results.Http_Security?.length
    ? results.Http_Security
    : [
        { policy: "Content Security Policy", status: "No" },
        { policy: "Strict Transport Policy", status: "No" },
        { policy: "X-Content-Type-Options", status: "No" },
        { policy: "X-Frame-Options", status: "No" },
        { policy: "X-XSS-Protection", status: "No" },
      ];

  const dnsRecords = results.DNS_Records;
  const robotsDisallows = results.Robots_Disallows || [];
  const whoisData = results.WHOIS_Data;
  const flattenDnsRecords = (dnsData) => {
    const flat = [];
    ["a", "mx", "ns"].forEach((type) => {
      dnsData[type]?.forEach((record) => {
        record.ips?.forEach((ipInfo) => {
          flat.push({
            policy: `${type.toUpperCase()} - ${record.host || "-"}`,
            status: `${ipInfo.ip || "-"} | ASN: ${
              ipInfo.asn || "-"
            } | ASN Name: ${ipInfo.asn_name || "-"}`,
          });
        });
      });
    });
    return flat;
  };

  const flattenWhoisData = (data) => {
    const flat = [];
    const walk = (obj, prefix = "") => {
      for (const [key, value] of Object.entries(obj)) {
        if (typeof value === "object" && value !== null) {
          walk(value, `${prefix}${key}.`);
        } else {
          flat.push({
            policy: `${prefix}${key}`,
            status: String(value),
          });
        }
      }
    };
    walk(data);
    return flat;
  };

  return (
    <div className="results-card">
      {groupedCards.map((group, index) => (
        <div key={index} className="card-item">
          <button
            className="ai-analyze-btn"
            onClick={() => handleAiAnalyze(group.items, group.title)}
          >
            {loadingCategory === group.title ? (
              <div className="spinner" />
            ) : (
              <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
            )}
          </button>
          <h4>{group.title}</h4>
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
          {loadingCategory === "HTTP Security" ? (
            <div className="spinner" />
          ) : (
            <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
          )}
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
          onClick={() =>
            handleAiAnalyze(flattenWhoisData(whoisData), "WHOIS Data")
          }
        >
          {loadingCategory === "WHOIS Data" ? (
            <div className="spinner" />
          ) : (
            <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
          )}
        </button>
        <h4>WHOIS Data</h4>
        <div>
          {whoisData ? renderNestedData(whoisData) : "No WHOIS data found."}
        </div>
      </div>
      {/* DNS Records */}
      {dnsRecords && (
        <div className="card-item dns-records-card">
          <button
            className="ai-analyze-btn"
            onClick={() =>
              handleAiAnalyze(flattenDnsRecords(dnsRecords), "DNS Records")
            }
          >
            {loadingCategory === "DNS Records" ? (
              <div className="spinner" />
            ) : (
              <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
            )}
          </button>
          <h4>DNS Records</h4>
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
              {["a", "mx", "ns"].map((type) =>
                dnsRecords[type]?.map((record, idx) => (
                  <tr key={`${type}-${idx}`}>
                    <td>{type.toUpperCase()}</td>
                    <td>{record.host || "-"}</td>
                    <td>{record.ips?.map((ip) => ip.ip).join(", ") || "-"}</td>
                    <td>{record.ips?.map((ip) => ip.asn).join(", ") || "-"}</td>
                    <td>
                      {record.ips?.map((ip) => ip.asn_name).join(", ") || "-"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
      {/* Robots.txt */}
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
          {loadingCategory === "Robots.txt Disallow Rules" ? (
            <div className="spinner" />
          ) : (
            <img src={aiIcon} alt="AI Analyze" className="ai-icon" />
          )}
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
      {/* AI Analysis Popup */}
      {isExpanded && aiAnalysis?.content && (
        <div className={`ai-popup ${isExpanded ? "ai-popup-fullscreen" : ""}`}>
          <div className="ai-popup-header">
            <h3>🔍 AI Analysis Result ({aiAnalysis.category})</h3>
            {/* */}
          </div>

          <div className="ai-analysis-text">
            {aiAnalysis.content.split("**").map((section, index) => (
              <p key={index}>
                {section.includes(":") ? (
                  <strong>{section.split(":")[0]}:</strong>
                ) : (
                  ""
                )}
                {section.includes(":") ? section.split(":")[1] : section}
              </p>
            ))}
          </div>

          <div className="popup-footer">
            <button
              className="close-btn"
              onClick={() => {
                setIsExpanded(false);
                setAiAnalysis(null);
              }}
            >
              Kapat
            </button>
          </div>
        </div>
      )}
      
      {analysisResults.length > 0 && (
        <div className="analysis-floating-badge">
          <div
            className="analysis-fab"
            onClick={() => setShowPanel((prev) => !prev)}
            title="AI Analiz Sonuçlarını Göster"
          >
            🧠
          </div>

          {showPanel && (
            <div className="analysis-hover-panel fixed">
              {analysisResults.map((item, idx) => (
                <div
                  key={idx}
                  className="analysis-notification-card"
                  onClick={() => {
                    setAiAnalysis(item);
                    setIsExpanded(true);
                    setShowPanel(false); // tıkladıktan sonra paneli kapat
                  }}
                >
                  <h4>{item.category}</h4>
                  <p>Sonucu görmek için tıkla.</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DomainCard;
