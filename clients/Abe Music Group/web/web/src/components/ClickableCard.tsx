"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

interface Props {
  icon: React.ReactNode;
  title: string;
  tagline: string;
  bullets: string[];
  cta: string;
  index: number;
}

export default function ClickableCard({ icon, title, tagline, bullets, cta, index }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.08 }}
      className="glass rounded-2xl overflow-hidden card-hover cursor-pointer"
      onClick={() => setOpen(!open)}
    >
      <div className="p-6">
        <div className="flex items-start gap-4">
          <div className="text-gold mt-1">{icon}</div>
          <div className="flex-1 min-w-0">
            <h3 className="font-display text-xl font-medium mb-1">{title}</h3>
            <p className="text-sm text-muted-foreground">{tagline}</p>
          </div>
          <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown className="w-5 h-5 text-gold mt-1" />
          </motion.div>
        </div>

        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <ul className="mt-4 space-y-2 border-t border-white/10 pt-4">
                {bullets.map((b, i) => (
                  <motion.li
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-start gap-2 text-sm text-foreground/80"
                  >
                    <span className="w-1 h-1 mt-2 rounded-full bg-gold shrink-0" />
                    {b}
                  </motion.li>
                ))}
              </ul>
              <div className="mt-4 text-sm text-gold font-medium">{cta} →</div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
