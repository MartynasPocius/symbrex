import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import './Main.css';

function Main() {
  const location = useLocation();
  const { uploadResponse } = location.state || {};
  const [selectedSupplier, setSelectedSupplier] = useState(null);

  useEffect(() => {
    if (uploadResponse && uploadResponse.output && uploadResponse.output.length > 0) {
      setSelectedSupplier(uploadResponse.output[0].supplier);
    }
  }, [uploadResponse]);

  if (!uploadResponse || !uploadResponse.output) {
    return <div className="main-container">No data available. Please upload a file first.</div>;
  }

  const suppliers = [...new Set(uploadResponse.output.map(item => item.supplier))];

  const handleSupplierClick = (supplier) => {
    setSelectedSupplier(supplier);
  };

  const selectedSupplierData = uploadResponse.output.find(item => item.supplier === selectedSupplier);

  const getScoreColor = (score, type) => {
    if (type === 'risk') {
      if (score <= 3) return '#12D18E'; // Green for low risk
      if (score <= 7) return '#FFDB7F'; // Yellow for medium risk
      return '#FB8D8D'; // Red for high risk
    } else {
      if (score >= 7) return '#12D18E'; // Green for high score
      if (score >= 4) return '#FFDB7F'; // Yellow for medium score
      return '#FB8D8D'; // Red for low score
    }
  };

  return (
    <div className="main-container">
      <div className="supplier-list">
        <h2>Suppliers</h2>
        <ul>
          {suppliers.map((supplier, index) => (
            <li 
              key={index} 
              onClick={() => handleSupplierClick(supplier)}
              className={selectedSupplier === supplier ? 'selected' : ''}
            >
              {supplier}
            </li>
          ))}
        </ul>
      </div>
      <div className="supplier-details">
        {selectedSupplierData ? (
          <div className="details-card">
            <h2>{selectedSupplierData.supplier}</h2>
            <p><strong>Item:</strong> {selectedSupplierData.item}</p>
            <p><strong>Description:</strong> {selectedSupplierData.description}</p>
            <div className="risk-scores">
              <div className="score">
                <span>Activity</span>
                <div 
                  className="score-bar" 
                  style={{
                    width: `${selectedSupplierData.activity * 10}%`,
                    backgroundColor: getScoreColor(selectedSupplierData.activity, 'activity')
                  }}
                ></div>
                <span>{selectedSupplierData.activity}</span>
              </div>
              <div className="score">
                <span>Confidence</span>
                <div 
                  className="score-bar" 
                  style={{
                    width: `${selectedSupplierData.confidence * 10}%`,
                    backgroundColor: getScoreColor(selectedSupplierData.confidence, 'confidence')
                  }}
                ></div>
                <span>{selectedSupplierData.confidence}</span>
              </div>
              <div className="score">
                <span>Risk</span>
                <div 
                  className="score-bar" 
                  style={{
                    width: `${selectedSupplierData.risk * 10}%`,
                    backgroundColor: getScoreColor(selectedSupplierData.risk, 'risk')
                  }}
                ></div>
                <span>{selectedSupplierData.risk}</span>
              </div>
            </div>
            <p><strong>Explanation:</strong> {selectedSupplierData.explanation}</p>
            {selectedSupplierData.alt_suppliers && selectedSupplierData.alt_suppliers.length > 0 && (
              <div className="alt-suppliers">
                <h3>Alternative Suppliers</h3>
                <div className="alt-suppliers-grid">
                  {selectedSupplierData.alt_suppliers.map((supplier, index) => (
                    <div key={index} className="alt-supplier-box">{supplier}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <p>Select a supplier to view details</p>
        )}
      </div>
    </div>
  );
}

export default Main;