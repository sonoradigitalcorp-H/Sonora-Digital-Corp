import { Telegraf, Markup, Context } from 'telegraf'
import axios from 'axios'

const BOT_TOKEN = process.env.ABE_MUSIC_BOT_TOKEN!
const API_URL = process.env.HERMES_API_URL || 'http://hermes-api:8000'
const ABRAHAM_CHAT_ID = process.env.ABRAHAM_CHAT_ID

if (!BOT_TOKEN) throw new Error('ABE_MUSIC_BOT_TOKEN requerido')

const bot = new Telegraf(BOT_TOKEN)
const api = axios.create({ baseURL: API_URL, timeout: 10000 })

// ── Helpers ──────────────────────────────────────────────────────────

async function getFanData(chatId: number) {
  try {
    const res = await api.get(`/hub/fans/${chatId}`)
    return res.data
  } catch {
    return null
  }
}

async function earnReso(chatId: number, concepto: string, referencia_id?: string) {
  try {
    await api.post('/hub/tokens/earn', { telegram_chat_id: chatId, concepto, referencia_id })
  } catch (e) {
    console.error('earnReso error:', e)
  }
}

async function notifyAbraham(mensaje: string) {
  if (!ABRAHAM_CHAT_ID) return
  try {
    await bot.telegram.sendMessage(ABRAHAM_CHAT_ID, `🎸 *Abe Music Hub*\n\n${mensaje}`, { parse_mode: 'Markdown' })
  } catch (e) {
    console.error('notifyAbraham error:', e)
  }
}

// ── /start ───────────────────────────────────────────────────────────

bot.start(async (ctx) => {
  const { first_name, id } = ctx.from!
  const refParam = ctx.startPayload

  try {
    await api.post('/hub/fans/register', {
      telegram_chat_id: id,
      nombre: first_name,
      username: ctx.from!.username,
      source: refParam ? 'referral' : 'telegram',
      referido_codigo: refParam || null,
    })

    if (refParam) await earnReso(id, 'bienvenida')
  } catch (e) {
    console.error('register error:', e)
  }

  await ctx.replyWithPhoto(
    { url: 'https://abemusicshub.com/assets/hub-banner.jpg' },
    {
      caption:
        `🎵 *Bienvenido al Abe Music Hub, ${first_name}!*\n\n` +
        `El hogar del músico sonorense.\n\n` +
        `🎸 Salas de ensayo • Estudio • Clases\n` +
        `🥁 Baquetas artesanales • Merch • VR\n` +
        `🎤 Shows • Eventos • Cursos online\n\n` +
        `Elige una opción:`,
      parse_mode: 'Markdown',
      ...Markup.inlineKeyboard([
        [Markup.button.callback('🎵 Servicios', 'servicios'), Markup.button.callback('📅 Reservar', 'reservar')],
        [Markup.button.callback('🪙 Mis $RESO', 'mis_reso'), Markup.button.callback('🏆 Ranking', 'ranking')],
        [Markup.button.callback('🎁 Merch', 'merch'), Markup.button.callback('🎟 Eventos', 'eventos')],
      ]),
    }
  )
})

// ── Servicios ─────────────────────────────────────────────────────────

bot.action('servicios', async (ctx) => {
  await ctx.answerCbQuery()
  try {
    const res = await api.get('/hub/services')
    const servicios = res.data.slice(0, 8)
    const lista = servicios
      .map((s: any) => `• *${s.nombre}* — $${s.precio_mxn} MXN`)
      .join('\n')
    await ctx.reply(
      `🎵 *Servicios disponibles:*\n\n${lista}\n\n_Escríbeme el nombre del servicio para reservar._`,
      { parse_mode: 'Markdown' }
    )
  } catch {
    await ctx.reply('⚠️ No pude cargar los servicios. Intenta de nuevo.')
  }
})

// ── Reservar (flujo multi-paso) ───────────────────────────────────────

const reservaState = new Map<number, Partial<{
  serviceId: string
  serviceName: string
  fecha: string
  hora: string
}>>()

