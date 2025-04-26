import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import 'antd/dist/reset.css';
import './index.css';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter> basename="/divvyviz.github.io"
    <App />
  </BrowserRouter>
);
//``` :contentReference[oaicite:14]{index=14}