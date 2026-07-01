import 'dotenv/config'
import { Telegraf, Markup } from 'telegraf'
import axios from 'axios'

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN
const API_URL = process.env.API_URL || 'http://localhost:4000'
const ADMIN_ID = parseInt(process.env.TELEGRAM_ADMIN_ID || '0')

if (!BOT_TOKEN) {
  console.error('TELEGRAM_BOT_TOKEN is required')
  process.exit(1)
}

const bot = new Telegraf(BOT_TOKEN)

// State for admin upload flow
const uploadState = new Map()
function getUpload(userId) { return uploadState.get(userId) || {} }
function setUpload(userId, data) { uploadState.set(userId, { ...getUpload(userId), ...data }) }
function clearUpload(userId) { uploadState.delete(userId) }

bot.start(async (ctx) => {
  const name = ctx.from.first_name || 'iniciado'
  await ctx.replyWithHTML(
    `🌙 <b>Bienvenido a Mystika, ${name}.</b>\n\n` +
    `Yo soy <b>Lilith</b>, y este es mi templo musical.\n` +
    `Aquí la música se siente, se vive, se convierte en ritual.\n\n` +
    `Usa los botones para explorar:`,
    Markup.inlineKeyboard([
      [Markup.button.callback('🎵 Catálogo de lecciones', 'catalogo')],
      [Markup.button.callback('🔮 Planes de suscripción', 'planes')],
      [Markup.button.callback('🌐 Abrir Mystika Web', 'web')],
      [Markup.button.url('✨ Ir a mystika.app', 'https://mystika.app')],
    ])
  )
})

bot.command('menu', async (ctx) => {
  await ctx.reply('¿Qué deseas hacer?', Markup.inlineKeyboard([
    [Markup.button.callback('🎵 Catálogo', 'catalogo')],
    [Markup.button.callback('🔮 Planes', 'planes')],
    [Markup.button.callback('👤 Mi cuenta', 'cuenta')],
  ]))
})

bot.command('catalogo', async (ctx) => {
  await showCatalog(ctx)
})

bot.command('suscripcion', async (ctx) => {
  await showPlans(ctx)
})

bot.command('mi_cuenta', async (ctx) => {
  await showAccount(ctx)
})

async function showCatalog(ctx) {
  try {
    const { data } = await axios.get(`${API_URL}/api/lessons`)
    const lessons = data.lessons || []
    if (lessons.length === 0) {
      return ctx.reply('🔮 Pronto habrá nuevos rituales. Vuelve pronto.')
    }
    let msg = '🎵 <b>Rituales disponibles:</b>\n\n'
    const buttons = []
    for (const lesson of lessons.slice(0, 10)) {
      msg += `<b>${lesson.title}</b> — $${lesson.price_usd}\n`
      msg += `  🥁 ${lesson.instrument} · ${lesson.difficulty || 'todos los niveles'}\n\n`
      buttons.push([Markup.button.callback(
        `🎵 ${lesson.title.substring(0, 30)}`,
        `lesson_${lesson.id}`
      )])
    }
    msg += 'Selecciona uno para ver detalles:'
    await ctx.replyWithHTML(msg, Markup.inlineKeyboard(buttons))
  } catch (err) {
    await ctx.reply('💫 Error al cargar el catálogo. Intenta de nuevo.')
  }
}

async function showPlans(ctx) {
  await ctx.replyWithHTML(
    '🔮 <b>Planes de Mystika:</b>\n\n' +
    '<b>🌙 Mysteria — $14.99/mes</b>\n' +
    '• Lecciones completas\n' +
    '• Fotos NSFW semanales\n' +
    '• Streaming grupal\n' +
    '• Chat con Lilith (20 msg/día)\n\n' +
    '<b>🔥 Ritual — $49.99/mes</b>\n' +
    '• Todo de Mysteria\n' +
    '• Videos NSFW exclusivos\n' +
    '• Fotos NSFW diarias\n' +
    '• Chat ilimitado\n' +
    '• Streaming 1:1 privado\n' +
    '• Retención de contenido incluida\n' +
    '• 15% desc en Mystika Apparel\n\n' +
    'Elige tu camino:',
    Markup.inlineKeyboard([
      [Markup.button.callback('🌙 Mysteria $14.99', 'sub_mysteria')],
      [Markup.button.callback('🔥 Ritual $49.99', 'sub_ritual')],
    ])
  )
}

async function showAccount(ctx) {
  // For now, link to web. Telegram linking will be implemented later
  await ctx.reply(
    '👤 <b>Mi cuenta Mystika</b>\n\n' +
    'Para ver tu perfil, lecciones compradas y altar, visita:\n' +
    '🌐 mystika.app/portal\n\n' +
    'Pronto podrás gestionar todo desde aquí.',
    { parse_mode: 'HTML', ...Markup.inlineKeyboard([
      [Markup.button.url('🌐 Ir a mi portal', 'https://mystika.app/portal')],
    ]) }
  )
}