bot.action('reservar', async (ctx) => {
  await ctx.answerCbQuery()
  try {
    const res = await api.get('/hub/services')
    const servicios = res.data.slice(0, 6)
    const buttons = servicios.map((s: any) =>
      [Markup.button.callback(s.nombre, `book_${s.id}`)]
    )
    await ctx.reply('¿Qué servicio quieres reservar?', Markup.inlineKeyboard(buttons))
  } catch {
    await ctx.reply('⚠️ Error al cargar servicios.')
  }
})

bot.action(/^book_(.+)$/, async (ctx) => {
  await ctx.answerCbQuery()
  const serviceId = ctx.match[1]
  const userId = ctx.from!.id

  reservaState.set(userId, { serviceId })

  await ctx.reply(
    '📅 ¿Para qué fecha? (Formato: DD/MM/AAAA)\nEjemplo: 15/06/2026',
    Markup.forceReply()
  )
})

// ── Balance $RESO ─────────────────────────────────────────────────────

bot.action('mis_reso', async (ctx) => {
  await ctx.answerCbQuery()
  const chatId = ctx.from!.id
  try {
    const res = await api.get(`/hub/tokens/balance/${chatId}`)
    const { balance, nivel, total_earned, total_burned } = res.data
    await ctx.reply(
      `🪙 *Tu saldo $RESO*\n\n` +
      `💰 Balance: *${balance} $RESO*\n` +
      `⭐ Nivel: *${nivel}*\n` +
      `📈 Total ganado: ${total_earned} $RESO\n` +
      `🔥 Total quemado: ${total_burned} $RESO\n\n` +
      `_Gana más $RESO creando contenido, asistiendo a eventos y completando cursos._`,
      { parse_mode: 'Markdown' }
    )
  } catch {
    await ctx.reply('⚠️ No pude cargar tu saldo. ¿Ya te registraste?')
  }
})

// ── Ranking ───────────────────────────────────────────────────────────

