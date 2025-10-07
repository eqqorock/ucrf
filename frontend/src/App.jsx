import React, { useState } from 'react'
import SearchBar from './components/SearchBar'
import ResultCard from './components/ResultCard'

export default function App(){
  const [result, setResult] = useState(null)

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-slate-900 to-gray-800 text-slate-100">
      <header className="bg-gradient-to-r from-indigo-700 via-purple-700 to-pink-600 shadow-lg">
        <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-extrabold tracking-tight">Used Car Reliability Forecaster</h1>
        </div>
      </header>
      <main className="max-w-4xl mx-auto p-6">
        <SearchBar onResult={setResult} />
        <div className="mt-6">
          <ResultCard data={result} />
        </div>
      </main>
    </div>
  )
}
