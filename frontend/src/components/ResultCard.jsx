import React from 'react'

export default function ResultCard({ data }){
  if (!data) return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold">Results</h2>
      <div className="mt-2 text-sm text-gray-700">Search a vehicle to see predictions.</div>
    </div>
  )

  if (data.error) return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold text-red-600">Error</h2>
      <pre className="mt-2 text-sm text-gray-700">{JSON.stringify(data, null, 2)}</pre>
    </div>
  )

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold">Prediction</h2>
      <div className="mt-3 grid grid-cols-2 gap-4">
        <div>
          <div className="text-sm text-gray-500">Predicted issue</div>
          <div className="text-lg font-medium">{data.predicted_issue}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Likelihood</div>
          <div className="text-lg font-medium">{(data.likelihood*100).toFixed(0)}%</div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Estimated cost</div>
          <div className="text-lg font-medium">${data.estimated_cost.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Range (months)</div>
          <div className="text-lg font-medium">{data.range_months}</div>
        </div>
      </div>
    </div>
  )
}
