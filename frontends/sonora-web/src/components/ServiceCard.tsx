export default function ServiceCard({ service, index }: {
  service: { id: string; name: string; desc: string; icon: string; color: string };
  index: number;
}) {
  return (
    <a href={`/service/${service.id}`}
      className="group glass rounded-2xl p-6 hover:bg-white/[0.03] transition-all duration-300 block">
      <div className="text-3xl mb-3">{service.icon}</div>
      <h3 className="font-semibold mb-2" style={{ color: service.color }}>{service.name}</h3>
      <p className="text-sm text-gray-400 leading-relaxed">{service.desc}</p>
      <div className="mt-4 text-xs" style={{ color: service.color, opacity: 0 }}>
        <span className="group-hover:opacity-100 transition-opacity">Más información →</span>
      </div>
    </a>
  );
}
