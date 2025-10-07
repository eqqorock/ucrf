import React, {useState, useMemo} from 'react'
import axios from 'axios'

// read Vite env var (Vite inlines VITE_ variables at build time)
let API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
// normalize (remove trailing slash)
if (API.endsWith('/')) API = API.slice(0, -1)

const DEFAULT_MAKES = ['Nissan','Toyota','Ford','Honda','Chevrolet']
const MODELS_BY_MAKE = {
  Nissan: ['Pathfinder','Xterra','Altima','Rogue'],
  Toyota: ['Camry','Corolla','RAV4','Prius'],
  Ford: ['F-150','Escape','Focus','Explorer'],
  Honda: ['Civic','Accord','CR-V','Pilot'],
  Chevrolet: ['Silverado','Malibu','Equinox','Impala']
}

export default function SearchBar({ onResult }){
  const now = new Date().getFullYear()
  const years = useMemo(()=>{
    const arr = []
    for(let y=1990; y<=now; y++) arr.push(y)
    return arr.reverse()
  },[])

  const [make,setMake] = useState(DEFAULT_MAKES[0])
  const [model,setModel] = useState(MODELS_BY_MAKE[DEFAULT_MAKES[0]][0])
  const [year,setYear] = useState(String(years[0]))
  const [loading,setLoading] = useState(false)
  const [result,setResult] = useState(null)

  const onMakeChange = (v) => {
    setMake(v)
    const m = MODELS_BY_MAKE[v] || []
    setModel(m[0] || '')
  }

  const submit = async (e)=>{
    e.preventDefault()
    setLoading(true)
    try{
      const res = await axios.post(`${API}/predict`, null, { params: { make, model_name: model, year: Number(year), mileage: 0 } })
      setResult(res.data)
      if (onResult) onResult(res.data)
    }catch(err){
      const payload = { error: err.message || 'Network Error' }
      setResult(payload)
      if (onResult) onResult(payload)
    }finally{ setLoading(false) }
  }

  return (
    <form onSubmit={submit} className="bg-white p-4 rounded shadow">
      <div className="flex gap-2 items-center">
        <select value={make} onChange={e=>onMakeChange(e.target.value)} className="border p-2 rounded w-48">
          {DEFAULT_MAKES.map(m=> <option key={m} value={m}>{m}</option>)}
        </select>

        <select value={model} onChange={e=>setModel(e.target.value)} className="border p-2 rounded flex-1">
          {(MODELS_BY_MAKE[make]||[]).map(m=> <option key={m} value={m}>{m}</option>)}
        </select>

        <select value={year} onChange={e=>setYear(e.target.value)} className="border p-2 rounded w-28">
          {years.map(y=> <option key={y} value={y}>{y}</option>)}
        </select>

        <button className="bg-blue-600 text-white px-4 rounded" disabled={loading}>{loading? '...' : 'Search'}</button>
      </div>
      {result && <pre className="mt-3 text-sm">{JSON.stringify(result,null,2)}</pre>}
    </form>
  )
}
