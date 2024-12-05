import React, { useState } from "react";
import "./domain.css";

const DomainCard = ({ results }) => {

  console.log("Results in DomainCard:", results);
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
      </div>

      {/* Source */}
      <div className="card-item">
        <h4>Source</h4>
        <p>{results.Source}</p>
      </div>

      {/* Category */}
      <div className="card-item">
        <h4>Category</h4>
        <p>{results.Category}</p>
      </div>

      {/* Is Valid */}
      <div className="card-item">
        <h4>Is Valid</h4>
        <p>{results.Is_Valid ? "Yes" : "No"}</p>
      </div>

      {/* Type */}
      <div className="card-item">
        <h4>Type</h4>
        <p>{results.Type}</p>
      </div>

  

      {/* Geometric Location */}
      <div className="card-item">
        <h4>Geometric Location</h4>
        <p>{results.Geometric_Location}</p>
      </div>

      {/* City */}
      <div className="card-item">
        <h4>City</h4>
        <p>{results.City}</p>
      </div>

      {/* Country */}
      <div className="card-item">
        <h4>Country</h4>
        <p>{results.Country}</p>
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
