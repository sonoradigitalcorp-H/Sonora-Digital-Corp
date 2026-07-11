import Reveal from "./Reveal";

export default function SectionTitle({
  eyebrow, title, subtitle,
}: {
  eyebrow?: string; title: React.ReactNode; subtitle?: string;
}) {
  return (
    <Reveal>
      <div className="text-center mb-16">
        {eyebrow && <p className="text-xs uppercase tracking-[0.3em] text-gold mb-4">{eyebrow}</p>}
        <h2 className="font-display text-4xl md:text-5xl font-light leading-tight mb-6">{title}</h2>
        {subtitle && <p className="text-muted-foreground text-lg max-w-2xl mx-auto">{subtitle}</p>}
      </div>
    </Reveal>
  );
}
