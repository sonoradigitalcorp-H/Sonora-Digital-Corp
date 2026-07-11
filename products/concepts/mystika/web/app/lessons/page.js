'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import { api } from '@/lib/api'

export default function Catalog() {
  const [lessons, setLessons] = useState([])
  const [instruments, setInstruments] = useState([])
  const [filter, setFilter] = useState('')

  useEffect(() => {
    api.getLessons().then((d) => setLessons(d.lessons))
    api.getInstruments().then(setInstruments)
  }, [])

  const filtered = filter
    ? lessons.filter((l) => l.instrument === filter)
    : lessons

  return (
    <div className="min-h-screen stars-bg">
      <Navbar />
      <div className="pt-24 pb-20">
        <div className="max-w-7xl mx-auto px-6">
          <h1 className="font-display text-4xl text-gold mb-2">Rituales</h1>
          <p className="font-serif text-white/50 mb-8 text-lg">Todas las lecciones disponibles</p>

          <div className="flex gap-2 flex-wrap mb-10">
            <button onClick={() => setFilter('')}
              className={`font-sans text-xs uppercase tracking-wider px-4 py-2 rounded-full border transition-all ${!filter ? 'bg-gold text-black border-gold' : 'border-white/20 text-white/60 hover:border-gold/40'}`}>
              Todas
            </button>
            {instruments.map((i) => (
              <button key={i.instrument} onClick={() => setFilter(i.instrument)}
                className={`font-sans text-xs uppercase tracking-wider px-4 py-2 rounded-full border transition-all ${filter === i.instrument ? 'bg-gold text-black border-gold' : 'border-white/20 text-white/60 hover:border-gold/40'}`}>
                {i.instrument} ({i.count})
              </button>
            ))}
          </div>

          {filtered.length === 0 ? (
            <div className="text-center py-20">
              <div className="text-6xl mb-4 opacity-30">🎵</div>
              <p className="font-serif text-white/40 text-lg">Pronto habrá nuevos rituales</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filtered.map((lesson) => (
                <Link key={lesson.id} href={`/lessons/${lesson.id}`}
                  className="card-mystika group cursor-pointer">
                  <div className="aspect-video rounded bg-gradient-to-br from-purple-shadow to-black mb-4 flex items-center justify-center border border-gold/10 group-hover:border-gold/30 transition-all">
                    <span className="text-4xl opacity-40 group-hover:opacity-60 transition-opacity">▶</span>
                  </div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-sans text-xs uppercase bg-gold/20 text-gold px-2 py-0.5 rounded">{lesson.instrument}</span>
                    <span className="font-sans text-xs uppercase text-white/30">{lesson.difficulty}</span>
                  </div>
                  <h3 className="font-heading text-lg text-white group-hover:text-gold transition-colors">{lesson.title}</h3>
                  <p className="font-serif text-sm text-white/50 mt-1 line-clamp-2">{lesson.description}</p>
                  <div className="mt-4 flex items-center justify-between">
                    <span className="font-display text-gold">${lesson.price_usd}</span>
                    {lesson.video_duration_seconds && (
                      <span className="font-sans text-xs text-white/30">{Math.floor(lesson.video_duration_seconds / 60)} min</span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
