import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Loading.css";

const Loading = () => {
  const navigate = useNavigate(); // React Router yönlendirme fonksiyonu

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/app"); // 2 saniye sonra /app adresine yönlendir
    }, 2000); // 2 saniye bekleme süresi
    return () => clearTimeout(timer); // Temizleme
  }, [navigate]);

  return (
    <div className="center">
      <div className="ring"></div>
      <span>Loading...</span>
    </div>
  );
};

export default Loading;
