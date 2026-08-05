interface Props {
  label: string
  value: string | number
  gold?: boolean
  change?: string
  up?: boolean
}

export default function KPICard({ label, value, gold, change, up }: Props) {
  return (
    <div className="bg-dark2 border border-[#1a1a1a] rounded-2xl p-5">
      <div className="text-xs text-[#888] uppercase tracking-wider mb-2">{label}</div>
      <div className={`text-3xl font-black ${gold ? 'text-gold' : 'text-[#F0EDE8]'}`}>{value}</div>
      {change && (
        <div className={`text-xs mt-1 ${up ? 'text-green-400' : 'text-red-400'}`}>{change}</div>
      )}
    </div>
  )
}
