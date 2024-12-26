import React from "react";
import "./domain.css";
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
        { key: "Records Affected", value: results.Data_Breach?.Records_Affected },
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
        <h4>WHOIS Data</h4>
        <div>{whoisData ? renderNestedData(whoisData) : "No WHOIS data found."}</div>
      </div>
  {/* DNS Records Card */}
  {dnsRecords && (
    <div className="card-item dns-records-card">
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
                  <td>{record.ips?.map((ip) => ip.ip).join(", ") || "-"}</td>
                  <td>{record.ips?.map((ip) => ip.asn).join(", ") || "-"}</td>
                  <td>{record.ips?.map((ip) => ip.asn_name).join(", ") || "-"}</td>
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
    <h4>robots.txt Disallow Rules</h4>
    <ul>
      {robotsDisallows.length > 0 ? (
        robotsDisallows.map((rule, index) => <li key={index}>{rule}</li>)
      ) : (
        <li>No disallow rules found</li>
      )}
    </ul>
  </div>
</div>

  );
};

export default DomainCard;