bot.action('ranking', async (ctx) => {
  await ctx.answerCbQuery()
  try {
    const res = await api.get('/hub/leaderboard/weekly')
    const top = res.data.slice(0, 10)
    const lista = top
      .map((f: any, i: number) => {
        const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`
        return `${medal} ${f.nombre} — ${f.balance} $RESO (${f.nivel})`
      })
      .join('\n')
    await ctx.reply(`🏆 *Top fans de esta semana:*\n\n${lista}`, { parse_mode: 'Markdown' })
  } catch {
    await ctx.reply('⚠️ Error al cargar el ranking.')
  }
})

// ── Merch ─────────────────────────────────────────────────────────────

bot.action('merch', async (ctx) => {
  await ctx.answerCbQuery()
  try {
    const res = await api.get('/hub/merch')
    const items = res.data.slice(0, 5)
    for (const item of items) {
      await ctx.reply(
        `🎁 *${item.nombre}*\n💵 $${item.precio_mxn} MXN\n${item.descripcion || ''}\n\n` +
        `Para comprar: wa.me/13238192000?text=Quiero+comprar+${encodeURIComponent(item.nombre)}`,
        { parse_mode: 'Markdown' }
      )
    }
  } catch {
    await ctx.reply('⚠️ Error al cargar el merch.')
  }
})

// ── Eventos ───────────────────────────────────────────────────────────

bot.action('eventos', async (ctx) => {
  await ctx.answerCbQuery()
  try {
    const res = await api.get('/hub/events')
    const eventos = res.data.slice(0, 5)
    if (!eventos.length) {
      await ctx.reply('🎟 No hay eventos próximos. ¡Síguenos para enterarte primero!')
      return
    }
    for (const ev of eventos) {
      const libre = ev.entrada_libre ? '🆓 Entrada libre' : `💵 $${ev.precio_entrada} MXN`
      await ctx.reply(
        `🎤 *${ev.nombre_evento}*\n` +
        `📅 ${ev.fecha_evento} ${ev.hora_inicio || ''}\n` +
        `📍 ${ev.lugar}\n` +
        `${libre}`,
        {
          parse_mode: 'Markdown',
          ...Markup.inlineKeyboard([[Markup.button.callback('✅ Me apunto', `join_${ev.id}`)]]),
        }
      )
    }
  } catch {
    await ctx.reply('⚠️ Error al cargar eventos.')
  }
})

bot.action(/^join_(.+)$/, async (ctx) => {
  await ctx.answerCbQuery('¡Registrando tu asistencia!')
  const eventId = ctx.match[1]
  const chatId = ctx.from!.id
  try {
    await api.post('/hub/events/join', { event_id: eventId, telegram_chat_id: chatId })
    await earnReso(chatId, 'live_virtual', eventId)
    await ctx.reply('✅ ¡Ya estás registrado! Ganarás 50 $RESO al asistir. 🎉')
  } catch {
    await ctx.reply('⚠️ Error al registrar. Intenta de nuevo.')
  }
})

// ── /referir ──────────────────────────────────────────────────────────

bot.command('referir', async (ctx) => {
  const chatId = ctx.from!.id
  const link = `https://t.me/${(await bot.telegram.getMe()).username}?start=${chatId}`
  await ctx.reply(
    `🔗 *Tu link de referido:*\n${link}\n\n` +
    `Gana *200 $RESO* por cada amigo que se suscriba. 💰`,
    { parse_mode: 'Markdown' }
  )
})

// ── Mensajes de texto (reserva o ayuda) ──────────────────────────────

bot.on('text', async (ctx) => {
  const userId = ctx.from!.id
  const state = reservaState.get(userId)

  if (state?.serviceId && !state.fecha) {
    const text = ctx.message.text.trim()
    const fechaRegex = /^\d{2}\/\d{2}\/\d{4}$/
    if (!fechaRegex.test(text)) {
      await ctx.reply('❌ Formato incorrecto. Usa DD/MM/AAAA — ejemplo: 15/06/2026')
      return
    }
    state.fecha = text
    reservaState.set(userId, state)
    await ctx.reply('⏰ ¿A qué hora? (Formato: HH:MM — ejemplo: 14:30)', Markup.forceReply())
    return
  }

  if (state?.fecha && !state.hora) {
    const hora = ctx.message.text.trim()
    if (!/^\d{2}:\d{2}$/.test(hora)) {
      await ctx.reply('❌ Formato incorrecto. Usa HH:MM — ejemplo: 14:30')
      return
    }

    try {
      const fan = await getFanData(userId)
      const [dia, mes, año] = state.fecha!.split('/')
      await api.post('/hub/bookings', {
        service_id: state.serviceId,
        telegram_chat_id: userId,
        nombre_cliente: ctx.from.first_name,
        fecha_reserva: `${año}-${mes}-${dia}`,
        hora_inicio: hora,
        hora_fin: `${parseInt(hora.split(':')[0]) + 1}:${hora.split(':')[1]}`,
      })

      reservaState.delete(userId)

      await ctx.reply(
        `✅ *¡Reserva confirmada!*\n\n` +
        `📅 Fecha: ${state.fecha}\n` +
        `⏰ Hora: ${hora}\n\n` +
        `Te contactaremos pronto para confirmar. 🎸`,
        { parse_mode: 'Markdown' }
      )

      await notifyAbraham(
        `Nueva reserva de *${ctx.from.first_name}* (@${ctx.from.username || 'sin usuario'})\n` +
        `📅 ${state.fecha} a las ${hora}`
      )
    } catch {
      await ctx.reply('⚠️ Error al crear la reserva. Intenta de nuevo o contáctanos directamente.')
      reservaState.delete(userId)
    }
    return
  }

  await ctx.reply(
    '🎵 ¿En qué puedo ayudarte?\n\nUsa los botones o escribe:\n• /referir — obtén tu link de referido\n\nO presiona /start para ver el menú principal.'
  )
})

// ── Launch ────────────────────────────────────────────────────────────

const isDev = process.env.NODE_ENV !== 'production'

if (isDev) {
  bot.launch({ dropPendingUpdates: true })
    .then(() => console.log('Abe Music Bot corriendo (polling)'))
    .catch(console.error)
} else {
  bot.launch({ dropPendingUpdates: true })
    .then(() => console.log('Abe Music Bot corriendo'))
    .catch(console.error)
}

process.once('SIGINT', () => bot.stop('SIGINT'))
process.once('SIGTERM', () => bot.stop('SIGTERM'))