bot.action('catalogo', async (ctx) => {
  await ctx.answerCbQuery()
  await showCatalog(ctx)
})

bot.action('planes', async (ctx) => {
  await ctx.answerCbQuery()
  await showPlans(ctx)
})

bot.action('cuenta', async (ctx) => {
  await ctx.answerCbQuery()
  await showAccount(ctx)
})

bot.action('web', async (ctx) => {
  await ctx.answerCbQuery('Abriendo mystika.app...')
  await ctx.reply('🌐 Abre mystika.app para la experiencia completa', Markup.inlineKeyboard([
    [Markup.button.url('✨ Ir a mystika.app', 'https://mystika.app')],
  ]))
})

bot.action(/^lesson_(\d+)$/, async (ctx) => {
  await ctx.answerCbQuery()
  const lessonId = ctx.match[1]
  try {
    const { data } = await axios.get(`${API_URL}/api/lessons/${lessonId}`)
    const lesson = data.lesson
    await ctx.replyWithHTML(
      `<b>${lesson.title}</b>\n\n` +
      `${lesson.description || 'Sin descripción'}\n\n` +
      `🥁 ${lesson.instrument} · ${lesson.difficulty || 'todos los niveles'}\n` +
      `💰 $${lesson.price_usd} USD / $${lesson.price_mxn} MXN\n\n` +
      `<i>Al comprar obtienes 1 vista. Después puedes retener o descargar.</i>`,
      Markup.inlineKeyboard([
        [Markup.button.callback(`💳 Comprar $${lesson.price_usd}`, `buy_${lesson.id}_stripe`)],
        [Markup.button.callback(`💳 Pagar con MP`, `buy_${lesson.id}_mp`)],
        [Markup.button.url('🌐 Ver en web', `https://mystika.app/lessons/${lesson.id}`)],
      ])
    )
  } catch (err) {
    await ctx.reply('Ritual no encontrado.')
  }
})

bot.action(/^buy_(\d+)_(stripe|mp)$/, async (ctx) => {
  await ctx.answerCbQuery('Generando link de pago...')
  const lessonId = ctx.match[1]
  const gateway = ctx.match[2] === 'stripe' ? 'stripe' : 'mercadopago'
  try {
    const { data } = await axios.post(`${API_URL}/api/payments/checkout/lesson`, {
      lesson_id: parseInt(lessonId),
      gateway,
    }, {
      headers: ctx.from?.id ? { 'X-Telegram-Id': String(ctx.from.id) } : {},
    })
    await ctx.reply(
      `🎯 <b>Link de pago generado:</b>\n\n${data.checkout_url}\n\n` +
      `Después del pago, tu acceso se activará automáticamente.`,
      { parse_mode: 'HTML' }
    )
  } catch (err) {
    await ctx.reply('Error al generar el pago. Intenta de nuevo.')
  }
})

bot.action('sub_mysteria', async (ctx) => {
  await ctx.answerCbQuery('Preparando suscripción...')
  try {
    const { data } = await axios.post(`${API_URL}/api/payments/checkout/subscription`, {
      plan: 'mysteria', gateway: 'stripe',
    })
    await ctx.reply(
      `🌙 <b>Plan Mysteria — $14.99/mes</b>\n\n` +
      `Link de pago:\n${data.checkout_url}\n\n` +
      `Después del pago, tu suscripción se activa automáticamente.`,
      { parse_mode: 'HTML' }
    )
  } catch (err) {
    await ctx.reply('Error al generar el link de suscripción.')
  }
})

bot.action('sub_ritual', async (ctx) => {
  await ctx.answerCbQuery('Preparando suscripción...')
  try {
    const { data } = await axios.post(`${API_URL}/api/payments/checkout/subscription`, {
      plan: 'ritual', gateway: 'stripe',
    })
    await ctx.reply(
      `🔥 <b>Plan Ritual — $49.99/mes</b>\n\n` +
      `Link de pago:\n${data.checkout_url}\n\n` +
      `Después del pago, tu suscripción se activa automáticamente.`,
      { parse_mode: 'HTML' }
    )
  } catch (err) {
    await ctx.reply('Error al generar el link de suscripción.')
  }
})

bot.on('video', async (ctx) => {
  const userId = ctx.from.id
  if (userId !== ADMIN_ID) {
    return ctx.reply('Solo Lilith puede subir contenido.')
  }
  const file = ctx.message.video
  const fileId = file.file_id
  const fileName = file.file_name || `video_${Date.now()}.mp4`
  setUpload(userId, { file_id: fileId, file_name: fileName, file_size: file.file_size })
  await ctx.reply(
    `📹 Video recibido (${(file.file_size / 1024 / 1024).toFixed(1)} MB)\n\n` +
    `Ahora dime el <b>nombre de la lección:</b>`,
    { parse_mode: 'HTML' }
  )
})

