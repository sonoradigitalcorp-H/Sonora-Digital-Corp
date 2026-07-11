"use client";

import { motion } from "framer-motion";

export default function Reveal({
  children, dir = "up", delay = 0, className = "",
}: {
  children: React.ReactNode; dir?: "up" | "left" | "right"; delay?: number; className?: string;
}) {
  const dirMap = { up: { y: 30 }, left: { x: -30 }, right: { x: 30 } };
  return (
    <motion.div
      initial={{ opacity: 0, ...dirMap[dir] }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.6, delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
