import React from "react";
import { Container, Form, Button, Navbar, Nav } from "react-bootstrap";
import './App.css';

const App = () => {
  return (
    <div>
      {/* Navbar */}
      <Navbar bg="light" expand="lg">
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
        className="d-flex flex-column align-items-center justify-content-start"
        style={{ height: "100%", paddingTop: "100px" }}
      >
        
        <Form className="d-flex justify-content-center mt-3 w-50">
          <Form.Control
            type="text"
            placeholder="Enter a domain, URL, Email, IP, CIDR, Bitcoin address, and more..."
            className="w-100"
          />
          <Button variant="success" className="ms-2">
            Search
          </Button>
        </Form>
      </Container>
    </div>
  );
};

export default App;
