# 4. Mini-Apps en Telegram

## Que son las Mini-Apps?
Aplicaciones web embebidas DENTRO de Telegram. Se abren como un modal.

## Tipos de Mini-Apps
| Tipo | Ejemplo | Codigo |
|------|---------|--------|
| **Botones inline** | Catalogo | Python + Keyboard |
| **Web App** | Tienda completa | HTML/JS embebido |
| **Game** | Trivia, ruleta | HTML5 + Telegram API |

## Catalogo Interactivo (ya funcionando en AzREC)
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = [
    [InlineKeyboardButton("🧢 Gorras", callback_data="gorras")],
    [InlineKeyboardButton("👕 Playeras", callback_data="playeras")],
    [InlineKeyboardButton("🛒 Ir a tienda", url="https://...")],
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Catalogo:", reply_markup=reply_markup)
```

## Web App (Proximamente)
```html
<!-- Se abre como modal en Telegram -->
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<script>
  const tg = window.Telegram.WebApp;
  tg.expand(); // Pantalla completa
  tg.MainButton.setText("Comprar");
  tg.MainButton.show();
</script>
```

## Mini-Juegos
### Trivia Musical
- Bot pregunta: "Que cancion tiene mas streams?"
- Usuarios responden en grupo
- Bot suma puntos
- Leaderboard semanal

### Ruleta de Descuentos
- Usuario gira ruleta
- Gana 5-20% descuento
- Codigo unico aplica en tienda

### Dado Virtual
`/dado` → Bot tira dado virtual
Para decisiones, rifas, dinamicas de grupo
