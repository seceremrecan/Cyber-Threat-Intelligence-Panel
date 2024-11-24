import React, { useState } from "react";
import "./domain.css";

const DomainCard = ({ results }) => {
  const [popupVisible, setPopupVisible] = useState({});
  const [copiedMessage, setCopiedMessage] = useState(false);

  if (!results) return null;

  // Popup'u açıp kapama
  const togglePopup = (key) => {
    setPopupVisible((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // Bilgiyi kopyalama
  const copyInfo = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedMessage(true);
      setTimeout(() => setCopiedMessage(false), 3000); // Snackbar'ı 3 saniye sonra gizle
    });
  };

  return (
    <div className="results-card">
      {/* IoC */}
      <div className="card-item">
        <h4>IoC</h4>
        <p>{results.IoC}</p>
        <div className="info-btn" onClick={() => togglePopup("IoC")}>
          i
        </div>
        <div className="copy-btn" onClick={() => copyInfo(results.IoC)}>
          📋
        </div>
        {popupVisible["IoC"] && (
          <div className="popup-content">{results.IoC}</div>
        )}
      </div>

      {/* IP */}
      <div className="card-item">
        <h4>IP</h4>
        <p>{results.IP}</p>
        <div className="info-btn" onClick={() => togglePopup("IP")}>
          i
        </div>
        <div className="copy-btn" onClick={() => copyInfo(results.IP)}>
          📋
        </div>
        {popupVisible["IP"] && (
          <div className="popup-content">{results.IP}</div>
        )}
      </div>

      {/* Type */}
      <div className="card-item">
        <h4>Type</h4>
        <p>{results.Type}</p>
        <div className="info-btn" onClick={() => togglePopup("Type")}>
          i
        </div>
        <div className="copy-btn" onClick={() => copyInfo(results.Type)}>
          📋
        </div>
        {popupVisible["Type"] && (
          <div className="popup-content">{results.Type}</div>
        )}
      </div>

      {/* Geometric Location */}
      <div className="card-item">
        <h4>Geometric Location</h4>
        <p>{results.Geometric_Location}</p>
        <div className="info-btn" onClick={() => togglePopup("Geometric_Location")}>
          i
        </div>
        <div
          className="copy-btn"
          onClick={() => copyInfo(results.Geometric_Location)}
        >
          📋
        </div>
        {popupVisible["Geometric_Location"] && (
          <div className="popup-content">{results.Geometric_Location}</div>
        )}
      </div>

      {/* City */}
      <div className="card-item">
        <h4>City</h4>
        <p>{results.City}</p>
        <div className="info-btn" onClick={() => togglePopup("City")}>
          i
        </div>
        <div className="copy-btn" onClick={() => copyInfo(results.City)}>
          📋
        </div>
        {popupVisible["City"] && (
          <div className="popup-content">{results.City}</div>
        )}
      </div>

      {/* Country */}
      <div className="card-item">
        <h4>Country</h4>
        <p>{results.Country}</p>
        <div className="info-btn" onClick={() => togglePopup("Country")}>
          i
        </div>
        <div className="copy-btn" onClick={() => copyInfo(results.Country)}>
          📋
        </div>
        {popupVisible["Country"] && (
          <div className="popup-content">{results.Country}</div>
        )}
      </div>

      {/* Snackbar for Copy */}
      {copiedMessage && (
        <div id="snackbar" className="show">
          Information copied!
        </div>
      )}
    </div>
  );
};

export default DomainCard;
