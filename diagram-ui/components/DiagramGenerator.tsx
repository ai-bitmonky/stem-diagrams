'use client'

import { useState } from 'react'

interface DiagramResult {
  svg: string
  metadata: {
    complexity_score: number
    selected_strategy: string
    property_graph_nodes: number
    property_graph_edges: number
  }
}

export default function DiagramGenerator() {
  const [problemText, setProblemText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DiagramResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!problemText.trim()) {
      setError('Please enter a problem description')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ problem_text: problemText }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate diagram')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <label htmlFor="problem-text" className="block text-sm font-medium text-gray-700 mb-2">
          Physics Problem Description
        </label>
        <textarea
          id="problem-text"
          rows={6}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
          placeholder="Example: A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm. A battery charges the plates to a potential difference of 120 V..."
          value={problemText}
          onChange={(e) => setProblemText(e.target.value)}
          disabled={loading}
        />

        <button
          onClick={handleGenerate}
          disabled={loading || !problemText.trim()}
          className="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 ease-in-out transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating Diagram...
            </span>
          ) : (
            'Generate Diagram'
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-6">
          {/* Metadata */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Analysis Metadata</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Complexity Score</p>
                <p className="text-lg font-semibold text-indigo-600">
                  {result.metadata.complexity_score.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Strategy</p>
                <p className="text-lg font-semibold text-indigo-600">
                  {result.metadata.selected_strategy}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Graph Nodes</p>
                <p className="text-lg font-semibold text-indigo-600">
                  {result.metadata.property_graph_nodes}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Graph Edges</p>
                <p className="text-lg font-semibold text-indigo-600">
                  {result.metadata.property_graph_edges}
                </p>
              </div>
            </div>
          </div>

          {/* Diagram */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Generated Diagram</h2>
            <div
              className="border border-gray-200 rounded-lg p-4 bg-gray-50"
              dangerouslySetInnerHTML={{ __html: result.svg }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
