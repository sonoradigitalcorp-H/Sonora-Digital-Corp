interface Props {
  label: string
  value: string | number
  sub?: string
}

export default function StatRow({ label, value, sub }: Props) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-[#111] last:border-0 text-sm">
      <span className="text-[#ccc]">{label}</span>
      <div className="text-right">
        <span className="font-bold text-gold">{value}</span>
        {sub && <div className="text-xs text-[#888]">{sub}</div>}
      </div>
    </div>
  )
}
