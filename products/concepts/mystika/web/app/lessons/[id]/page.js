'use client'
import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import { api } from '@/lib/api'
import { useAuth } from '@/lib/auth'

export default function LessonDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const router = useRouter()
  const [lesson, setLesson] = useState(null)
  const [access, setAccess] = useState(null)
  const [streamUrl, setStreamUrl] = useState(null)
  const [loading, setLoading] = useState(true)
  const [consumed, setConsumed] = useState(false)

  useEffect(() => {
    api.getLesson(id).then((d) => {
      setLesson(d.lesson)
      setAccess(d.access)
      setLoading(false)
    })
  }, [id])

  async function handleBuy(gateway = 'stripe') {
    try {
      const data = await api.checkoutLesson({ lesson_id: parseInt(id), gateway })
      window.open(data.checkout_url, '_blank')
    } catch (err) {
      alert(err.message)
    }
  }

  async function handleWatch() {
    try {
      const data = await api.getStreamToken(id)
      setStreamUrl(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000'}${data.stream_url}`)
    } catch (err) {
      if (err.message.includes('consumed')) {
        setConsumed(true)
      } else {
        alert(err.message)
      }
    }
  }

  async function handleRetain() {
    try {
      const data = await api.retainLesson({ lesson_id: parseInt(id), gateway: 'stripe' })
      window.open(data.checkout_url, '_blank')
    } catch (err) {
      alert(err.message)
    }
  }

  function handleVideoEnded() {
    api.reportViewed({ lesson_id: parseInt(id), progress: { watched_seconds: 0, is_completed: true } })
    setConsumed(true)
    setStreamUrl(null)
  }

  if (loading) {
    return (
      <div className="min-h-screen stars-bg">
        <Navbar />
        <div className="pt-32 text-center">
          <div className="text-gold font-display text-2xl animate-glow">Cargando...</div>
        </div>
      </div>
    )
  }

  if (!lesson) {
    return (
      <div className="min-h-screen stars-bg"><Navbar />
        <div className="pt-32 text-center font-serif text-white/50">Ritual no encontrado</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen stars-bg">
      <Navbar />
      <div className="pt-24 pb-20">
        <div className="max-w-4xl mx-auto px-6">

          {streamUrl ? (
            <div className="mb-8">
              <video controls autoPlay className="w-full rounded-lg shadow-2xl"
                onEnded={handleVideoEnded}
                controlsList="nodownload noremoteplayback"
                disablePictureInPicture>
                <source src={streamUrl} type="video/mp4" />
              </video>
              <p className="font-sans text-xs text-white/30 text-center mt-2">
                Este ritual es solo para ti. No compartas este momento.
              </p>
            </div>
          ) : (
            <div className="aspect-video rounded-lg bg-gradient-to-br from-purple-shadow via-black to-black mb-8 flex items-center justify-center border border-gold/20">
              <div className="text-center">
                <span className="text-6xl block mb-4">☽</span>
                <p className="font-serif text-white/40">
                  {access?.has_access ? 'Listo para ver' : 'Compra o suscríbete para acceder'}
                </p>
              </div>
            </div>
          )}

          <div className="flex items-center gap-3 mb-4">
            <span className="font-sans text-xs uppercase bg-gold/20 text-gold px-3 py-1 rounded">{lesson.instrument}</span>
            <span className="font-sans text-xs uppercase text-white/30">{lesson.difficulty}</span>
          </div>

          <h1 className="font-display text-4xl text-gold mb-4">{lesson.title}</h1>
          <p className="font-serif text-lg text-white/60 mb-8 leading-relaxed">{lesson.description}</p>

          {consumed ? (
            <div className="card-mystika border-gold/40">
              <div className="text-center py-4">
                <span className="text-4xl block mb-3">🔥</span>
                <h3 className="font-heading text-xl text-gold mb-2">Ritual consumido</h3>
                <p className="font-serif text-white/50 mb-6">Tu vista única se ha completado. ¿Quieres conservar este momento?</p>
                <div className="flex gap-4 justify-center flex-wrap">
                  <button onClick={handleRetain}
                    className="btn-primary">Consagrar en mi altar — $7.49</button>
                  <button onClick={() => handleBuy('stripe')}
                    className="btn-secondary">Descargar talismán — $14.99</button>
                </div>
              </div>
            </div>
          ) : access?.has_access && !streamUrl ? (
            <button onClick={handleWatch}
              className="btn-primary text-lg px-12 py-4">
              Ver ritual
            </button>
          ) : !user ? (
            <div className="flex gap-4">
              <button onClick={() => router.push('/login')}
                className="btn-primary">Inicia sesión para comprar</button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex gap-4 flex-wrap">
                <button onClick={() => handleBuy('stripe')}
                  className="btn-primary">Comprar ${lesson.price_usd}</button>
                <button onClick={() => handleBuy('mercadopago')}
                  className="btn-secondary">Pagar con Mercado Pago</button>
              </div>
              <p className="font-sans text-xs text-white/30">
                Al comprar obtienes 1 vista. Después puedes retener o descargar.
                Los suscriptores Mysteria tienen descuento en retención. Los suscriptores Ritual tienen retención incluida.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
