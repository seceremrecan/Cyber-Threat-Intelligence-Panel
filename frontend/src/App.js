import React, { useState } from "react";
import { Container, Form, Button, Navbar, Nav } from "react-bootstrap";
import "./App.css";
import DomainCard from "./domain"; // DomainCard bileşenini ekliyoruz

const App = () => {
  const [domain, setDomain] = useState(""); // Kullanıcının girdiği domain
  const [results, setResults] = useState(null); // API'den alınan sonuçlar
  const [loading, setLoading] = useState(false); // API çağrısı sırasında durum
  const [snackbar, setSnackbar] = useState({ show: false, message: "", isError: false });

  // Snackbar'ı göstermek için bir fonksiyon
  const showSnackbar = (message, isError = false) => {
    setSnackbar({ show: true, message, isError });
    setTimeout(() => setSnackbar({ show: false, message: "", isError: false }), 3000);
  };

  // Flask backend'den veri çekmek için kullanılan fonksiyon
  const fetchDomainInfo = async () => {
    if (!domain) return; // Eğer domain boşsa işlem yapma
    setLoading(true);

    try {
      // Flask API'ye istek gönder
      const response = await fetch("http://localhost:5000/api/domain", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ domain }), // Backend'e domain gönder
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data); // Backend'den gelen veriyi kaydet
        console.log(data);
        showSnackbar("Data sent successfully!", false); // Başarılı bildirim
      } else {
        setResults(null);
        console.error("API request failed.");
        showSnackbar("Failed to fetch data.", true); // Hata bildirimi
      }
    } catch (error) {
      console.error("Error fetching domain info:", error);
      setResults(null);
      showSnackbar("An error occurred while fetching data.", true); // Hata bildirimi
    }
    setLoading(false);
  };

  return (
    <div>
      {/* Navbar */}
      <Navbar bg="light" expand="lg" className="fixed-top">
        <Container>
          <Navbar.Brand href="#">
            <span style={{ fontWeight: "bold", color: "#007bff" }}></span>
            Dev<span style={{ color: "#007bff" }}>CTI</span>
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="ms-auto">
              <Nav.Link href="#">About</Nav.Link>
              <Nav.Link href="#">Product</Nav.Link>
              <Nav.Link href="#">Blog</Nav.Link>
              <Nav.Link href="#">Tools</Nav.Link>
              <Nav.Link href="#">Integrations</Nav.Link>
              <Button variant="outline-primary" className="mx-2">
                Login
              </Button>
              <Button variant="primary">Sign up</Button>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      {/* Main Content */}
      <Container
        className="container-content d-flex flex-column align-items-center justify-content-start"
        style={{ paddingTop: "100px" }}
      >
        <Form
          className="d-flex justify-content-center mt-3 w-50"
          onSubmit={(e) => {
            e.preventDefault();
            fetchDomainInfo();
          }}
        >
          <Form.Control
            type="text"
            placeholder="Enter a domain, URL, Email, IP, and more..."
            className="w-100"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
          />
          <Button variant="success" className="ms-2" onClick={fetchDomainInfo}>
            Search
          </Button>
        </Form>

        {/* Loading Indicator */}
        {loading && (
          <div className="overlay">
            <div className="loader"></div>
          </div>
        )}

        {/* DomainCard Component */}
        {results && <DomainCard results={results} />}
      </Container>

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
