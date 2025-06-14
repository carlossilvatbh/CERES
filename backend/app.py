from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "message": "CERES Backend API",
        "version": "1.0.0",
        "description": "Customer Enrollment and Risk Evaluation System",
        "status": "running"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "CERES Backend",
        "timestamp": "2025-06-14T07:00:00Z"
    })

@app.route('/api/v1/customers')
def customers():
    return jsonify({
        "customers": [],
        "total": 0,
        "message": "Customer endpoint - Django integration pending"
    })

@app.route('/api/v1/screening')
def screening():
    return jsonify({
        "screening_sources": [
            {"name": "OFAC", "status": "active"},
            {"name": "UN Consolidated List", "status": "active"},
            {"name": "EU Financial Sanctions", "status": "active"},
            {"name": "OpenSanctions", "status": "active"}
        ],
        "message": "Screening endpoint - Django integration pending"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))

