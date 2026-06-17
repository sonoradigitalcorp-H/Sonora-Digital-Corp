# Skills para Músicos

## fal-ai-video
Genera videos musicales con IA usando fal.ai.
- Input: prompt de video, duración, estilo
- Output: URL del video generado
- Uso: `fal-ai-video --prompt "video musical cinemático" --duration 180`

## music-gen
Genera música con IA (MusicGen/AudioCraft).
- Input: descripción, género, duración
- Output: archivo de audio
- Uso: `music-gen --prompt "rock alternativo energético" --duration 180`

## abe-music
CRM y gestión de artistas (ABE MUSIC - THE HUB).
- Input: datos del artista
- Output: artista registrado en Neo4j
- Uso: `abe-music create-artist --nombre "Artista" --genero "pop"`

## distribution
Distribuye música a plataformas digitales.
- Input: archivo de audio, metadata
- Output: confirmación de distribución
- Uso: `distribution release --file "cancion.mp3" --platforms "spotify,apple"`

## merch-store
Gestión de merch con Printful.
- Input: diseño, productos
- Output: productos en tienda
- Uso: `merch-store create --design "logo.png" --products "tshirt,hoodie"`
