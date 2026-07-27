"use client";

interface ServiceCardProps {
  icon: string;
  title: string;
  description: string;
  features: string[];
  price?: string;
  gradient?: string;
}

export default function ServiceCard({
  icon,
  title,
  description,
  features,
  price,
  gradient = "linear-gradient(135deg, rgba(139,92,246,0.05), rgba(59,130,246,0.05))",
}: ServiceCardProps) {
  return (
    <div
      className="card"
      style={{
        background: "rgba(255,255,255,0.03)",
        backdropFilter: "blur(24px)",
        border: "1px solid rgba(255,255,255,0.06)",
        borderRadius: "20px",
        padding: "2rem",
        transition: "all 0.5s cubic-bezier(.25,.46,.45,.94)",
        position: "relative",
        overflow: "hidden",
        cursor: "pointer",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-6px)";
        e.currentTarget.style.borderColor = "rgba(139,92,246,0.3)";
        e.currentTarget.style.background = "rgba(255,255,255,0.06)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.borderColor = "rgba(255,255,255,0.06)";
        e.currentTarget.style.background = "rgba(255,255,255,0.03)";
      }}
    >
      <div style={{ fontSize: "2.2rem", marginBottom: "1.2rem" }}>{icon}</div>
      <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "0.6rem", letterSpacing: "-0.01em", fontFamily: "'Outfit', sans-serif" }}>
        {title}
      </h3>
      <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "0.9rem", lineHeight: 1.7, fontWeight: 300 }}>
        {description}
      </p>
      {price && (
        <div
          className="gradient-text"
          style={{ marginTop: "1rem", fontSize: "1.8rem", fontWeight: 300 }}
        >
          {price}
        </div>
      )}
      <ul style={{ marginTop: "1.2rem", listStyle: "none", padding: 0 }}>
        {features.map((f, i) => (
          <li
            key={i}
            style={{
              padding: "0.4rem 0",
              fontSize: "0.875rem",
              color: "rgba(255,255,255,0.45)",
              fontWeight: 300,
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <span style={{ color: "#34d399", fontWeight: 700 }}>✓</span>
            {f}
          </li>
        ))}
      </ul>
    </div>
  );
}
