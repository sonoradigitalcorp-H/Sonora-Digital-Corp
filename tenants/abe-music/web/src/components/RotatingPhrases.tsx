"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function RotatingPhrases({ phrases, interval = 3000 }: { phrases: string[]; interval?: number }) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setIndex((i) => (i + 1) % phrases.length), interval);
    return () => clearInterval(timer);
  }, [phrases.length, interval]);

  return (
    <span className="relative inline-block min-h-[1.5em]">
      <AnimatePresence mode="wait">
        <motion.span
          key={index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.4 }}
          className="absolute left-0 whitespace-nowrap"
        >
          {phrases[index]}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}
