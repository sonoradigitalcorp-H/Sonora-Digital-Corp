'use client'
import Navbar from '@/components/Navbar'

export default function About() {
  return (
    <div className="min-h-screen stars-bg">
      <Navbar />
      <div className="pt-24 pb-20">
        <div className="max-w-3xl mx-auto px-6">
          <div className="text-center mb-12">
            <div className="w-24 h-24 mx-auto mb-6 rounded-full border-2 border-gold flex items-center justify-center">
              <span className="text-4xl">🌙</span>
            </div>
            <h1 className="font-display text-4xl text-gold mb-2">Lilith Mystika</h1>
            <p className="font-heading text-xl text-white/60 italic">&ldquo;Que el ritmo te guíe&rdquo;</p>
          </div>

          <div className="card-mystika p-8 mb-8">
            <p className="font-serif text-lg text-white/70 leading-relaxed mb-6">
              Antes de Mystika, era música. Años de estudio, presentaciones en vivo,
              la energía de la multitud y la intimidad del estudio. Pero algo faltaba.
            </p>
            <p className="font-serif text-lg text-white/70 leading-relaxed mb-6">
              Mystika nació de la idea de que la música no debería ser solo técnica.
              Es conexión. Es energía. Es un ritual entre el alma y el sonido.
            </p>
            <p className="font-serif text-lg text-white/70 leading-relaxed">
              Aquí no solo aprenderás a tocar un instrumento. Aprenderás a sentir la música
              en cada fibra de tu ser. Y cuando la línea entre la enseñanza y el deseo
              comience a desvanecerse... ahí es donde realmente comienza la magia.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-4 text-center">
            <div className="card-mystika">
              <div className="text-3xl mb-2">🎵</div>
              <h3 className="font-heading text-gold">Música</h3>
              <p className="font-serif text-sm text-white/50">Todos los instrumentos y producción</p>
            </div>
            <div className="card-mystika">
              <div className="text-3xl mb-2">🔮</div>
              <h3 className="font-heading text-gold">Magia</h3>
              <p className="font-serif text-sm text-white/50">La energía que transforma notas en emociones</p>
            </div>
            <div className="card-mystika">
              <div className="text-3xl mb-2">🌙</div>
              <h3 className="font-heading text-gold">Misterio</h3>
              <p className="font-serif text-sm text-white/50">Lo que no se dice es más poderoso</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
