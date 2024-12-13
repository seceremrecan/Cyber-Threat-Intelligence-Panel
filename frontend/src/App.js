import React, { useState } from "react";
import { Container, Form, Button, Navbar } from "react-bootstrap";
import "./App.css";
import DomainCard from "./domain";

const App = () => {
  const [domain, setDomain] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    show: false,
    message: "",
    isError: false,
  });
  const [validationError, setValidationError] = useState(""); // Validasyon hatası için state

  const showSnackbar = (message, isError = false) => {
    setSnackbar({ show: true, message, isError });
    setTimeout(
      () => setSnackbar({ show: false, message: "", isError: false }),
      3000
    );
  };

  const validInputRegex = /^(https?:\/\/)?((([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6})|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))(:\d{1,5})?(\/.*)?$|^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  const fetchDomainInfo = async () => {
    // Önce validation kontrolü
    if (!domain.trim()) {
      setValidationError("Lütfen bir değer girin.");
      setResults(null); // Önceki verileri temizle
      return;
    }

    if (!validInputRegex.test(domain)) {
      setValidationError("Geçersiz bir giriş yaptınız. Lütfen kontrol edin.");
      setResults(null); // Önceki verileri temizle
      return;
    }

    // Validation hatasını temizle
    setValidationError("");

    // Önceki sonuçları temizle
    setResults(null);

    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/domain", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ domain: domain.replace(/\s+/g, '') })
, // Trim spaces before sending
      });

      if (response.ok) {
        const data = await response.json();
        setResults({ ...data, inputDomain: domain.trim() }); // Trim spaces here as well
        console.log(data);
        showSnackbar("Data sent successfully!", false);
      } else {
        const errorData = await response.json();
        console.error("API request failed with response:", errorData);
        showSnackbar("Failed to fetch data.", true);
      }
    } catch (error) {
      console.error("Error fetching domain info:", error);
      setResults(null);
      showSnackbar("An error occurred while fetching data.", true);
    }

    setLoading(false);
  };

  return (
    <div className="app-background">
      <Navbar bg="dark" variant="dark" expand="lg" className="fixed-top">
        <Container>
          <Navbar.Brand href="#" className="text-success">
            Dev<span style={{ color: "#198754" }}>CTI</span>
          </Navbar.Brand>
          {results && (
            <div className="ms-auto text-end text-white">
              <h5 className="m-0">{results.inputDomain}</h5>
              <p
                className="m-0"
                style={{ fontStyle: "italic", fontSize: "14px" }}
              >
                {results.Type}
              </p>
            </div>
          )}
        </Container>
      </Navbar>

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
              onChange={(e) => setDomain(e.target.value.replace(/\s+/g, ''))}
            />
            {validationError && (
              <div className="invalid-tooltip">{validationError}</div>
            )}
          </div>
          <Button variant="success" className="ms-2" onClick={fetchDomainInfo}>
            Search
          </Button>
        </Form>

        {loading && (
          <div className="overlay">
            <div className="loader"></div>
          </div>
        )}

        {results && <DomainCard results={results} />}
      </Container>

      {snackbar.show && (
        <div id="snackbar" className={snackbar.isError ? "show error" : "show"}>
          {snackbar.message}
        </div>
      )}
    </div>
  );
};

export default App;
