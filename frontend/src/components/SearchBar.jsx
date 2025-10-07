import React, {useState, useMemo, useEffect} from 'react'
import axios from 'axios'

// read Vite env var (Vite inlines VITE_ variables at build time)
let API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
// normalize (remove trailing slash)
if (API.endsWith('/')) API = API.slice(0, -1)

// Small local fallback mapping used if the backend catalog cannot be reached.
const LOCAL_MODELS_BY_MAKE = {
  'Honda': ['Civic', 'Accord', 'CR-V'],
  'Toyota': ['Corolla', 'Camry', 'RAV4'],
  'Ford': ['F-150', 'Focus', 'Explorer'],
  'BMW': ['3 Series', '5 Series', 'X3'],
  'Hyundai': ['Elantra', 'Santa Fe', 'Tucson'],
  'Volkswagen': ['Golf', 'Passat', 'Tiguan']
}

const DEFAULT_MAKES = Object.keys(LOCAL_MODELS_BY_MAKE).sort()

export default function SearchBar({ onResult }){
  const now = new Date().getFullYear()
  const years = useMemo(()=>{
    const arr = []
    for(let y=1990; y<=now; y++) arr.push(y)
    return arr.reverse()
  },[])

  const [make,setMake] = useState(DEFAULT_MAKES[0] || '')
  const [model,setModel] = useState((LOCAL_MODELS_BY_MAKE[DEFAULT_MAKES[0]]||[])[0] || '')
  const [modelsByMake, setModelsByMake] = useState(LOCAL_MODELS_BY_MAKE)
  const [makers, setMakers] = useState(DEFAULT_MAKES)
  const [catalogLoaded, setCatalogLoaded] = useState(false)
  const [year,setYear] = useState(String(years[0]))
  const [loading,setLoading] = useState(false)
  const [result,setResult] = useState(null)

  const onMakeChange = (v) => {
    setMake(v)
    const m = modelsByMake[v] || []
    setModel((m||[])[0] || '')
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

  // Try to fetch the problem catalog from the backend and extract makers.
  useEffect(()=>{
    let mounted = true
    const fetchCatalog = async ()=>{
      try{
        const res = await axios.get(`${API}/problem-catalog`)
        if (!mounted) return
        const data = res.data || {}
        // Build a simple mapping: makers -> small model lists (fallback to local models if not available)
        const catMakers = (data.makers && Array.isArray(data.makers)) ? data.makers : Object.keys(LOCAL_MODELS_BY_MAKE)
        const mapping = {}
        for(const m of catMakers){
          // prefer local short lists if available, otherwise use a placeholder model list
          mapping[m] = LOCAL_MODELS_BY_MAKE[m] || ["Model A", "Model B", "Model C"]
        }
        setModelsByMake(mapping)
        setMakers(catMakers.slice().sort())
        setMake((catMakers[0]) || make)
        setModel((mapping[catMakers[0]]||[])[0] || model)
        setCatalogLoaded(true)
      }catch(_err){
        // leave the local mapping in place silently
        setCatalogLoaded(false)
      }
    }
    fetchCatalog()
    return ()=>{ mounted = false }
  }, [])

  return (
    <form onSubmit={submit} className="bg-white p-4 rounded shadow">
      <div className="flex gap-2 items-center">
        <select value={make} onChange={e=>onMakeChange(e.target.value)} className="border p-2 rounded w-48 bg-slate-900 text-slate-100">
          {makers.map(m=> <option key={m} value={m}>{m}</option>)}
        </select>

        <select value={model} onChange={e=>setModel(e.target.value)} className="border p-2 rounded flex-1 bg-slate-900 text-slate-100">
          {((modelsByMake[make]||[]).slice().sort()).map(m=> <option key={m} value={m}>{m}</option>)}
        </select>

        <select value={year} onChange={e=>setYear(e.target.value)} className="border p-2 rounded w-28">
          {years.map(y=> <option key={y} value={y}>{y}</option>)}
        </select>

  <button className="bg-gradient-to-r from-pink-600 to-indigo-500 text-white px-4 rounded shadow-lg" disabled={loading}>{loading? '...' : 'Search'}</button>
      </div>
  {/* Result is shown in the separate ResultCard component; no raw JSON blob here */}
    </form>
  )
}