bot.on('photo', async (ctx) => {
  const userId = ctx.from.id
  if (userId !== ADMIN_ID) {
    return ctx.reply('Solo Lilith puede subir contenido.')
  }
  const photo = ctx.message.photo.pop()
  setUpload(userId, { file_id: photo.file_id, content_type: 'photo' })
  await ctx.reply(
    `📸 Foto recibida.\n\n` +
    `¿Es para <b>Mysteria</b> o <b>Ritual</b>?`,
    { parse_mode: 'HTML', ...Markup.inlineKeyboard([
      [Markup.button.callback('🌙 Mysteria', 'content_mysteria')],
      [Markup.button.callback('🔥 Ritual', 'content_ritual')],
      [Markup.button.callback('✨ Ambos', 'content_all')],
    ]) }
  )
})

bot.action(/^content_(mysteria|ritual|all)$/, async (ctx) => {
  await ctx.answerCbQuery()
  const userId = ctx.from.id
  if (userId !== ADMIN_ID) return
  const plan = ctx.match[1]
  setUpload(userId, { min_plan: plan })
  await ctx.reply('✅ Contenido guardado en la galería.')
  clearUpload(userId)
})

bot.on('text', async (ctx) => {
  const userId = ctx.from.id
  if (userId === ADMIN_ID) {
    const state = getUpload(userId)
    if (state.file_id && !state.title) {
      setUpload(userId, { title: ctx.message.text })
      return ctx.reply('💰 ¿Precio en USD? (ej: 14.99)')
    }
    if (state.title && !state.price_usd) {
      const price = parseFloat(ctx.message.text)
      if (isNaN(price)) return ctx.reply('Precio inválido. Escribe un número (ej: 14.99)')
      setUpload(userId, { price_usd: price, price_mxn: Math.round(price * 20) })
      return ctx.reply('🥁 ¿Instrumento? (bateria, guitarra, piano, voz, bajo, produccion)')
    }
    if (state.title && state.price_usd && !state.instrument) {
      const inst = ctx.message.text.toLowerCase()
      setUpload(userId, { instrument: inst })
      return ctx.reply('📝 Descripción (opcional, escribe /skip para omitir)')
    }
    if (state.title && state.price_usd && state.instrument && state.description === undefined) {
      if (ctx.message.text === '/skip') {
        setUpload(userId, { description: '' })
      } else {
        setUpload(userId, { description: ctx.message.text })
      }
      await ctx.reply(
        `✅ <b>Lección lista para guardar:</b>\n\n` +
        `🎵 ${state.title}\n` +
        `💰 $${state.price_usd} USD / $${state.price_mxn} MXN\n` +
        `🥁 ${state.instrument}\n` +
        `📝 ${state.description || 'Sin descripción'}\n\n` +
        `¿Guardar?`,
        { parse_mode: 'HTML', ...Markup.inlineKeyboard([
          [Markup.button.callback('✅ Guardar', 'save_lesson')],
          [Markup.button.callback('❌ Cancelar', 'cancel_upload')],
        ]) }
      )
    }
  }
})

bot.action('save_lesson', async (ctx) => {
  await ctx.answerCbQuery()
  const userId = ctx.from.id
  if (userId !== ADMIN_ID) return
  const state = getUpload(userId)
  try {
    await axios.post(`${API_URL}/api/admin/lessons`, {
      title: state.title,
      description: state.description || '',
      instrument: state.instrument,
      difficulty: 'beginner',
      price_usd: state.price_usd,
      price_mxn: state.price_mxn || Math.round(state.price_usd * 20),
      video_filename: state.file_name,
    })
    await ctx.reply('✅ Ritual guardado. Para publicarlo: /publicar [id]')
    clearUpload(userId)
  } catch (err) {
    await ctx.reply('Error al guardar. Intenta de nuevo.')
  }
})

bot.action('cancel_upload', async (ctx) => {
  await ctx.answerCbQuery()
  clearUpload(ctx.from.id)
  await ctx.reply('🚫 Subida cancelada.')
})

bot.command('publicar', async (ctx) => {
  if (ctx.from.id !== ADMIN_ID) return ctx.reply('Solo Lilith puede publicar.')
  const id = ctx.message.text.split(' ')[1]
  if (!id) return ctx.reply('Usa: /publicar [id de lección]')
  try {
    await axios.post(`${API_URL}/api/admin/lessons/${id}/publish`)
    await ctx.reply(`✅ Ritual ${id} publicado.`)
  } catch (err) {
    await ctx.reply('Error al publicar.')
  }
})

process.once('SIGINT', () => bot.stop('SIGINT'))
process.once('SIGTERM', () => bot.stop('SIGTERM'))

bot.launch()
console.log('Mystika Telegram Bot running...')
