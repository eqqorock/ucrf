import React, { useState } from 'react'
import SearchBar from './components/SearchBar'
import ResultCard from './components/ResultCard'

export default function App(){
  const [result, setResult] = useState(null)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">UCRF</h1>
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
