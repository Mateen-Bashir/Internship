import { useState } from 'react'
import './index.css'

function App() {
  const [formData, setFormData] = useState({
    Completion_Time: '',
    Feedback_Rating: '',
    Attendance: ''
  })

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/predict`, {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          Completion_Time: parseFloat(formData.Completion_Time),
          Feedback_Rating: parseFloat(formData.Feedback_Rating),
          Attendance: parseFloat(formData.Attendance)
        })
      })

      if (!response.ok) {
        throw new Error('Failed to fetch prediction')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <div className="glass-card">
        <header className="header">
          <h1>Intern AI Predictor</h1>
          <p>Discover future performance potential instantly</p>
        </header>

        <form onSubmit={handleSubmit} className="form-content">
          <div className="form-group">
            <label htmlFor="Completion_Time">Completion Time (Hrs)</label>
            <input
              type="number"
              step="0.01"
              id="Completion_Time"
              name="Completion_Time"
              placeholder="e.g. 4.5"
              value={formData.Completion_Time}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="Feedback_Rating">Feedback Rating (1-10)</label>
            <input
              type="number"
              step="0.01"
              id="Feedback_Rating"
              name="Feedback_Rating"
              placeholder="e.g. 8.5"
              value={formData.Feedback_Rating}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="Attendance">Attendance (%)</label>
            <input
              type="number"
              step="0.01"
              id="Attendance"
              name="Attendance"
              placeholder="e.g. 95.0"
              value={formData.Attendance}
              onChange={handleChange}
              required
            />
          </div>

          <button
            type="submit"
            className="submit-btn"
            disabled={loading}
          >
            {loading ? 'Predicting Matrix...' : 'Generate Prediction'}
          </button>
        </form>

        {error && (
          <div style={{ color: '#ff4d4d', marginTop: '1rem', textAlign: 'center' }}>
            Error: {error}
          </div>
        )}

        {result && (
          <div className="result-card">
            <h3>Predicted Performance Score</h3>
            <div className="score-display">
              {result.prediction.toFixed(2)}
            </div>
            <p style={{ fontSize: '0.8rem', opacity: 0.5, marginTop: '10px' }}>
              RF Reference: {result.rf_prediction_reference.toFixed(2)}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
