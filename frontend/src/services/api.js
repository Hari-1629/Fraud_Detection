import axios from 'axios';

const API_BASE = '/api';

export const api = {
  // 1. Upload files
  async uploadFiles(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    const response = await axios.post(`${API_BASE}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // 2. Get list of documents
  async getDocuments() {
    const response = await axios.get(`${API_BASE}/documents`);
    return response.data;
  },

  // 3. Get document details (Extracted data + Clauses + Risk Analysis)
  async getDocumentDetails(docId) {
    const response = await axios.get(`${API_BASE}/documents/${docId}`);
    return response.data;
  },

  // 4. Financial Calculations & Amortization
  async getCalculations(docId) {
    const response = await axios.get(`${API_BASE}/calculate/${docId}`);
    return response.data;
  },

  // 5. Clauses
  async getClauses(docId) {
    const response = await axios.get(`${API_BASE}/clauses/${docId}`);
    return response.data;
  },

  // 6. Compare Multiple Loans
  async compareLoans(docIds = []) {
    const response = await axios.post(`${API_BASE}/compare`, { doc_ids: docIds });
    return response.data;
  },

  // 7. RAG Chat Assistant
  async sendChatMessage(query, docIds = null) {
    const response = await axios.post(`${API_BASE}/chat`, { query, doc_ids: docIds });
    return response.data;
  },

  // 8. Load Pre-built Sample Docs
  async loadSampleDocs() {
    const response = await axios.post(`${API_BASE}/load-samples`);
    return response.data;
  },

  // 9. PDF Report URL
  getReportPdfUrl(docId) {
    return `${API_BASE}/report/${docId}/pdf`;
  }
};
