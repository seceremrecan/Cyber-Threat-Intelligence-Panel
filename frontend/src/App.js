import React, { useState } from "react";
import { Container, Form, Button, Navbar } from "react-bootstrap";
import "./App.css";
import DomainCard from "./domain";

const App = () => {
  const [domain, setDomain] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSearchBar, setShowSearchBar] = useState(true); // Search bar kontrolü
  const [snackbar, setSnackbar] = useState({
    show: false,
    message: "",
    isError: false,
  });
  const [validationError, setValidationError] = useState("");

  const showSnackbar = (message, isError = false) => {
    setSnackbar({ show: true, message, isError });
    setTimeout(() => setSnackbar({ show: false, message: "", isError: false }), 3000);
  };

  const validInputRegex =
    /^(https?:\/\/)?((([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6})|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(:\d{1,5})?(\/.*)?$|^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  const fetchDomainInfo = async () => {
    if (!domain.trim()) {
      setValidationError("Lütfen bir değer girin.");
      return;
    }

    if (!validInputRegex.test(domain)) {
      setValidationError("Geçersiz bir giriş yaptınız.");
      return;
    }

    setValidationError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/domain", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ domain: domain.trim() }),
      });

      if (response.ok) {
        const data = await response.json();
        setResults({ ...data, inputDomain: domain.trim() });
        setShowSearchBar(false); // Search barı gizle
        showSnackbar("Data fetched successfully!", false);
      } else {
        console.error("API request failed");
        showSnackbar("Failed to fetch data.", true);
      }
    } catch (error) {
      console.error("Error fetching domain info:", error);
      showSnackbar("An error occurred while fetching data.", true);
    }

    setLoading(false);
  };

  return (
    <div className="app-background">
      {/* Navbar */}
      <Navbar bg="dark" variant="dark" expand="lg" className="fixed-top">
        <Container>
          <Navbar.Brand href="#" className="text-success">
            Dev<span style={{ color: "#198754" }}>CTI</span>
          </Navbar.Brand>
          {results && (
            <div className="ms-auto text-end text-white d-flex align-items-center">
              <img
                src={`https://icon.horse/icon/${results.inputDomain}`}
                alt={`${results.inputDomain} icon`}
                style={{
                  width: "24px",
                  height: "24px",
                  borderRadius: "4px",
                  marginRight: "8px",
                }}
              />
              <div>
                <h5 className="m-0">{results.inputDomain}</h5>
                <p className="m-0" style={{ fontStyle: "italic", fontSize: "14px" }}>
                  {results.Type}
                </p>
              </div>
            </div>
          )}
        </Container>
      </Navbar>

      {showSearchBar && (
        <Container
          className="container-content d-flex flex-column align-items-center justify-content-start"
          style={{ paddingTop: "80px" }}
        >
          <Form
            className="position-relative d-flex justify-content-center align-items-center mt-3 w-50"
            onSubmit={(e) => {
              e.preventDefault();
              fetchDomainInfo();
            }}
          >
            <div className="position-relative w-100">
              <Form.Control
                type="text"
                placeholder="Enter a domain, URL, Email, IP, and more..."
                className={`search-bar ${validationError ? "is-invalid" : ""}`}
                value={domain}
                onChange={(e) => setDomain(e.target.value.replace(/\s+/g, ""))}
              />
              {validationError && <div className="invalid-tooltip">{validationError}</div>}
            </div>
            <Button variant="success" className="ms-2" onClick={fetchDomainInfo}>
              Search
            </Button>
          </Form>
        </Container>
      )}
      {/* Boşluk için div */}
      {!showSearchBar && <div style={{ height: "100px" }}></div>}

      {/* Loading Spinner */}
      {loading && (
        <div className="overlay">
          <div className="loader"></div>
        </div>
      )}

      {/* Results */}
      {results && <DomainCard results={results} />}

      {/* Snackbar */}
      {snackbar.show && (
        <div id="snackbar" className={snackbar.isError ? "show error" : "show"}>
          {snackbar.message}
        </div>
      )}
    </div>
  );
};

export default App;
