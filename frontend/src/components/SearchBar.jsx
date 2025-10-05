import React, {useState} from 'react'
import axios from 'axios'

export default function SearchBar(){
  const [make,setMake] = useState('')
  const [model,setModel] = useState('')
  const [year,setYear] = useState('')
  const [loading,setLoading] = useState(false)
  const [result,setResult] = useState(null)

  const submit = async (e)=>{
    e.preventDefault()
    setLoading(true)
    try{
      const res = await axios.post('http://localhost:8000/predict', null, { params: { make, model_name: model, year: Number(year), mileage: 0 } })
      setResult(res.data)
    }catch(err){
      setResult({ error: err.message })
    }finally{ setLoading(false) }
  }

  return (
    <form onSubmit={submit} className="bg-white p-4 rounded shadow">
      <div className="flex gap-2">
        <input value={make} onChange={e=>setMake(e.target.value)} placeholder="Make" className="border p-2 rounded flex-1" />
        <input value={model} onChange={e=>setModel(e.target.value)} placeholder="Model" className="border p-2 rounded flex-1" />
        <input value={year} onChange={e=>setYear(e.target.value)} placeholder="Year" className="border p-2 rounded w-24" />
        <button className="bg-blue-600 text-white px-4 rounded" disabled={loading}>{loading? '...' : 'Search'}</button>
      </div>
      {result && <pre className="mt-3 text-sm">{JSON.stringify(result,null,2)}</pre>}
    </form>
  )
}
