import React from "react";
import "./domain.css";

const DomainCard = ({ results }) => {
  if (!results) return null;

  const groupedCards = [
    {
      title: "Possible Threat",
      items: [
        { key: "Address Status", value: results.Is_Valid  },
        { key: "Malicious", value: results.Malicious },
        { key: "Source", value: results.Source  },
      ],
    },
    {
      title: "Location Details",
      items: [
        { key: "City", value: results.City  },
        { key: "Country", value: results.Country },
        { key: "Geometric Location", value: results.Geometric_Location  },
      ],
    },
    {
      title: "Data Breach Details",
      items: [
        { key: "Company Name", value: results.Data_Breach?.Company_Name },
        { key: "Breach Type", value: results.Data_Breach?.Breach_Type  },
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
          {/* <thead>
            <tr>
              <th>Policy</th>
              <th>Status</th>
            </tr>
          </thead> */}
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
    </div>
  );
};

export default DomainCard;
