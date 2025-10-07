import React, {useState, useMemo} from 'react'
import axios from 'axios'

// read Vite env var (Vite inlines VITE_ variables at build time)
let API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
// normalize (remove trailing slash)
if (API.endsWith('/')) API = API.slice(0, -1)

// Dummy makers and models: 5 per region with 15 models each (toy data)
const MODELS_BY_MAKE = {
  // Japanese
  'Honda': ['Accord','Civic','CR-V','Element','Fit','HR-V','Insight','Jazz','N-One','Pilot','Prelude','Ridgeline','S2000','Stepwgn','Vezel'],
  'Mazda': ['3','6','CX-3','CX-30','CX-5','CX-9','MX-5','RX-7','RX-8','Biante','Atenza','Capella','Demio','MPV','Premacy'],
  'Nissan': ['300ZX','Altima','Armada','Cube','Frontier','Juke','Kicks','Leaf','Maxima','Murano','Pathfinder','Patrol','Rogue','Sentra','Xterra'],
  'Subaru': ['BRZ','Crosstrek','Forester','Impreza','Justy','Legacy','Levorg','Outback','Pleo','STI','Tribeca','WRX','Baja','Alcyone','R2'],
  'Toyota': ['86','Alphard','Aurion','Avalon','Camry','Corolla','Crown','Estima','FJ Cruiser','Hilux','Land Cruiser','Prius','RAV4','Sequoia','Yaris'],
  // Korean
  'Genesis': ['G70','G80','G90','GV60','GV70','GV80','XG','Coupé','Equus','KM240','Newport','Rexton','Rodeo','Stellar','Tivoli'],
  'Hyundai': ['Accent','Azera','Elantra','Encore','Equus','Genesis','Ioniq','Kona','Palisade','Santa Fe','Santa Cruz','Sonata','Staria','Tucson','Veloster'],
  'Kia': ['Cadenza','Carnival','Forte','K900','KX3','KX5','Link','Niro','Optima','Picanto','Quoris','Rio','Sedona','Sorento','Sportage'],
  'Daewoo': ['Lacetti','Korando','Matiz','Leganza','Nubira','Musso','Espero','Tico','Prince','Lanos','Veritas','Racer','Tornado','Kruse','Monza'],
  'SsangYong': ['Actyon','Chairman','Korando','Khan','Kyron','Musso','Rexton','Rodius','Tivoli','Turino','Korando Sports','Rexton W','Korando C','Actyon Sports','Korando Turismo'],
  // American
  'Ford': ['Bronco','Edge','Escape','Expedition','Explorer','F-150','F-250','Fiesta','Flex','Focus','Mustang','Ranger','Taurus','Transit','Thunderbird'],
  'Chevrolet': ['Avalanche','Bolt','Camaro','Caprice','Chevelle','Corvette','Cruze','Equinox','Impala','Malibu','Monte Carlo','Silverado','Sonic','Spark','Suburban'],
  'Dodge': ['Avenger','Challenger','Charger','Dakota','Daytona','Durango','Magnum','Neon','Nitro','Polara','Ram','Stratus','Viper','Journey','Caliber'],
  'Tesla': ['Model S','Model 3','Model X','Model Y','Roadster','Cybertruck','Semi','Roadster 2020','Tesla Two','E-Model','Alpha','Beta','Gamma','Delta','Omega'],
  'Cadillac': ['ATS','Brougham','CTS','DeVille','CT4','CT5','Eldorado','Escalade','Fleetwood','Seville','SRX','STS','XLR','XT4','XT5'],
  // German
  'BMW': ['1 Series','2 Series','3 Series','4 Series','5 Series','6 Series','7 Series','8 Series','i3','i8','M2','M3','M4','X1','X3'],
  'Mercedes-Benz': ['A-Class','B-Class','C-Class','CLA','CLS','E-Class','G-Class','GLA','GLC','GLE','S-Class','SL','SLC','Sprinter','Vito'],
  'Audi': ['A1','A3','A4','A5','A6','A7','A8','Q2','Q3','Q5','Q7','R8','RS3','RS5','TT'],
  'Porsche': ['911','Boxster','Cayenne','Cayman','Macan','Panamera','Taycan','924','944','968','928','356','914','718','Carrera GT'],
  'Volkswagen': ['Beetle','Golf','Jetta','Passat','Polo','Tiguan','Touareg','Arteon','Atlas','CC','Scirocco','Vanagon','K70','Karmann','Golf R']
}

const DEFAULT_MAKES = Object.keys(MODELS_BY_MAKE).sort()

export default function SearchBar({ onResult }){
  const now = new Date().getFullYear()
  const years = useMemo(()=>{
    const arr = []
    for(let y=1990; y<=now; y++) arr.push(y)
    return arr.reverse()
  },[])

  const [make,setMake] = useState(DEFAULT_MAKES[0])
  const [model,setModel] = useState((MODELS_BY_MAKE[DEFAULT_MAKES[0]]||[])[0])
  const [year,setYear] = useState(String(years[0]))
  const [loading,setLoading] = useState(false)
  const [result,setResult] = useState(null)

  const onMakeChange = (v) => {
    setMake(v)
    const m = MODELS_BY_MAKE[v] || []
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

  return (
    <form onSubmit={submit} className="bg-white p-4 rounded shadow">
      <div className="flex gap-2 items-center">
        <select value={make} onChange={e=>onMakeChange(e.target.value)} className="border p-2 rounded w-48 bg-slate-900 text-slate-100">
          {DEFAULT_MAKES.map(m=> <option key={m} value={m}>{m}</option>)}
        </select>

        <select value={model} onChange={e=>setModel(e.target.value)} className="border p-2 rounded flex-1 bg-slate-900 text-slate-100">
          {((MODELS_BY_MAKE[make]||[]).slice().sort()).map(m=> <option key={m} value={m}>{m}</option>)}
        </select>

        <select value={year} onChange={e=>setYear(e.target.value)} className="border p-2 rounded w-28">
          {years.map(y=> <option key={y} value={y}>{y}</option>)}
        </select>

  <button className="bg-gradient-to-r from-pink-600 to-indigo-500 text-white px-4 rounded shadow-lg" disabled={loading}>{loading? '...' : 'Search'}</button>
      </div>
      {result && <pre className="mt-3 text-sm">{JSON.stringify(result,null,2)}</pre>}
    </form>
  )
}
