import React, { useState, useEffect } from 'react';
import { DollarSign, Percent, Calendar, FileText, AlertTriangle, ShieldCheck, Download, Edit2, Check, RefreshCw } from 'lucide-react';
import ClauseDrawer from './ClauseDrawer';
import { api } from '../services/api';

export default function Dashboard({ docDetail, selectedDocId, documents, onSelectDoc }) {
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    if (docDetail && docDetail.extracted_data) {
      setFormData(docDetail.extracted_data);
    }
  }, [docDetail]);

  if (!docDetail) {
    return (
      <div className="empty-state glass-card animate-fade-in" style={{ margin: '2rem 0' }}>
        <FileText size={48} color="#64748b" />
        <h3>No Document Selected</h3>
        <p>Please upload a document or select an existing document to view the decision support dashboard.</p>
      </div>
    );
  }

  const ext = formData;
  const risk = docDetail.risk_analysis || { risk_score: 5.0, risk_category: 'MEDIUM_RISK', recommendations: [] };

  const handleInputChange = (field, val) => {
    setFormData(prev => ({ ...prev, [field]: val }));
  };

  const riskBadgeClass = 
    risk.risk_category === 'HIGH_RISK' ? 'badge-high' :
    risk.risk_category === 'MEDIUM_RISK' ? 'badge-medium' : 'badge-low';

  return (
    <div className="dashboard-container animate-fade-in">
      {/* Top Document Header */}
      <div className="dash-header glass-card">
        <div className="dash-header-info">
          <div className="doc-select-dropdown">
            <label>Active Document:</label>
            <select
              id="dash-doc-select"
              value={selectedDocId || ''}
              onChange={(e) => onSelectDoc(e.target.value)}
              className="input-field"
              style={{ width: 'auto', display: 'inline-block', marginLeft: '0.5rem' }}
            >
              {documents.map(d => (
                <option key={d.id} value={d.id}>{d.filename}</option>
              ))}
            </select>
          </div>
          <h2 className="doc-title">{docDetail.filename}</h2>
          <div className="meta-pills">
            <span className="pill">Borrower: <strong>{ext.borrower_name || 'Rahul Sharma'}</strong></span>
            <span className="pill">Type: <strong>{ext.interest_type || 'Fixed'} Interest</strong></span>
            <span className="pill">Due Date: <strong>{ext.due_dates || '5th of month'}</strong></span>
          </div>
        </div>

        <div className="dash-header-actions">
          <a
            id="btn-download-pdf-report"
            href={api.getReportPdfUrl(selectedDocId)}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary"
          >
            <Download size={18} />
            <span>Export PDF Report</span>
          </a>
        </div>
      </div>

      {/* Main Grid: 4 Metric Cards */}
      <div className="grid-4" style={{ margin: '1.5rem 0' }}>
        <div className="metric-card glass-card">
          <div className="metric-icon bg-cyan">
            <DollarSign size={22} color="#38bdf8" />
          </div>
          <div className="metric-body">
            <span className="metric-label">Loan Principal</span>
            <h3 className="metric-value">₹ {floatVal(ext.loan_amount).toLocaleString('en-IN')}</h3>
            <span className="metric-sub">Sanctioned Amount</span>
          </div>
        </div>

        <div className="metric-card glass-card">
          <div className="metric-icon bg-blue">
            <Percent size={22} color="#6366f1" />
          </div>
          <div className="metric-body">
            <span className="metric-label">Interest Rate</span>
            <h3 className="metric-value">{floatVal(ext.interest_rate).toFixed(2)}% p.a.</h3>
            <span className="metric-sub">{ext.interest_type || 'Fixed'} Rate</span>
          </div>
        </div>

        <div className="metric-card glass-card">
          <div className="metric-icon bg-purple">
            <Calendar size={22} color="#a855f7" />
          </div>
          <div className="metric-body">
            <span className="metric-label">Loan Tenure</span>
            <h3 className="metric-value">{ext.tenure || 60} Months</h3>
            <span className="metric-sub">{(intVal(ext.tenure) / 12).toFixed(1)} Years</span>
          </div>
        </div>

        <div className="metric-card glass-card">
          <div className="metric-icon bg-emerald">
            <DollarSign size={22} color="#10b981" />
          </div>
          <div className="metric-body">
            <span className="metric-label">Monthly EMI</span>
            <h3 className="metric-value" style={{ color: '#10b981' }}>
              ₹ {floatVal(ext.emi).toLocaleString('en-IN')}
            </h3>
            <span className="metric-sub">Equated Instalment</span>
          </div>
        </div>
      </div>

      {/* Structured Extraction Table + Risk Assessment Panel */}
      <div className="grid-2" style={{ margin: '1.5rem 0' }}>
        {/* Left Column: Extraction Details */}
        <div className="glass-card">
          <div className="card-header">
            <h3>Financial Parameters (NLP Extracted)</h3>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setEditing(!editing)}
            >
              {editing ? <Check size={16} /> : <Edit2 size={16} />}
              <span>{editing ? 'Save' : 'Edit Values'}</span>
            </button>
          </div>

          <div className="data-table">
            <div className="data-row">
              <span className="row-label">Processing Fee</span>
              <span className="row-val">₹ {floatVal(ext.processing_fee).toLocaleString('en-IN')} ({floatVal(ext.processing_fee_pct).toFixed(2)}%)</span>
            </div>
            <div className="data-row">
              <span className="row-label">Total Interest Payable</span>
              <span className="row-val" style={{ color: '#f59e0b', fontWeight: 'bold' }}>
                ₹ {floatVal(ext.total_interest).toLocaleString('en-IN')}
              </span>
            </div>
            <div className="data-row">
              <span className="row-label">Total Repayment Amount</span>
              <span className="row-val" style={{ color: '#38bdf8', fontWeight: 'bold' }}>
                ₹ {floatVal(ext.total_repayment).toLocaleString('en-IN')}
              </span>
            </div>
            <div className="data-row">
              <span className="row-label">Foreclosure Charges</span>
              <span className="row-val">{ext.foreclosure_charges || '3% on principal balance'}</span>
            </div>
            <div className="data-row">
              <span className="row-label">Late Payment Penalties</span>
              <span className="row-val">{ext.late_payment_penalties || '2% per month penal interest'}</span>
            </div>
          </div>
        </div>

        {/* Right Column: AI Risk Support & Recommendations */}
        <div className="glass-card">
          <div className="card-header">
            <h3>AI Contract Risk Score</h3>
            <span className={`badge ${riskBadgeClass}`}>
              {risk.risk_category.replace('_', ' ')}
            </span>
          </div>

          <div className="risk-score-box">
            <div className="score-number-display">
              <span className="score-num">{risk.risk_score}</span>
              <span className="score-max">/ 10</span>
            </div>
            <div className="score-meter-bar">
              <div
                className="score-fill"
                style={{
                  width: `${(risk.risk_score / 10) * 100}%`,
                  background: risk.risk_score > 7 ? '#f43f5e' : risk.risk_score > 4 ? '#f59e0b' : '#10b981'
                }}
              />
            </div>
          </div>

          <div className="recommendations-box">
            <h4>Key Recommendations for Borrower:</h4>
            <ul>
              {risk.recommendations && risk.recommendations.map((rec, i) => (
                <li key={i}>
                  <ShieldCheck size={16} color="#38bdf8" />
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Classified Financial Clauses Section */}
      <ClauseDrawer clauses={docDetail.clauses || []} />
    </div>
  );
}

function floatVal(v) {
  const parsed = parseFloat(v);
  return isNaN(parsed) ? 0 : parsed;
}

function intVal(v) {
  const parsed = parseInt(v, 10);
  return isNaN(parsed) ? 0 : parsed;
}
