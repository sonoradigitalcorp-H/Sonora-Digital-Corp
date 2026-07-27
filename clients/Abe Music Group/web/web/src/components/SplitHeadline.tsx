"use client";

import { motion } from "framer-motion";

interface Part {
  text: string;
  from?: "left" | "right" | "up" | "down";
  className?: string;
}

const DIR_MAP = {
  left: { x: -60, y: 0 },
  right: { x: 60, y: 0 },
  up: { x: 0, y: 40 },
  down: { x: 0, y: -40 },
};

export default function SplitHeadline({ parts, className = "" }: { parts: Part[]; className?: string }) {
  return (
    <h1 className={`font-display ${className}`}>
      {parts.map((part, i) => {
        const dir = DIR_MAP[part.from || "up"];
        return (
          <motion.span
            key={i}
            initial={{ opacity: 0, x: dir.x, y: dir.y }}
            animate={{ opacity: 1, x: 0, y: 0 }}
            transition={{ duration: 0.6, delay: i * 0.15, ease: "easeOut" }}
            className={`inline-block mr-[0.3em] ${part.className || ""}`}
          >
            {part.text}
          </motion.span>
        );
      })}
    </h1>
  );
}
