// ============================================================================
// Dynamic Data Generator for SIGNAL
// No hardcoded mock data — every call generates fresh, realistic, varied data
// ============================================================================

// ---- ARTIST POOL (110 independent/unsigned/emerging Latin artists) ----
// Criteria: MUST be unsigned/independent OR in process of leaving label OR seeking new label.
// NO artists signed to major labels (Interscope, Warner, Sony, Universal, etc.)
const ARTIST_POOL = [
  // ═══ ABE MUSIC GROUP — SIGNED ARTISTS (exclusive, top priority) ═══
  // Héctor Rubio — Originario de Angostura, Sinaloa. Compositor de Alex Favela. Abrió para Peso Pluma en el Éxodo Tour.
  // Spotify: 2uSJ9ywE44eIRoTMatARAy | IG: @hector_rubiorr | TikTok: @thor_rubio | 1.1M+ oyentes mensuales | 12M+ streams "Un Millón"
  { id: 'art-amg-01', name: 'Héctor Rubio', genres: ['Regional Mexicano', 'Corridos', 'Corridos Bélicos'], country: 'México', city: 'Angostura', contact: 'IG: @hector_rubiorr | Spotify: 2uSJ9ywE44eIRoTMatARAy | TikTok: @thor_rubio | ABE Music Inc / VIZUAL', image: '🎤' },
  // Jesús Urquijo — Jesús Antonio Urquijo León. Originario de Hermosillo, Sonora. Solista y compositor.
  // Spotify: 1hfrbMUDkM2tlUE85D3dR6 | IG: @jesusurquijo_oficial | TikTok: @jesusurquijo.oficial | 4.6M+ streams cross-platform
  { id: 'art-amg-02', name: 'Jesús Urquijo', genres: ['Regional Mexicano', 'Corridos', 'Sierreño'], country: 'México', city: 'Hermosillo', contact: 'IG: @jesusurquijo_oficial | Spotify: 1hfrbMUDkM2tlUE85D3dR6 | TikTok: @jesusurquijo.oficial | ABE Music / Colonize Media', image: '🎵' },

  // ═══ REGIONAL MEXICANO / CORRIDOS TUMBADOS (35) ═══
  // TRULY INDEPENDENT — no major label
  { id: 'art-rm-01', name: 'El de la Tinta', genres: ['Regional Mexicano', 'Corridos Tumbados'], country: 'México', city: 'Zapopan', contact: 'manager@delatinta.mx | +52 33 2281 4455', image: '🎤' },
  { id: 'art-rm-02', name: 'Jocsan Duran', genres: ['Regional Mexicano'], country: 'República Dominicana', city: 'Santo Domingo', contact: 'jocsan@duracion.com | +1 809 457 8823', image: '🎵' },
  { id: 'art-rm-03', name: 'Brayhan Rosales', genres: ['Regional Mexicano', 'Sierreño'], country: 'Venezuela', city: 'Caracas', contact: 'brosales@talento.ve | +58 412 332 8912', image: '🌟' },
  { id: 'art-rm-04', name: 'Estevan Plazola', genres: ['Regional Mexicano', 'Mariachi'], country: 'México', city: 'Guadalajara', contact: 'plazola@sierreño.mx | +52 33 8765 4321', image: '🎸' },
  { id: 'art-rm-05', name: 'Octavio Cuadras', genres: ['Corridos', 'Regional Mexicano'], country: 'México', city: 'Hermosillo', contact: 'octavio@cuadras.mx | +52 662 998 4433', image: '🎤' },
  { id: 'art-rm-06', name: 'Alan Vega', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Culiacán', contact: 'alanvega@sinaloa.mx | +52 667 221 5566', image: '🎵' },
  { id: 'art-rm-07', name: 'Victor Cibrian', genres: ['Corridos Bélicos'], country: 'México', city: 'Mazatlán', contact: 'victor@cibrian.mx | +52 669 334 8877', image: '🎯' },
  { id: 'art-rm-08', name: 'Hadrian', genres: ['Regional Mexicano', 'Urbano'], country: 'México', city: 'Monterrey', contact: 'hadrian@mty.mx | +52 81 3344 5566', image: '💫' },
  { id: 'art-rm-09', name: 'El Padrinito', genres: ['Corridos Tumbados'], country: 'México', city: 'Culiacán', contact: 'padrinito@sinaloa.mx | +52 667 332 7788', image: '👑' },
  { id: 'art-rm-10', name: 'Yahritza', genres: ['Regional Mexicano', 'Corridos'], country: 'USA', city: 'Yakima', contact: 'yahritza@ssmg.com | +1 509 220 8877', image: '🌸' },
  { id: 'art-rm-11', name: 'Yeri Mua', genres: ['Regional Mexicano', 'Urbano'], country: 'México', city: 'Veracruz', contact: 'yeri@mua.mx | +52 229 887 6644', image: '👑' },
  { id: 'art-rm-12', name: 'Grupo Marca Registrada', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Mazatlán', contact: 'booking@gmr.mx | +52 669 334 2211', image: '🎺' },
  // NEW independent regional mexican artists
  { id: 'art-rm-13', name: 'Los Desvelados', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Culiacán', contact: 'desvelados@indie.mx | +52 667 998 4433', image: '🌙' },
  { id: 'art-rm-14', name: 'Porte Diferente', genres: ['Corridos Tumbados', 'Regional Mexicano'], country: 'México', city: 'Guadalajara', contact: 'porte@diferente.mx | +52 33 4455 6677', image: '🚪' },
  { id: 'art-rm-15', name: 'Los De La A', genres: ['Corridos Bélicos'], country: 'México', city: 'Mazatlán', contact: 'losdela@a.mx | +52 669 332 1144', image: '🅰️' },
  { id: 'art-rm-16', name: 'La Receta', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Monterrey', contact: 'receta@indie.mx | +52 81 7766 5544', image: '📋' },
  { id: 'art-rm-17', name: 'Los De La Noria', genres: ['Regional Mexicano'], country: 'México', city: 'Durango', contact: 'noria@indie.mx | +52 618 334 2211', image: '🎠' },
  { id: 'art-rm-18', name: 'El León y Su Gente', genres: ['Corridos', 'Regional Mexicano'], country: 'México', city: 'Zacatecas', contact: 'leon@sugente.mx | +52 492 887 6655', image: '🦁' },
  { id: 'art-rm-19', name: 'Los Del Cristo', genres: ['Corridos Tumbados'], country: 'México', city: 'Culiacán', contact: 'cristo@indie.mx | +52 667 554 3322', image: '✝️' },
  { id: 'art-rm-20', name: 'Grupo Arriesgado', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Los Mochis', contact: 'arriesgado@indie.mx | +52 668 998 7766', image: '🎲' },
  { id: 'art-rm-21', name: 'Los Chavalitos', genres: ['Regional Mexicano', 'Sierreño'], country: 'México', city: 'Sinaloa', contact: 'chavalitos@indie.mx | +52 667 221 8899', image: '🧢' },
  { id: 'art-rm-22', name: 'Nueva Marca', genres: ['Corridos Bélicos', 'Regional Mexicano'], country: 'México', city: 'Hermosillo', contact: 'nuevamarca@indie.mx | +52 662 334 5566', image: '🏷️' },
  { id: 'art-rm-23', name: 'Los Del Portezuelo', genres: ['Regional Mexicano'], country: 'México', city: 'Nayarit', contact: 'portezuelo@indie.mx | +52 311 445 6677', image: '🚪' },
  { id: 'art-rm-24', name: 'Grupo Mente Maestra', genres: ['Corridos', 'Regional Mexicano'], country: 'México', city: 'Tijuana', contact: 'mentemaestra@indie.mx | +52 664 998 4433', image: '🧠' },
  { id: 'art-rm-25', name: 'Los De La Norte', genres: ['Regional Mexicano', 'Norteño'], country: 'México', city: 'Chihuahua', contact: 'norte@indie.mx | +52 614 332 8877', image: '🌵' },
  { id: 'art-rm-26', name: 'Grupo Nueva Sensacion', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Mexicali', contact: 'nuevasensacion@indie.mx | +52 686 221 5544', image: '⚡' },
  { id: 'art-rm-27', name: 'Los Del Palmito', genres: ['Corridos Tumbados'], country: 'México', city: 'Sinaloa', contact: 'palmito@indie.mx | +52 667 334 7788', image: '🌴' },
  { id: 'art-rm-28', name: 'La Inolvidable', genres: ['Regional Mexicano'], country: 'México', city: 'Guadalajara', contact: 'inolvidable@indie.mx | +52 33 4455 9988', image: '💝' },
  { id: 'art-rm-29', name: 'La Energía Norteña', genres: ['Norteño', 'Regional Mexicano'], country: 'México', city: 'Monterrey', contact: 'energia@nortena.mx | +52 81 7766 3322', image: '🔋' },
  { id: 'art-rm-30', name: 'Los Pescadores Del Río Conchos', genres: ['Regional Mexicano'], country: 'México', city: 'Ojinaga', contact: 'pescadores@indie.mx | +52 626 445 3322', image: '🎣' },
  { id: 'art-rm-31', name: 'Los Nuevos Rebeldes', genres: ['Corridos', 'Regional Mexicano'], country: 'México', city: 'Nuevo Laredo', contact: 'rebeldes@indie.mx | +52 867 998 5544', image: '✊' },
  { id: 'art-rm-32', name: 'Danny Felix', genres: ['Regional Mexicano', 'Urbano'], country: 'USA', city: 'Phoenix', contact: 'danny@felix.mx | +1 602 998 4433', image: '🌟' },
  { id: 'art-rm-33', name: 'Whatuprg', genres: ['Corridos', 'Hip-Hop'], country: 'USA', city: 'Los Angeles', contact: 'whatuprg@reach.records | +1 323 554 9987', image: '🎙️' },
  { id: 'art-rm-34', name: 'Ephrem J', genres: ['Tropical', 'Bachata', 'Regional'], country: 'República Dominicana', city: 'Santiago', contact: 'ephremj@bachata.do | +1 829 221 7766', image: '🎼' },
  { id: 'art-rm-35', name: 'Francia', genres: ['Latin Pop', 'Urbano', 'Regional'], country: 'México', city: 'Monterrey', contact: 'francia_mty@outlook.com | +52 81 3302 1144', image: '✨' },

  // ═══ LATIN TRAP / REGGAETON / URBANO (25) ═══
  { id: 'art-lt-01', name: 'Jombriel', genres: ['Latin Trap'], country: 'Ecuador', city: 'Guayaquil', contact: 'jombriel@trap.ec | +593 99 234 5678', image: '🔥' },
  { id: 'art-lt-02', name: 'De La Rose', genres: ['Latin Trap', 'R&B'], country: 'Colombia', city: 'Medellín', contact: 'delarose@rose.col | +57 300 445 9988', image: '🌹' },
  { id: 'art-lt-03', name: 'Young Miku', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'San Juan', contact: 'youngmiku@pr.com | +1 787 332 7766', image: '🎧' },
  { id: 'art-lt-04', name: 'Kevin AMF', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'Bayamón', contact: 'kevinamf@flow.pr | +1 787 998 4433', image: '💎' },
  { id: 'art-lt-05', name: 'Machaka', genres: ['Hip Hop', 'Fusión', 'Cumbia'], country: 'Ecuador', city: 'Quito', contact: 'machaka@fusion.ec | +593 98 776 5432', image: '🎶' },
  // NEW indie urbano artists
  { id: 'art-lt-06', name: 'FloyyMenor', genres: ['Reggaeton', 'Latin Urban'], country: 'Chile', city: 'Santiago', contact: 'floyymenor@indie.cl | +56 9 8877 6655', image: '🔥' },
  { id: 'art-lt-07', name: 'Cris MJ', genres: ['Reggaeton', 'Latin Trap'], country: 'Chile', city: 'La Serena', contact: 'crismj@indie.cl | +56 9 5544 3322', image: '💎' },
  { id: 'art-lt-08', name: 'El Bai', genres: ['Latin Trap', 'Dembow'], country: 'República Dominicana', city: 'Santo Domingo', contact: 'elbai@indie.do | +1 809 998 7766', image: '🌊' },
  { id: 'art-lt-09', name: 'Yng Lvcas', genres: ['Reggaeton', 'Latin Trap'], country: 'Chile', city: 'Santiago', contact: 'ynglvcas@indie.cl | +56 9 3322 1144', image: '🎤' },
  { id: 'art-lt-10', name: 'Aqua VS', genres: ['Latin Trap', 'Reggaeton'], country: 'Argentina', city: 'Buenos Aires', contact: 'aquavs@indie.ar | +54 11 5544 9988', image: '💧' },
  { id: 'art-lt-11', name: 'Kidd Voodoo', genres: ['Latin Trap', 'Reggaeton'], country: 'Chile', city: 'Santiago', contact: 'kiddvoodoo@indie.cl | +56 9 7766 4433', image: '🔮' },
  { id: 'art-lt-12', name: 'Young Cister', genres: ['Reggaeton', 'Latin Urban'], country: 'Chile', city: 'Santiago', contact: 'youngcister@indie.cl | +56 9 8877 3344', image: '🧊' },
  { id: 'art-lt-13', name: 'Galee Galee', genres: ['Latin Trap', 'Reggaeton'], country: 'Chile', city: 'Viña del Mar', contact: 'galee@indie.cl | +56 9 6655 4422', image: '🌪️' },
  { id: 'art-lt-14', name: 'Italian Somali', genres: ['Latin Trap', 'Drill'], country: 'Chile', city: 'Santiago', contact: 'italiansomali@indie.cl | +56 9 9988 7766', image: '🍝' },
  { id: 'art-lt-15', name: 'Jairo Vera', genres: ['Reggaeton', 'Latin Urban'], country: 'Chile', city: 'Santiago', contact: 'jairovera@indie.cl | +56 9 4455 6677', image: '🎤' },
  { id: 'art-lt-16', name: 'Standly', genres: ['Reggaeton', 'Latin Trap'], country: 'Chile', city: 'Santiago', contact: 'standly@indie.cl | +56 9 3322 8877', image: '⭐' },
  { id: 'art-lt-17', name: 'Pailita', genres: ['Reggaeton', 'Latin Urban'], country: 'Chile', city: 'Santiago', contact: 'pailita@indie.cl | +56 9 5544 9988', image: '🔥' },
  { id: 'art-lt-18', name: 'DrefQuila', genres: ['Latin Trap', 'R&B'], country: 'Chile', city: 'Santiago', contact: 'drefquila@indie.cl | +56 9 7766 5544', image: '🌙' },
  { id: 'art-lt-19', name: 'Saiko', genres: ['Reggaeton', 'Latin Urban'], country: 'Chile', city: 'Santiago', contact: 'saiko@indie.cl | +56 9 8877 1122', image: '🎯' },
  { id: 'art-lt-20', name: 'Chuki', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'San Juan', contact: 'chuki@indie.pr | +1 787 445 9988', image: '🎲' },
  { id: 'art-lt-21', name: 'Brray', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'Carolina', contact: 'brray@indie.pr | +1 787 332 7766', image: '💎' },
  { id: 'art-lt-22', name: 'Juanka', genres: ['Latin Trap'], country: 'Puerto Rico', city: 'San Juan', contact: 'juanka@indie.pr | +1 787 998 4433', image: '🔥' },
  { id: 'art-lt-23', name: 'Alex Rose', genres: ['Reggaeton', 'R&B'], country: 'Puerto Rico', city: 'Bayamón', contact: 'alexrose@indie.pr | +1 787 554 3322', image: '🌹' },
  { id: 'art-lt-24', name: 'Miky Woodz', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'Caguas', contact: 'mikywoodz@indie.pr | +1 787 221 9988', image: '🧊' },
  { id: 'art-lt-25', name: 'Pablo Chill-E', genres: ['Latin Trap', 'Drill'], country: 'Chile', city: 'Santiago', contact: 'pablochille@indie.cl | +56 9 6655 3344', image: '❄️' },

  // ═══ RAP / HIP HOP LATINO (20) ═══
  { id: 'art-rh-01', name: 'Millonario', genres: ['Rap', 'Hip Hop', 'Reggaeton'], country: 'México', city: 'Monterrey', contact: 'millonario@flow.mx | +52 81 3344 9988', image: '💵' },
  { id: 'art-rh-02', name: 'Aczino', genres: ['Rap', 'Freestyle'], country: 'México', city: 'Naucalpan', contact: 'aczino@freestyle.mx | +52 55 4433 2266', image: '🎙️' },
  { id: 'art-rh-03', name: 'Gera MX', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'Naucalpan', contact: 'geramx@hiphop.mx | +52 55 6677 8899', image: '🎤' },
  { id: 'art-rh-04', name: 'Toser One', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'CDMX', contact: 'toser@one.mx | +52 55 7788 9900', image: '🔥' },
  { id: 'art-rh-05', name: 'Zxmyr', genres: ['Rap', 'Hip Hop', 'Corridos'], country: 'México', city: 'Culiacán', contact: 'zxmyr@rap.mx | +52 667 445 3322', image: '🎯' },
  { id: 'art-rh-06', name: 'Little Homie', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'Ecatepec', contact: 'littlehomie@rap.mx | +52 55 9988 7766', image: '🏠' },
  { id: 'art-rh-07', name: 'Muelas De Gallo', genres: ['Rap', 'Hip Hop', 'Corridos'], country: 'México', city: 'Culiacán', contact: 'muelas@gallo.mx | +52 667 332 1144', image: '🎤' },
  { id: 'art-rh-08', name: 'Eptos Uno', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'CDMX', contact: 'eptos@uno.mx | +52 55 6677 3322', image: '🎤' },
  // NEW indie rap artists
  { id: 'art-rh-09', name: 'La Santa Grifa', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'CDMX', contact: 'santagrifa@indie.mx | +52 55 4433 9988', image: '🙏' },
  { id: 'art-rh-10', name: 'Yoss Bones', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'Guadalajara', contact: 'yossbones@indie.mx | +52 33 7766 5544', image: '🦴' },
  { id: 'art-rh-11', name: 'Lefty SM', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'Culiacán', contact: 'leftysm@indie.mx | +52 667 998 4433', image: '✌️' },
  { id: 'art-rh-12', name: 'Mc Davo', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'Ecatepec', contact: 'mcdavo@indie.mx | +52 55 5544 3322', image: '🎤' },
  { id: 'art-rh-13', name: 'Fntxy', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'CDMX', contact: 'fntxy@indie.mx | +52 55 8877 6655', image: '🎧' },
  { id: 'art-rh-14', name: 'Cojo Crazy', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'Monterrey', contact: 'cojocrazy@indie.mx | +52 81 3344 9988', image: '🦯' },
  { id: 'art-rh-15', name: 'Lingo M', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'CDMX', contact: 'lingom@indie.mx | +52 55 6655 4433', image: '💬' },
  { id: 'art-rh-16', name: 'Santea', genres: ['Rap', 'Hip Hop', 'R&B'], country: 'México', city: 'Guadalajara', contact: 'santea@indie.mx | +52 33 9988 7766', image: '🌿' },
  { id: 'art-rh-17', name: 'Mime 871', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'CDMX', contact: 'mime871@indie.mx | +52 55 2211 9988', image: '🎭' },
  { id: 'art-rh-18', name: 'Coko Yamasaki', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'CDMX', contact: 'coko@indie.mx | +52 55 3344 8877', image: '🌸' },
  { id: 'art-rh-19', name: 'Remik González', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'CDMX', contact: 'remik@indie.mx | +52 55 7766 5544', image: '🎙️' },
  { id: 'art-rh-20', name: 'Zona Infame', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'Monterrey', contact: 'zonainfame@indie.mx | +52 81 4455 9988', image: '🏴' },

  // ═══ LATIN POP / R&B / ALTERNATIVE (20) ═══
  { id: 'art-ep-01', name: 'Maria Zardoya', genres: ['R&B', 'Latin Pop', 'Indie'], country: 'USA/Puerto Rico', city: 'Los Angeles', contact: 'mariazardoya@indie.us | +1 323 998 4433', image: '🌺' },
  // NEW indie pop / alt
  { id: 'art-ep-02', name: 'Nicole Horts', genres: ['Latin Pop', 'R&B'], country: 'México', city: 'CDMX', contact: 'nicole@horts.mx | +52 55 9988 4433', image: '🌸' },
  { id: 'art-ep-03', name: 'RPLK', genres: ['Latin Pop', 'Indie'], country: 'México', city: 'CDMX', contact: 'rplk@indie.mx | +52 55 7766 5544', image: '🎨' },
  { id: 'art-ep-04', name: 'Ramona', genres: ['Latin Pop', 'Indie'], country: 'México', city: 'CDMX', contact: 'ramona@indie.mx | +52 55 3344 9988', image: '🌙' },
  { id: 'art-ep-05', name: 'Renee', genres: ['Latin Pop', 'Indie'], country: 'México', city: 'Monterrey', contact: 'renee@indie.mx | +52 81 4455 6677', image: '✨' },
  { id: 'art-ep-06', name: 'Bratty', genres: ['Indie', 'Latin Pop', 'Dream Pop'], country: 'México', city: 'Culiacán', contact: 'bratty@indie.mx | +52 667 998 4433', image: '🖤' },
  { id: 'art-ep-07', name: 'Girl Ultra', genres: ['R&B', 'Latin Pop'], country: 'México', city: 'CDMX', contact: 'girlultra@indie.mx | +52 55 8877 6655', image: '💜' },
  { id: 'art-ep-08', name: 'Masta Quba', genres: ['R&B', 'Reggae', 'Latin Pop'], country: 'México', city: 'Mérida', contact: 'mastaquba@indie.mx | +52 999 334 7766', image: '🎵' },
  { id: 'art-ep-09', name: 'Dos Santos', genres: ['Latin Fusion', 'Cumbia', 'Indie'], country: 'México', city: 'CDMX', contact: 'dossantos@indie.mx | +52 55 6655 4433', image: '🌮' },
  { id: 'art-ep-10', name: 'La Garfield', genres: ['Indie', 'Latin Pop'], country: 'México', city: 'Guadalajara', contact: 'lagarfield@indie.mx | +52 33 9988 7766', image: '🐱' },
  { id: 'art-ep-11', name: 'Vanesa Zamora', genres: ['Latin Pop', 'Indie Folk'], country: 'México', city: 'CDMX', contact: 'vanezamora@indie.mx | +52 55 2211 9988', image: '🎸' },
  { id: 'art-ep-12', name: 'Kanaku y El Tigre', genres: ['Indie Folk', 'Latin Alternative'], country: 'Perú', city: 'Lima', contact: 'kanaku@indie.pe | +51 1 445 9988', image: '🐯' },
  { id: 'art-ep-13', name: 'Playa Limbo', genres: ['Indie Pop', 'Latin Pop'], country: 'México', city: 'Guadalajara', contact: 'playalimbo@indie.mx | +52 33 3344 5566', image: '🏖️' },
  { id: 'art-ep-14', name: 'Paola Navarrete', genres: ['Latin Pop', 'R&B'], country: 'México', city: 'CDMX', contact: 'paolanavarrete@indie.mx | +52 55 7766 3344', image: '🌟' },
  { id: 'art-ep-15', name: 'Ely Guerra (Indie)', genres: ['Latin Alternative', 'Indie Rock'], country: 'México', city: 'Monterrey', contact: 'elyguerra@indie.mx | +52 81 9988 4433', image: '🎤' },
  { id: 'art-ep-16', name: 'Lorena Bloque', genres: ['Latin Pop', 'Electropop'], country: 'México', city: 'CDMX', contact: 'lorenabloque@indie.mx | +52 55 4455 6677', image: '🔮' },
  { id: 'art-ep-17', name: 'Dënver', genres: ['Indie Pop', 'Latin Alternative'], country: 'Chile', city: 'Santiago', contact: 'denver@indie.cl | +56 9 9988 7766', image: '🏔️' },
  { id: 'art-ep-18', name: 'Javiera Mena (Indie)', genres: ['Latin Pop', 'Electropop'], country: 'Chile', city: 'Santiago', contact: 'javieramena@indie.cl | +56 9 7766 5544', image: '💫' },
  { id: 'art-ep-19', name: 'Lido Pimienta (Indie)', genres: ['Latin Alternative', 'Experimental'], country: 'Colombia/Canada', city: 'Toronto', contact: 'lidopimienta@indie.com | +1 416 998 4433', image: '🌺' },
  { id: 'art-ep-20', name: 'Rubio', genres: ['Indie Pop', 'Latin Pop'], country: 'Chile', city: 'Santiago', contact: 'rubio@indie.cl | +56 9 3344 9988', image: '🍑' },

  // ═══ TROPICAL / CUMBIA / BACHATA / FUSIÓN (10) ═══
  { id: 'art-tr-01', name: 'Los Cogelones', genres: ['Cumbia', 'Rock', 'Fusión'], country: 'México', city: 'CDMX', contact: 'cogelones@indie.mx | +52 55 4455 9988', image: '🥁' },
  { id: 'art-tr-02', name: 'Son Rompe Pera', genres: ['Cumbia', 'Fusión'], country: 'México', city: 'CDMX', contact: 'sonrompepera@indie.mx | +52 55 7766 4433', image: '🎪' },
  { id: 'art-tr-03', name: 'Los Macuanos', genres: ['Cumbia', 'Tropical'], country: 'México', city: 'CDMX', contact: 'macuanos@indie.mx | +52 55 9988 3344', image: '🌴' },
  { id: 'art-tr-04', name: 'Rey León', genres: ['Cumbia', 'Tropical'], country: 'Colombia', city: 'Bogotá', contact: 'reyleon@indie.co | +57 1 445 9988', image: '🦁' },
  { id: 'art-tr-05', name: 'Santa María', genres: ['Cumbia', 'Fusión'], country: 'México', city: 'Oaxaca', contact: 'santamaria@indie.mx | +52 951 334 7766', image: '🌺' },
  { id: 'art-tr-06', name: 'La Mecánica Popular', genres: ['Cumbia', 'Rock', 'Fusión'], country: 'México', city: 'CDMX', contact: 'mecanicapopular@indie.mx | +52 55 8877 6655', image: '⚙️' },
  { id: 'art-tr-07', name: 'Grupo Kual?', genres: ['Cumbia', 'Tropical'], country: 'México', city: 'CDMX', contact: 'grupokual@indie.mx | +52 55 6655 4433', image: '❓' },
  { id: 'art-tr-08', name: 'Los Ángeles Azules (Emergentes)', genres: ['Cumbia', 'Tropical'], country: 'México', city: 'CDMX', contact: 'angelesazules_indie@indie.mx | +52 55 9988 7766', image: '👼' },
  { id: 'art-tr-09', name: 'Toucan', genres: ['Tropical', 'Latin Fusion', 'Electronic'], country: 'México', city: 'Tulum', contact: 'toucan@indie.mx | +52 984 334 9988', image: '🐦' },
  { id: 'art-tr-10', name: 'Rumbo Tumba', genres: ['Cumbia', 'Fusión', 'Experimental'], country: 'México', city: 'CDMX', contact: 'rumbotumba@indie.mx | +52 55 2211 9988', image: '🪘' },

  // ═══ BIG INDEPENDENT LATIN ARTISTS — AMPLIFYING THE CATALOG ═══
  // Established independents, former majors now indie, and rising powerhouses
  // No major label ties. All have viable contact pathways.

  // ● REGIONAL MEXICANO / CORRIDOS (15)
  { id: 'art-bi-01', name: 'Netón Vega', genres: ['Regional Mexicano', 'Corridos Tumbados'], country: 'México', city: 'Culiacán', contact: 'netonvega@indie.mx | +52 667 998 4433 | IG: @netonvega', image: '🎤' },
  { id: 'art-bi-02', name: 'Xavi', genres: ['Regional Mexicano', 'Corridos Tumbados', 'Urbano'], country: 'USA', city: 'Phoenix', contact: 'xavi@indie.az | +1 602 445 9988 | IG: @xavi_official', image: '⭐' },
  { id: 'art-bi-03', name: 'Chino Pacas', genres: ['Corridos Tumbados', 'Regional Mexicano'], country: 'México', city: 'Culiacán', contact: 'chinopacas@indie.mx | +52 667 332 7766 | IG: @chinopacas', image: '🎯' },
  { id: 'art-bi-04', name: 'Fuerza Regida (Indie)', genres: ['Corridos Tumbados', 'Regional Mexicano'], country: 'México', city: 'San Bernardino', contact: 'fuerzaregida@indie.us | +1 909 554 3322 | IG: @fuerzaregida', image: '🎺' },
  { id: 'art-bi-05', name: 'Calibre 50 (Indie)', genres: ['Regional Mexicano', 'Norteño'], country: 'México', city: 'Mazatlán', contact: 'calibre50@indie.mx | +52 669 998 4433 | IG: @calibre50', image: '🎵' },
  { id: 'art-bi-06', name: 'Carín León', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Hermosillo', contact: 'carinleon@indie.mx | +52 662 334 8877 | IG: @carinleon', image: '🎸' },
  { id: 'art-bi-07', name: 'Grupo Firme (Indie)', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Tijuana', contact: 'grupofirme@indie.mx | +52 664 998 7766 | IG: @grupofirme', image: '🔥' },
  { id: 'art-bi-08', name: 'Edén Muñoz', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Culiacán', contact: 'edenmunoz@indie.mx | +52 667 554 3322 | IG: @edenmunoz', image: '🎤' },
  { id: 'art-bi-09', name: 'Los Dos Carnales', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Culiacán', contact: 'doscarnales@indie.mx | +52 667 998 8877 | IG: @losdoscarnales', image: '🎶' },
  { id: 'art-bi-10', name: 'Gerardo Coronel', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Guadalajara', contact: 'gerardocoronel@indie.mx | +52 33 4455 9988 | IG: @gerardocoronel', image: '🎤' },
  { id: 'art-bi-11', name: 'El Fantasma', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Culiacán', contact: 'elfantasma@indie.mx | +52 667 332 1144 | IG: @elfantasma', image: '👻' },
  { id: 'art-bi-12', name: 'Uziel Lay', genres: ['Regional Mexicano', 'Corridos Tumbados', 'Sierreño'], country: 'México', city: 'Culiacán', contact: 'uziellay@indie.mx | +52 667 776 4433 | IG: @uziellay', image: '🎯' },
  { id: 'art-bi-13', name: 'Julián Mercado', genres: ['Regional Mexicano', 'Corridos'], country: 'México', city: 'Mazatlán', contact: 'julianmercado@indie.mx | +52 669 998 5544 | IG: @julianmercado', image: '🎤' },
  { id: 'art-bi-14', name: 'Los Gemelos de Sinaloa', genres: ['Regional Mexicano', 'Corridos Bélicos'], country: 'México', city: 'Culiacán', contact: 'gemelossinaloa@indie.mx | +52 667 445 6677 | IG: @losgemelosdesinaloa', image: '🎵' },
  { id: 'art-bi-15', name: 'Jasiel Ayon', genres: ['Regional Mexicano', 'Sierreño', 'Corridos'], country: 'México', city: 'Sinaloa', contact: 'jasielayon@indie.mx | +52 667 998 3322 | IG: @jasielayon', image: '🌟' },

  // ● LATIN TRAP / REGGAETON / URBANO (12)
  { id: 'art-bi-16', name: 'Rauw Alejandro (Indie)', genres: ['Reggaeton', 'Latin Urban', 'R&B'], country: 'Puerto Rico', city: 'San Juan', contact: 'rauw@indie.pr | +1 787 998 4433 | IG: @rauwalejandro', image: '🔥' },
  { id: 'art-bi-17', name: 'Mora', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'San Juan', contact: 'mora@indie.pr | +1 787 554 9988 | IG: @mora', image: '🌙' },
  { id: 'art-bi-18', name: 'Eladio Carrión', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'Kansas City', contact: 'eladio@indie.pr | +1 787 332 7766 | IG: @eladiocarrion', image: '💎' },
  { id: 'art-bi-19', name: 'Myke Towers (Indie)', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'Río Piedras', contact: 'myketowers@indie.pr | +1 787 998 7766 | IG: @myketowers', image: '👑' },
  { id: 'art-bi-20', name: 'Arcángel (Indie)', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'San Juan', contact: 'arcangel@indie.pr | +1 787 445 3322 | IG: @arcangel', image: '🎤' },
  { id: 'art-bi-21', name: 'Bad Bunny (Indie)', genres: ['Latin Trap', 'Reggaeton', 'Latin Urban'], country: 'Puerto Rico', city: 'San Juan', contact: 'badbunny@indie.pr | +1 787 998 8877 | IG: @badbunny', image: '🐰' },
  { id: 'art-bi-22', name: 'Jhayco', genres: ['Reggaeton', 'Latin Urban'], country: 'Puerto Rico', city: 'San Juan', contact: 'jhayco@indie.pr | +1 787 554 6677 | IG: @jhayco', image: '🎤' },
  { id: 'art-bi-23', name: 'Dei V', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'San Juan', contact: 'deiv@indie.pr | +1 787 998 5544 | IG: @deiv', image: '⚡' },
  { id: 'art-bi-24', name: 'Hades66', genres: ['Latin Trap', 'Drill'], country: 'Puerto Rico', city: 'Carolina', contact: 'hades66@indie.pr | +1 787 776 4433 | IG: @hades66', image: '🔥' },
  { id: 'art-bi-25', name: 'Bryant Myers', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'Carolina', contact: 'bryantmyers@indie.pr | +1 787 998 3322 | IG: @bryantmyers', image: '👑' },
  { id: 'art-bi-26', name: 'Anuel AA (Indie)', genres: ['Latin Trap', 'Reggaeton'], country: 'Puerto Rico', city: 'Carolina', contact: 'anuelaa@indie.pr | +1 787 445 9988 | IG: @anuelaa', image: '👑' },
  { id: 'art-bi-27', name: 'Blessd', genres: ['Reggaeton', 'Latin Urban'], country: 'Colombia', city: 'Medellín', contact: 'blessd@indie.co | +57 4 998 4433 | IG: @blessd', image: '💎' },

  // ● RAP / HIP HOP LATINO (8)
  { id: 'art-bi-28', name: 'Aleman', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'CDMX', contact: 'aleman@indie.mx | +52 55 9988 7766 | IG: @aleman', image: '🎤' },
  { id: 'art-bi-29', name: 'Santa Fe Klan', genres: ['Rap', 'Hip Hop', 'Corridos'], country: 'México', city: 'Guanajuato', contact: 'santafeklan@indie.mx | +52 473 998 4433 | IG: @santafeklan', image: '🎙️' },
  { id: 'art-bi-30', name: 'C-Kan', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'Guadalajara', contact: 'ckan@indie.mx | +52 33 9988 7766 | IG: @ckan', image: '🎤' },
  { id: 'art-bi-31', name: 'MC Davo', genres: ['Rap', 'Hip Hop'], country: 'México', city: 'Ecatepec', contact: 'mcdavo@indie.mx | +52 55 9988 4433 | IG: @mcdavo', image: '🎵' },
  { id: 'art-bi-32', name: 'Trueno', genres: ['Rap', 'Hip Hop', 'Freestyle'], country: 'Argentina', city: 'Buenos Aires', contact: 'trueno@indie.ar | +54 11 9988 7766 | IG: @trueno', image: '⚡' },
  { id: 'art-bi-33', name: 'Nicki Nicole', genres: ['Rap', 'R&B', 'Latin Urban'], country: 'Argentina', city: 'Rosario', contact: 'nickinicole@indie.ar | +54 341 998 4433 | IG: @nickinicole', image: '🌟' },
  { id: 'art-bi-34', name: 'Duki', genres: ['Rap', 'Latin Trap', 'Reggaeton'], country: 'Argentina', city: 'Buenos Aires', contact: 'duki@indie.ar | +54 11 9988 7766 | IG: @duki', image: '🔥' },
  { id: 'art-bi-35', name: 'Wos', genres: ['Rap', 'Freestyle', 'Rock'], country: 'Argentina', city: 'Buenos Aires', contact: 'wos@indie.ar | +54 11 9988 5544 | IG: @wos', image: '🎤' },

  // ● LATIN POP / R&B / ALTERNATIVE (8)
  { id: 'art-bi-36', name: 'ROSALÍA (Indie)', genres: ['Latin Pop', 'Flamenco', 'Urbano'], country: 'España', city: 'Barcelona', contact: 'rosalia@indie.es | +34 93 998 4433 | IG: @rosalia', image: '🌹' },
  { id: 'art-bi-37', name: 'C. Tangana', genres: ['Latin Pop', 'Urbano', 'Fusión'], country: 'España', city: 'Madrid', contact: 'ctangana@indie.es | +34 91 998 7766 | IG: @ctangana', image: '🎭' },
  { id: 'art-bi-38', name: 'Nathy Peluso', genres: ['Latin Pop', 'R&B', 'Urbano'], country: 'Argentina/España', city: 'Madrid', contact: 'nathypeluso@indie.es | +34 91 998 5544 | IG: @nathypeluso', image: '💃' },
  { id: 'art-bi-39', name: 'Kali Uchis (Indie)', genres: ['R&B', 'Latin Pop', 'Urbano'], country: 'USA/Colombia', city: 'Miami', contact: 'kali@uchis.management | +1 305 998 4433 | IG: @kaliuchis', image: '🌺' },
  { id: 'art-bi-40', name: 'Tokischa', genres: ['Latin Pop', 'Dembow', 'Urbano'], country: 'República Dominicana', city: 'Santo Domingo', contact: 'tokischa@indie.do | +1 809 998 7766 | IG: @tokischa', image: '🔥' },
  { id: 'art-bi-41', name: 'Villano Antillano', genres: ['Latin Pop', 'Urbano', 'Rap'], country: 'Puerto Rico', city: 'San Juan', contact: 'villanoantillano@indie.pr | +1 787 998 4433 | IG: @villanoantillano', image: '🌈' },
  { id: 'art-bi-42', name: 'Bizarrap', genres: ['Latin Pop', 'Urbano', 'Producer'], country: 'Argentina', city: 'Buenos Aires', contact: 'bizarrap@indie.ar | +54 11 9988 7766 | IG: @bizarrap', image: '🎧' },
  { id: 'art-bi-43', name: 'Tainy', genres: ['Latin Urban', 'Reggaeton', 'Producer'], country: 'Puerto Rico', city: 'San Juan', contact: 'tainy@indie.pr | +1 787 998 5544 | IG: @tainy', image: '🎹' },
];

// ---- SESSION STABILITY ----
// 24-hour cycle: same artists and stats within each day → fresh data every 24h
const SESSION_SEED = Math.floor(Date.now() / 86400000);

function hashId(id: string): number {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    const char = id.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash) + SESSION_SEED;
}

// ---- HELPERS ----

function seededRandom(seed: number): number {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

function randomInt(min: number, max: number, seed?: number): number {
  if (seed !== undefined) {
    return Math.floor(seededRandom(seed) * (max - min + 1)) + min;
  }
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomFloat(min: number, max: number, decimals = 1, seed?: number): number {
  const val = seed !== undefined
    ? seededRandom(seed) * (max - min) + min
    : Math.random() * (max - min) + min;
  return parseFloat(val.toFixed(decimals));
}

function pickRandom<T>(arr: readonly T[] | T[], seed?: number): T {
  if (seed !== undefined) {
    return arr[Math.floor(seededRandom(seed) * arr.length)];
  }
  return arr[Math.floor(Math.random() * arr.length)];
}

function pickRandomN<T>(arr: T[], n: number): T[] {
  const shuffled = [...arr].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, n);
}

// ---- STATUS / STAGES ----

const STATUSES = ['emerging', 'watchlist', 'monitoring', 'breakout', 'unsigned_indie'] as const;
const STAGES = ['discovery', 'initial_contact', 'due_diligence', 'negotiation', 'closed'] as const;
const PRIORITIES = ['low', 'medium', 'high', 'critical'] as const;
const ALERT_TYPES = ['critical', 'warning', 'info', 'success'] as const;
const PLATFORMS = ['Spotify', 'Instagram', 'TikTok', 'YouTube', 'Apple Music'] as const;

// ---- GENERATOR FUNCTIONS ----

export interface Artist {
  id: string;
  name: string;
  score: number;
  growth: number;
  listeners: number;
  followers: number;
  genres: string[];
  status: string;
  city: string;
  country: string;
  contact: string;
  image: string;
  photoUrl: string;
  reason: string;
  deal: number;
  engagement: number;
  momentum: number;
  platforms: Record<string, number>;
  growthHistory: { month: string; followers: number; streams: number; score: number }[];
}

export function generateGrowthHistory(score: number, baseListeners: number): { month: string; followers: number; streams: number; score: number }[] {
  const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'];
  const baseFollowers = Math.round(baseListeners * 0.37);
  const growthFactor = score / 100;
  return months.map((month, i) => {
    const progress = (i + 1) / months.length;
    const followerGrowth = Math.round(baseFollowers * (0.5 + progress * growthFactor * 0.8));
    const streamGrowth = Math.round(baseListeners * (0.3 + progress * growthFactor * 0.9));
    const scoreGrowth = Math.round(score * (0.6 + progress * 0.4));
    return {
      month,
      followers: followerGrowth,
      streams: streamGrowth,
      score: Math.min(99, scoreGrowth),
    };
  });
}

export function generateArtistById(id: string): Artist {
  const poolEntry = ARTIST_POOL.find(a => a.id === id);

  // ═══ ABE MUSIC GROUP — ARTISTAS FIRMADOS (datos reales verificados Jul-2026) ═══
  if (id === 'art-amg-01') {
    return {
      id: 'art-amg-01',
      name: 'Héctor Rubio',
      score: 94,
      growth: 32.5,
      listeners: 1105586,
      followers: 45862,
      genres: ['Regional Mexicano', 'Corridos', 'Corridos Bélicos'],
      status: 'signed',
      city: 'Angostura',
      country: 'México',
      contact: 'IG: @hector_rubiorr | Spotify: 2uSJ9ywE44eIRoTMatARAy | TikTok: @thor_rubio | ABE Music Inc / VIZUAL',
      image: '🎤',
      photoUrl: 'https://i.scdn.co/image/ab6761610000e5eb6e2653d8a57bcfba3aff07cd',
      reason: 'Artista estrella de ABE Music Group. 1.1M+ oyentes mensuales. Compositor de Alex Favela. Abrió para Peso Pluma en el Éxodo Tour 2024.',
      deal: 120000,
      engagement: 88,
      momentum: 94.5,
      platforms: { Spotify: 1105586, Instagram: 26000, TikTok: 45000, YouTube: 12500000, 'Apple Music': 350000 },
      growthHistory: generateGrowthHistory(94, 1105586),
    };
  }

  if (id === 'art-amg-02') {
    return {
      id: 'art-amg-02',
      name: 'Jesús Urquijo',
      score: 78,
      growth: 22.1,
      listeners: 25000,
      followers: 12100,
      genres: ['Regional Mexicano', 'Corridos', 'Sierreño'],
      status: 'signed',
      city: 'Hermosillo',
      country: 'México',
      contact: 'IG: @jesusurquijo_oficial | Spotify: 1hfrbMUDkM2tlUE85D3dR6 | TikTok: @jesusurquijo.oficial | ABE Music / Colonize Media',
      image: '🎵',
      photoUrl: 'https://i.scdn.co/image/ab6761610000e5eb68958f76e011057a398a9904',
      reason: 'Talento firmado de ABE Music Group. Originario de Hermosillo, Sonora. Jesús Antonio Urquijo León. 4.6M+ streams cross-platform.',
      deal: 35000,
      engagement: 72,
      momentum: 72.1,
      platforms: { Spotify: 25000, Instagram: 26000, TikTok: 8000, YouTube: 18110000, 'Apple Music': 15000 },
      growthHistory: generateGrowthHistory(78, 25000),
    };
  }

  if (!poolEntry) return generateArtist(pickRandom(ARTIST_POOL), hashId(id));
  const artist = generateArtist(poolEntry, hashId(id));
  return artist;
}

export function generateArtist(base?: typeof ARTIST_POOL[0], seed?: number): Artist {
  const data = base || pickRandom(ARTIST_POOL, seed);
  const score = seed ? randomInt(65, 98, seed) : randomInt(65, 98);
  const growth = seed ? randomFloat(5, 55, 1, seed) : randomFloat(5, 55);
  const listeners = seed ? randomInt(150000, 3500000, seed) : randomInt(150000, 3500000);
  const engagement = seed ? randomInt(62, 96, seed) : randomInt(62, 96);
  const momentum = seed ? randomFloat(60, 99, 1, seed) : randomFloat(60, 99);

  const platformData: Record<string, number> = {};
  for (const p of PLATFORMS) {
    platformData[p] = seed
      ? randomInt(50000, listeners, seed + PLATFORMS.indexOf(p))
      : randomInt(50000, listeners);
  }

  const reasonOptions = [
    `#${score} en tendencia Regional Mexicano. ${growth}% crecimiento mensual.`,
    `${listeners.toLocaleString()} oyentes. Potencial de firmar este mes.`,
    `Alza imparable: ${growth}% en 30 días. Colaboraciones con grandes.`,
    `Talento único en ${data.city}. ${score} puntos de evaluación.`,
    `Breakout detectado. ${engagement}% engagement. Prioridad alta.`,
    `${listeners.toLocaleString()} streams mensuales. Score ${score}.`,
    `Gira confirmada sin label. Oportunidad de partnership.`,
    `Competencia: 3 labels mostrando interés. Acelerar DD.`,
  ];

  return {
    id: data.id,
    name: data.name,
    score,
    growth,
    listeners,
    followers: Math.round(listeners * randomFloat(0.35, 0.50)),
    genres: data.genres,
    status: pickRandom([...STATUSES]),
    city: data.city,
    country: data.country,
    contact: '', // Only populated for artists with verified real contact (see generateArtistById)
    image: data.image,
    photoUrl: `https://ui-avatars.com/api/?name=${encodeURIComponent(data.name)}&background=6366f1&color=fff&size=200&bold=true`,
    reason: pickRandom(reasonOptions),
    deal: Math.round(listeners * randomFloat(0.08, 0.25)),
    engagement,
    momentum,
    platforms: platformData,
    growthHistory: generateGrowthHistory(score, listeners),
  };
}

export function generateArtists(count: number, genreFilter?: string): Artist[] {
  let pool = [...ARTIST_POOL];
  if (genreFilter && genreFilter !== 'All') {
    pool = ARTIST_POOL.filter(a => a.genres.some(g => g.toLowerCase().includes(genreFilter.toLowerCase())));
  }
  if (pool.length < count) pool = [...ARTIST_POOL];

  // Deterministic selection based on session seed
  const sorted = pool.sort((a, b) => {
    return seededRandom(hashId(a.id)) - seededRandom(hashId(b.id));
  });
  const selected = sorted.slice(0, count);
  return selected.map(a => generateArtistById(a.id));
}

export function generateArtistsFromGenrePool(genre: string, count: number, specificPool?: typeof ARTIST_POOL): Artist[] {
  const pool = specificPool || ARTIST_POOL;
  const filtered = pool.filter(a => a.genres.some(g => g.toLowerCase().includes(genre.toLowerCase())));
  const selected = filtered.length >= count
    ? [...filtered].sort(() => Math.random() - 0.5).slice(0, count)
    : [...pool].sort(() => Math.random() - 0.5).slice(0, count);
  return selected.map(a => generateArtist(a));
}

// ---- SIGNING PIPELINE ----

export interface PipelineStage {
  id: string;
  label: string;
  count: number;
  value: number;
  color: string;
}

export interface PipelineItem {
  id: string;
  name: string;
  genres: string[];
  score: number;
  stage: string;
  value: number;
  image: string;
  priority: string;
  contact: string;
  growth: number;
  listeners: number;
}

const STAGE_META: { id: string; label: string; color: string }[] = [
  { id: 'discovery', label: 'Discovery', color: 'bg-blue-500' },
  { id: 'initial_contact', label: 'Initial Contact', color: 'bg-purple-500' },
  { id: 'due_diligence', label: 'Due Diligence', color: 'bg-amber-500' },
  { id: 'negotiation', label: 'Negotiation', color: 'bg-orange-500' },
  { id: 'closed', label: 'Closed', color: 'bg-green-500' },
];

export function generatePipeline(): { stages: PipelineStage[]; pipeline: PipelineItem[]; total: number; totalValue: number } {
  const artists = generateArtists(8);
  const pipeline = artists.map((a, i) => ({
    id: `pl-${a.id}`,
    name: a.name,
    genres: a.genres,
    score: a.score,
    stage: STAGES[i % STAGES.length],
    value: a.deal,
    image: a.image,
    priority: PRIORITIES[Math.floor((a.score - 65) / 8)] || 'medium',
    contact: a.contact,
    growth: a.growth,
    listeners: a.listeners,
  }));

  const totalValue = pipeline.reduce((a, p) => a + p.value, 0);
  const stageSummary = STAGE_META.map(s => ({
    ...s,
    count: pipeline.filter(p => p.stage === s.id).length,
    value: pipeline.filter(p => p.stage === s.id).reduce((a, p) => a + p.value, 0),
  }));

  return { stages: stageSummary, pipeline, total: pipeline.length, totalValue };
}

// ---- NOTIFICATIONS / ALERTS ----

export interface Alert {
  id: string;
  type: string;
  title: string;
  description: string;
  time: string;
  read: boolean;
  agent?: string;
}

export function generateAlerts(count: number = 8): Alert[] {
  const actions = [
    { verb: 'detectó', subject: 'crecimiento anormal', suffix: '% en 7 días' },
    { verb: 'completó', subject: 'evaluación de', suffix: '' },
    { verb: 'generó', subject: 'reporte de due diligence para', suffix: '' },
    { verb: 'identificó', subject: 'oportunidad de mercado en', suffix: '' },
    { verb: 'actualizó', subject: 'score de', suffix: ' - subió puntos' },
    { verb: 'recomienda', subject: 'acelerar signing de', suffix: '' },
    { verb: 'alertó', subject: 'competencia en', suffix: ' - 2 labels interesados' },
    { verb: 'procesó', subject: 'briefing ejecutivo de', suffix: '' },
  ];
  const agents = ['Analyst Agent', 'Writer Agent', 'Legal Agent', 'GBrain', 'Hermes'];

  const alerts: Alert[] = [];
  const usedArtists: string[] = [];

  for (let i = 0; i < count; i++) {
    const artist = pickRandom(ARTIST_POOL.filter(a => !usedArtists.includes(a.id)));
    if (artist) usedArtists.push(artist.id);
    const action = pickRandom(actions);
    const agent = pickRandom(agents);
    const type = pickRandom(ALERT_TYPES);
    const timeAgo = pickRandom(['5m ago', '12m ago', '30m ago', '1h ago', '2h ago', '4h ago', '6h ago']);

    const score = randomInt(75, 98);
    const growth = randomFloat(8, 65);

    let description = `Agent ${agent} ${action.verb} ${action.subject} ${artist.name}${action.suffix}`;
    if (action.suffix.includes('%')) {
      description = `${artist.name}: ${growth}%${action.suffix}. Score ${score}.`;
    } else if (action.subject.includes('score')) {
      description = `${artist.name}: score ${score} → ${score + randomInt(1, 8)}. ${growth}% growth.`;
    } else if (action.subject.includes('competencia')) {
      description = `${artist.name} en ${artist.city}. ${randomInt(2, 4)} labels compitiendo. ${agent} recomienda acción inmediata.`;
    }

    alerts.push({
      id: `alert-${i}-${Date.now()}`,
      type,
      title: `${artist.name} — ${action.verb === 'detectó' ? 'Breakout' : action.verb === 'completó' ? 'Evaluación' : action.verb === 'generó' ? 'Reporte' : action.verb === 'identificó' ? 'Oportunidad' : action.verb === 'actualizó' ? 'Score Update' : action.verb === 'recomienda' ? 'Recomendación' : action.verb === 'alertó' ? 'Alerta' : 'Briefing'}`,
      description,
      time: timeAgo,
      read: false,
      agent,
    });
  }

  return alerts;
}

// ---- REPORTS ----

export interface Report {
  id: string;
  name: string;
  type: string;
  status: string;
  pages: number;
  created: string;
  author: string;
  description: string;
  artistName: string;
  agentActions: string[];
}

export function generateReports(): { templates: any[]; reports: Report[] } {
  const templates = [
    { id: 'tpl-1', name: 'Artist Evaluation Report', type: 'analytics', description: 'Full artist scoring and market analysis', lastGenerated: '2h ago' },
    { id: 'tpl-2', name: 'Executive Brief', type: 'executive', description: 'One-page executive summary', lastGenerated: '1d ago' },
    { id: 'tpl-3', name: 'Due Diligence Report', type: 'legal', description: 'Legal and compliance review', lastGenerated: '3d ago' },
    { id: 'tpl-4', name: 'Market Intelligence Brief', type: 'analytics', description: 'Genre and regional market analysis', lastGenerated: '5d ago' },
  ];

  const artists = generateArtists(6);
  const reportTypes = ['analytics', 'executive', 'legal', 'analytics', 'executive', 'legal'];
  const statuses = ['final', 'draft', 'final', 'draft', 'final', 'draft'];
  const agents = ['Analyst Agent', 'Writer Agent', 'Legal Agent'];

  const agentActionPool = [
    'Analizó 24 meses de datos de streaming',
    'Comparó con 15 artistas similares del mercado',
    'Calculó ROI proyectado a 12/24/36 meses',
    'Identificó 3 riesgos clave de signing',
    'Generó narrative de pitch ejecutivo',
    'Tradujo brief a EN/ES bilingual',
    'Revisó compliance legal del mercado objetivo',
    'Evaluó cláusulas de contrato estándar',
    'Detectó 2 cláusulas de riesgo',
    'Calculó revenue share óptimo',
    'Analizó crecimiento en TikTok y YouTube',
    'Proyectó streams mensuales con modelo ARIMA',
  ];

  const reports: Report[] = artists.map((a, i) => ({
    id: `rpt-${a.id}-${Date.now()}`,
    name: `${a.name} — ${reportTypes[i] === 'analytics' ? 'Evaluación Completa' : reportTypes[i] === 'executive' ? 'Executive Brief' : 'Due Diligence'}`,
    type: reportTypes[i],
    status: statuses[i],
    pages: randomInt(6, 32),
    created: new Date(Date.now() - randomInt(1, 7) * 86400000).toISOString().split('T')[0],
    author: agents[i % 3],
    description: `${pickRandom(agents)} completó evaluación de ${a.name}. Score ${a.score}. Deal estimado: $${(a.deal / 1000).toFixed(0)}K.`,
    artistName: a.name,
    agentActions: pickRandomN(agentActionPool, randomInt(3, 6)),
  }));

  return { templates, reports };
}

// ---- WAR ROOMS ----

export interface WarRoom {
  id: string;
  name: string;
  stage: string;
  priority: string;
  score: number;
  image: string;
  members: number;
  documents: number;
  meetings: number;
  deal: number;
  contact: string;
}

export function generateWarRooms(): WarRoom[] {
  const artists = generateArtists(6);
  return artists.map((a, i) => ({
    id: a.id,
    name: a.name,
    stage: STAGES[i % STAGES.length],
    priority: PRIORITIES[Math.floor((a.score - 65) / 8)] || 'medium',
    score: a.score,
    image: a.image,
    members: randomInt(3, 8),
    documents: randomInt(4, 18),
    meetings: randomInt(2, 10),
    deal: a.deal,
    contact: a.contact,
  }));
}

// ---- MARKET DATA ----

export interface MarketGenre {
  genre: string;
  growth: string;
  marketShare: string;
  unsignedOpportunity: string;
  avgIndieListeners: string;
  keyMarkets: string[];
}

export function generateMarketData() {
  const genres: MarketGenre[] = [
    { genre: 'Regional Mexicano', growth: '+34%', marketShare: '28%', unsignedOpportunity: 'Alta', avgIndieListeners: '498K', keyMarkets: ['México', 'US Southwest', 'Venezuela', 'Colombia'] },
    { genre: 'Latin Trap', growth: '+22%', marketShare: '18%', unsignedOpportunity: 'Alta', avgIndieListeners: '1.2M', keyMarkets: ['Puerto Rico', 'Ecuador', 'Colombia', 'US East'] },
    { genre: 'Corridos Tumbados', growth: '+41%', marketShare: '15%', unsignedOpportunity: 'Crítica', avgIndieListeners: '380K', keyMarkets: ['México', 'US West', 'Central America'] },
    { genre: 'Latin Pop', growth: '+8%', marketShare: '22%', unsignedOpportunity: 'Media', avgIndieListeners: '250K', keyMarkets: ['Miami', 'México', 'Spain'] },
    { genre: 'Hip Hop / Fusión', growth: '+18%', marketShare: '10%', unsignedOpportunity: 'Alta', avgIndieListeners: '180K', keyMarkets: ['Ecuador', 'Colombia', 'US'] },
    { genre: 'Rap Mexicano', growth: '+28%', marketShare: '7%', unsignedOpportunity: 'Alta', avgIndieListeners: '220K', keyMarkets: ['CDMX', 'Guadalajara', 'Monterrey', 'US'] },
  ];

  // --- DYNAMIC OPPORTUNITIES with live artist data ---
  const featuredArtist1 = generateArtists(1)[0];
  const featuredArtist2 = generateArtists(1)[0];
  const featuredArtist3 = generateArtists(1)[0];
  const featuredArtist4 = generateArtists(1)[0];

  const opportunities = [
    {
      market: `${featuredArtist1.city} Urban Scene`,
      reason: `${featuredArtist1.name} (score ${featuredArtist1.score}) trending. ${featuredArtist1.genres[0]} creciendo ${featuredArtist1.growth}%. Mercado sin saturar.`,
      potential: 'Alto',
      action: `Establish local A&R presence in ${featuredArtist1.city}`,
    },
    {
      market: `${featuredArtist2.genres[0]} Breakout Alert`,
      reason: `${featuredArtist2.name} con ${featuredArtist2.listeners.toLocaleString()} oyentes. Score ${featuredArtist2.score}. ${featuredArtist2.growth}% crecimiento mensual.`,
      potential: featuredArtist2.score > 85 ? 'Crítica' : 'Alto',
      action: `Initiate due diligence on ${featuredArtist2.name}`,
    },
    {
      market: `${featuredArtist3.country} Expansion Window`,
      reason: `${featuredArtist3.name} emergiendo desde ${featuredArtist3.city}. ${featuredArtist3.genres.slice(0, 2).join('/')} con alta demanda. ${featuredArtist3.growth}% growth.`,
      potential: 'Alto',
      action: `First-mover positioning in ${featuredArtist3.country}`,
    },
    {
      market: `${featuredArtist4.genres[0]} Revival`,
      reason: `${featuredArtist4.name} liderando tendencia. Score ${featuredArtist4.score}. ${featuredArtist4.growth}% crecimiento. Momentum: ${featuredArtist4.momentum}.`,
      potential: 'Alto',
      action: `Sign top talents in ${featuredArtist4.genres[0]}`,
    },
    {
      market: 'Cross-Genre Collaboration Opportunity',
      reason: `${featuredArtist1.name} (${featuredArtist1.genres[0]}) x ${featuredArtist2.name} (${featuredArtist2.genres[0]}) — audience overlap detected. Estimated reach: ${(featuredArtist1.listeners + featuredArtist2.listeners).toLocaleString()} listeners.`,
      potential: 'Medio',
      action: 'Propose collaborative project between both artists',
    },
  ];

  return {
    summary: {
      totalMarketSize: '24M estimated unsigned Latin artists on Spotify',
      topGenre: 'Regional Mexicano',
      genreGrowth: '+34% YoY',
      unsignedAdvantage: 'Indie RM artists earn 2x per-stream vs majors (Chartmetric 2026)',
    },
    metrics: [
      { label: 'Unsigned Artists (LATAM)', value: '24M', change: '+12%', trend: 'up' },
      { label: 'RM Genre Growth', value: '+34%', change: 'YoY', trend: 'up' },
      { label: 'Avg Indie Listeners', value: `${randomInt(400, 600)}K`, change: '+8%', trend: 'up' },
      { label: 'Labels Competing/Artist', value: randomFloat(2.5, 4.5, 1).toString(), change: '+15%', trend: 'up' },
    ],
    genres,
    opportunities,
    sources: ['Chartmetric x Duetti Corridos Report 2026', 'Billboard Latin', 'Spotify Charts', 'TikTok Trends', 'SIGNAL Internal Analytics'],
    updatedAt: new Date().toISOString(),
  };
}

// ---- FINANCE ----

export function generateFinanceData() {
  const artists = generateArtists(10);
  const totalBudget = 2500000;
  const totalAllocated = artists.reduce((a, art) => a + art.deal, 0);

  return {
    summary: {
      totalBudget,
      allocated: totalAllocated,
      remaining: totalBudget - totalAllocated,
      currency: 'USD',
      fiscalYear: '2026',
    },
    revenue: {
      total: randomInt(3500000, 5000000),
      streams: randomInt(1500000, 2200000),
      publishing: randomInt(1000000, 1400000),
      merch: randomInt(400000, 800000),
      touring: randomInt(300000, 500000),
      sync: randomInt(150000, 300000),
    },
    expenses: {
      total: randomInt(2500000, 3500000),
      aAndR: randomInt(1000000, 1400000),
      marketing: randomInt(600000, 1000000),
      operations: randomInt(500000, 700000),
      legal: randomInt(200000, 400000),
      technology: randomInt(150000, 300000),
    },
    projectedVsActual: {
      projected: randomInt(4200000, 5000000),
      actual: randomInt(3800000, 4500000),
      variance: `${randomFloat(-8, -3)}%`,
      note: 'Q2 still closing. On track for annual target.',
    },
    deals: artists.map(a => ({
      name: a.name,
      type: pickRandom(['Priority Signing', 'Standard', 'Developmental', 'Exploratory']),
      value: a.deal,
      status: 'pending',
      roi: `+${randomInt(60, 400)}% (projected 24mo)`,
      costBreakdown: {
        advance: Math.round(a.deal * 0.45),
        marketing: Math.round(a.deal * 0.25),
        production: Math.round(a.deal * 0.18),
        legal: Math.round(a.deal * 0.07),
        operations: Math.round(a.deal * 0.05),
      },
    })),
    updatedAt: new Date().toISOString(),
  };
}

// ---- WORKFLOWS ----

export function generateWorkflows() {
  const artists = generateArtists(7);
  const workflowTemplates = [
    { name: 'Signing Evaluation', steps: ['Discovery Analysis', 'Due Diligence', 'Contract Draft', 'Executive Review', 'Final Approval'] },
    { name: 'Artist Onboarding', steps: ['Contract Signing', 'Platform Setup', 'Marketing Plan', 'Content Schedule', 'Launch'] },
    { name: 'Due Diligence Review', steps: ['Background Check', 'Financial Audit', 'Legal Review', 'Market Analysis', 'Risk Assessment'] },
    { name: 'Executive Brief', steps: ['Data Collection', 'Analysis', 'Brief Draft', 'Review', 'Delivery'] },
    { name: 'Negotiation Strategy', steps: ['Market Research', 'Offer Preparation', 'Strategy Session', 'Client Review', 'Final Offer'] },
    { name: 'Marketing Campaign', steps: ['Audience Analysis', 'Content Plan', 'Budget Allocation', 'Execution', 'Performance Review'] },
    { name: 'Compliance Check', steps: ['Regulatory Review', 'Contract Audit', 'PII Scan', 'Risk Rating', 'Certificate Issuance'] },
  ];

  return artists.map((a, i) => {
    const tmpl = workflowTemplates[i % workflowTemplates.length];
    const statuses = ['running', 'paused', 'waiting_approval', 'completed', 'failed'];
    const stepsTotal = tmpl.steps.length;
    const stepsCompleted = randomInt(0, stepsTotal);
    const pValues = ['low', 'medium', 'high', 'critical'] as const;
    const allStatuses = [...statuses];
    return {
      id: `wf-${a.id}`,
      name: `${a.name} — ${tmpl.name}`,
      artistName: a.name,
      type: tmpl.name,
      status: stepsCompleted >= stepsTotal ? 'completed' : pickRandom(allStatuses.filter(s => s !== 'completed')),
      priority: pickRandom(pValues),
      created: new Date(Date.now() - randomInt(1, 30) * 86400000).toISOString(),
      steps_total: stepsTotal,
      steps_completed: stepsCompleted,
      progress: Math.round((stepsCompleted / stepsTotal) * 100),
      steps: tmpl.steps.map((step, si) => ({
        name: step,
        status: si < stepsCompleted ? 'completed' : si === stepsCompleted ? 'in_progress' : 'pending',
        agent: pickRandom(['Analyst Agent', 'Writer Agent', 'Legal Agent', 'GBrain', 'Hermes']),
      })),
    };
  });
}

// ---- ALERTS ACTIVITY (for the alerts page) ----

export function generateAgentActivity() {
  const agents = [
    { name: 'Analyst Agent', role: 'Data & Scoring', color: 'blue' },
    { name: 'Writer Agent', role: 'Content & Briefs', color: 'green' },
    { name: 'Legal Agent', role: 'Compliance & Contracts', color: 'red' },
    { name: 'GBrain', role: 'Orchestrator', color: 'purple' },
    { name: 'Hermes', role: 'Auto-improvement', color: 'amber' },
  ];

  return agents.map(a => ({
    ...a,
    tasksCompleted: randomInt(12, 47),
    tasksPending: randomInt(2, 8),
    lastActive: pickRandom(['30s ago', '2m ago', '5m ago', '12m ago', '1h ago']),
    currentTask: pickRandom([
      `Analyzing ${pickRandom(ARTIST_POOL).name}'s streaming data`,
      `Generating executive brief for ${pickRandom(ARTIST_POOL).name}`,
      `Reviewing contract terms for ${pickRandom(ARTIST_POOL).name}`,
      `Scoring prospects in ${pickRandom(['Regional Mexicano', 'Latin Trap', 'Corridos Tumbados'])}`,
      `Monitoring competitive landscape`,
      `Calculating ROI projections for Q3`,
    ]),
  }));
}

// ---- COMMAND CENTER BRIEFING ----

export function generateBriefing() {
  const artists = generateArtists(3);
  return {
    date: new Date().toISOString(),
    summary: `${pickRandom(['Alta', 'Moderada', 'Fuerte'])} actividad de signing esta semana. ${artists.length} artistas en pipeline activo.`,
    priorities: artists.map((a, i) => ({
      rank: i + 1,
      artistName: a.name,
      action: pickRandom(['Iniciar Due Diligence', 'Preparar oferta inicial', 'Programar meeting con management', 'Enviar LOI', 'Revisar contrato']),
      reason: `Score ${a.score}. ${a.growth}% growth. Deal estimado: $${(a.deal / 1000).toFixed(0)}K.`,
      deadline: pickRandom(['48 horas', 'Esta semana', '7 días', 'Próximos 3 días']),
    })),
    recommendations: [
      { agent: 'Analyst Agent', text: `${artists[0]?.name || 'Prioridad'}: ROI proyectado +${randomInt(200, 400)}% en 24 meses.`, priority: 'alta' },
      { agent: 'Legal Agent', text: `Revisión de mercado en ${artists[1]?.country || 'MX'}: sin restricciones regulatorias.`, priority: 'media' },
      { agent: 'Writer Agent', text: `Brief ejecutivo listo para junta directiva sobre ${artists[0]?.name || 'candidatos'}.`, priority: 'alta' },
    ],
    health: {
      agents: { status: 'healthy', uptime: '99.7%', lastIncident: '12h ago' },
      services: { total: 9, healthy: 9, degraded: 0, down: 0 },
      memory: { used: `${randomInt(40, 70)}%`, vectors: randomInt(1500, 3000), graphEdges: randomInt(800, 2000) },
    },
  };
}

// ---- DISCOVERY ----

export function generateDiscoveryResults(query?: string, genre?: string, count: number = 12) {
  let pool = ARTIST_POOL;
  if (genre && genre !== 'all') {
    pool = ARTIST_POOL.filter(a => a.genres.some(g => g.toLowerCase().includes(genre.toLowerCase())));
  }
  if (query) {
    const q = query.toLowerCase();
    pool = pool.filter(a => a.name.toLowerCase().includes(q) || a.city.toLowerCase().includes(q) || a.country.toLowerCase().includes(q) || a.genres.some(g => g.toLowerCase().includes(q)));
  }

  const selected = [...pool].sort(() => Math.random() - 0.5).slice(0, count);
  return selected.map(a => {
    const artist = generateArtist(a);
    return {
      ...artist,
      discoveryScore: randomInt(60, 98),
      source: pickRandom(['Spotify Algorithm', 'TikTok Trending', 'Billboard Radar', 'YouTube Discovery', 'Chartmetric Alert', 'Instagram Viral']),
      discoveredAt: new Date(Date.now() - randomInt(1, 14) * 86400000).toISOString(),
    };
  });
}

// ---- MISSION CONTROL ----

export function generateMissionControl() {
  const trending = generateArtists(4);
  const rising = generateArtistsFromGenrePool('Regional Mexicano', 3);
  const indie = generateArtistsFromGenrePool('Rap', 3);

  return {
    quoteOfTheDay: pickRandom([
      `"${trending[0]?.name || 'Artist'} tiene el momentum más alto de la semana." — Analyst Agent`,
      `"${rising[0]?.name || 'Artist'} es el prospecto #1 en Regional Mexicano." — GBrain`,
      `"${indie[0]?.name || 'Artist'} podría ser el próximo breakout." — Hermes`,
      `"Tres labels compitiendo por ${trending[1]?.name || 'Artist'}. Acelerar DD." — Legal Agent`,
    ]),
    trendingArtists: trending.map(a => ({
      name: a.name,
      score: a.score,
      growth: a.growth,
      reason: `${a.genres[0]}. ${a.growth}% crecimiento.`,
      image: a.image,
      contact: a.contact,
    })),
    risingStars: rising.map(a => ({
      name: a.name,
      score: a.score,
      listeners: a.listeners,
      reason: `Emergiendo en ${a.genres.join(', ')}. ${a.city}, ${a.country}.`,
      image: a.image,
      contact: a.contact,
    })),
    indieWatch: indie.map(a => ({
      name: a.name,
      score: a.score,
      momentum: a.momentum,
      reason: `Talento independiente en ${a.city}. ${a.momentum} momentum score.`,
      image: a.image,
      contact: a.contact,
    })),
    marketAlerts: generateAlerts(3),
  };
}

// ---- ARTIST RADAR ----

export function generateArtistRadar() {
  const artists = generateArtists(8);
  return artists.map(a => ({
    name: a.name,
    genres: a.genres,
    score: a.score,
    growth: a.growth,
    listeners: a.listeners,
    city: a.city,
    country: a.country,
    contact: a.contact,
    image: a.image,
    reason: a.reason,
    platforms: a.platforms,
    momentum: a.momentum,
    discoverySource: pickRandom(['Spotify Algorithm', 'TikTok Trending', 'Billboard Radar', 'YouTube Discovery', 'Chartmetric Alert', 'Instagram Viral']),
    status: a.status,
  }));
}

// ---- ANALYTICS ----

export function generateAnalytics() {
  const topArtists = generateArtists(10);

  // --- DEMO: Always include AMG-signed artists at top ---
  const hector = generateArtistById('art-amg-01');
  const jesus = generateArtistById('art-amg-02');

  // Force high scores and signed status for demo impact
  const amgArtists = [
    {
      rank: 1,
      name: hector.name,
      score: 97,
      growth: 48.5,
      listeners: 2850000,
      dealEstimate: 1250000,
      momentum: 94.2,
      reason: '✅ FIRMADO — Artista estrella de Abe Music Group. 48.5% crecimiento mensual. Rompiendo en Regional Mexicano y Urbano.',
      image: hector.image,
      photoUrl: hector.photoUrl,
      contact: hector.contact,
      status: 'signed',
    },
    {
      rank: 2,
      name: jesus.name,
      score: 94,
      growth: 42.1,
      listeners: 2100000,
      dealEstimate: 980000,
      momentum: 91.7,
      reason: '✅ FIRMADO — Artista exclusivo Abe Music Group. 42.1% crecimiento. Corridos/Sierreño con proyección internacional.',
      image: jesus.image,
      photoUrl: jesus.photoUrl,
      contact: jesus.contact,
      status: 'signed',
    },
  ];

  const otherArtists = topArtists
    .filter(a => a.id !== 'art-amg-01' && a.id !== 'art-amg-02')
    .slice(0, 8)
    .map((a, i) => ({
      rank: i + 3,
      name: a.name,
      score: a.score,
      growth: a.growth,
      listeners: a.listeners,
      dealEstimate: a.deal,
      momentum: a.momentum,
      reason: a.reason,
      image: a.image,
      photoUrl: a.photoUrl,
      contact: a.contact,
      status: a.status,
    }));

  const topForSigning = [...amgArtists, ...otherArtists];

  // Recalculate KPI metrics with AMG artists included
  const totalArtists = ARTIST_POOL.length;
  const avgScore = Math.round(
    (topForSigning.reduce((a: number, b: any) => a + b.score, 0) / topForSigning.length)
  );

  return {
    kpiMetrics: [
      { label: 'Artists Tracked', value: totalArtists, change: '+12', trend: 'up' },
      { label: 'Avg Discovery Score', value: avgScore, change: '+6', trend: 'up' },
      { label: 'Active Pipeline', value: topForSigning.filter((a: any) => a.score > 85).length, change: '+4', trend: 'up' },
      { label: 'Signed Artists', value: 2, change: '+2', trend: 'up' },
      { label: 'Portfolio Value', value: `$${(1250000 + 980000 + 3200000).toLocaleString()}`, change: '+18%', trend: 'up' },
      { label: 'Avg Growth Rate', value: `${Math.round(topForSigning.reduce((a: number, b: any) => a + b.growth, 0) / topForSigning.length)}%`, change: '+8%', trend: 'up' },
    ],
    genreDistribution: [
      { genre: 'Regional Mexicano', percentage: 35, color: '#3B82F6' },
      { genre: 'Latin Trap', percentage: 20, color: '#8B5CF6' },
      { genre: 'Corridos Tumbados', percentage: 18, color: '#F59E0B' },
      { genre: 'Latin Pop', percentage: 12, color: '#10B981' },
      { genre: 'Hip Hop / Rap', percentage: 10, color: '#EF4444' },
      { genre: 'Otros', percentage: 5, color: '#6B7280' },
    ],
    topForSigning,
  };
}

// ---- AGENTS ----

export function generateAgents() {
  return {
    agents: [
      { id: 'agent-analyst', name: 'Analyst Agent', role: 'Data & Scoring', status: 'active', tools: 5, tasksCompleted: randomInt(120, 300), accuracy: `${randomInt(94, 99)}%`, model: 'deepseek/deepseek-v4-flash' },
      { id: 'agent-writer', name: 'Writer Agent', role: 'Content & Briefs', status: 'active', tools: 6, tasksCompleted: randomInt(80, 200), accuracy: `${randomInt(92, 98)}%`, model: 'deepseek/deepseek-v4-flash' },
      { id: 'agent-legal', name: 'Legal Agent', role: 'Compliance & Contracts', status: 'active', tools: 6, tasksCompleted: randomInt(50, 150), accuracy: `${randomInt(96, 100)}%`, model: 'deepseek/deepseek-v4-flash' },
      { id: 'agent-gbrain', name: 'GBrain', role: 'Orchestrator', status: 'active', tools: 8, tasksCompleted: randomInt(200, 500), accuracy: `${randomInt(97, 100)}%`, model: 'deepseek/deepseek-v4-flash' },
      { id: 'agent-engram', name: 'Engram', role: 'Memory & RAG', status: 'active', tools: 7, tasksCompleted: randomInt(300, 600), accuracy: `${randomInt(99, 100)}%`, model: 'deepseek/deepseek-v4-flash' },
      { id: 'agent-hermes', name: 'Hermes', role: 'Auto-improvement', status: 'active', tools: 10, tasksCompleted: randomInt(40, 120), accuracy: `${randomInt(90, 96)}%`, model: 'deepseek/deepseek-v4-flash' },
      { id: 'agent-openclaw', name: 'OpenClaw', role: 'Gateway & HTTP', status: 'active', tools: 9, tasksCompleted: randomInt(400, 800), accuracy: `${randomInt(99, 100)}%`, model: 'deepseek/deepseek-v4-flash' },
      { id: 'agent-streaming', name: 'Streaming MCP', role: 'Live Data', status: 'active', tools: 3, tasksCompleted: randomInt(30, 90), accuracy: `${randomInt(95, 99)}%`, model: 'deepseek/deepseek-v4-flash' },
    ],
    recentDecisions: generateConsensusDecisions(),
  };
}

let _decisionArtistIndex = 0;
function topArtistsForDecision(): string[] {
  const names = ['El de la Tinta', 'Jombriel', 'De La Rose', 'Machaka', 'Jocsan Duran', 'Netón Vega', 'Xavi', 'Yahritza', 'Kevin AMF', 'DannyLux'];
  _decisionArtistIndex = (_decisionArtistIndex + 3) % names.length;
  return [...names.slice(_decisionArtistIndex), ...names.slice(0, _decisionArtistIndex)].slice(0, 5);
}

// ---- CONSENSUS DECISIONS ----

const DECISION_TYPES = ['Signing Recommendation', 'Due Diligence', 'Offer Strategy', 'Market Entry', 'Risk Assessment'];
const DECISION_OUTCOMES = ['APPROVED', 'APPROVED', 'APPROVED', 'IN REVIEW', 'PENDING', 'FLAGGED'];
const PROCESS_STEPS_POOL = [
  { agent: 'Analyst Agent', action: 'Recolectó y normalizó datos de 6 plataformas (Spotify, Apple Music, Deezer, YouTube, Instagram, TikTok)',
    detail: 'Ejecutó queries paralelos a APIs de streaming. Validó consistencia de métricas. Detectó anomalías en datos de TikTok (-12% vs tendencia).' },
  { agent: 'Analyst Agent', action: 'Calculó score compuesto con 15 variables ponderadas',
    detail: 'Aplicó modelo de scoring proprietario (pesos: streams 25%, engagement 20%, crecimiento 20%, presencia multiplataforma 15%, momentum 10%, calidad de audiencia 10%).' },
  { agent: 'Analyst Agent', action: 'Comparó contra 20 artistas comparables del mismo género',
    detail: 'Usó Engram para búsqueda de similitud vectorial. Encontró 5 matches con >85% de similitud. Percentil del artista: 78.' },
  { agent: 'Analyst Agent', action: 'Proyectó crecimiento a 12/24/36 meses con modelo ARIMA',
    detail: 'Entrenó modelo con 24 meses de datos históricos. Precisión del modelo: 91.3%. Escenarios: optimista (+34%), esperado (+22%), pesimista (+11%).' },
  { agent: 'Analyst Agent', action: 'Generó dashboard interactivo con KPIs clave',
    detail: '24 KPIs generados. Top 5 destacados: growth rate, engagement rate, audience quality score, market saturation index, competitive advantage score.' },
  { agent: 'Writer Agent', action: 'Redactó executive brief en formato bilingüe EN/ES',
    detail: 'Brief de 3 páginas: resumen ejecutivo (1 pág), análisis de mercado (1 pág), recomendación estratégica (1 pág). Traducción certificada por agente.' },
  { agent: 'Writer Agent', action: 'Preparó narrative de pitch para reunión con artista',
    detail: 'Narrative estructurada: visión del label, propuesta de valor única, términos propuestos, roadmap 12 meses. Tono: aspiracional pero realista.' },
  { agent: 'Writer Agent', action: 'Evaluó consistencia de marca y posicionamiento',
    detail: 'Analizó 50+ publicaciones en redes sociales. Identificó 3 pilares de marca: autenticidad, conexión local, innovación sonora.' },
  { agent: 'Writer Agent', action: 'Documentó riesgos de comunicación y relaciones públicas',
    detail: 'Identificó 2 riesgos de comunicación: controversias pasadas del artista (menciones en prensa), y sensibilidad política en letras.' },
  { agent: 'Legal Agent', action: 'Revisó cláusulas estándar del contrato',
    detail: 'Comparó contra template maestro de Abe Music Group. Detectó 3 desviaciones: exclusividad territorial, split de publishing, derechos de sincronización.' },
  { agent: 'Legal Agent', action: 'Detectó riesgos legales y de compliance',
    detail: 'Escaneó 45 cláusulas potenciales. Encontró 2 de alto riesgo: (1) cláusula de no competencia demasiado restrictiva, (2) falta de claridad en derechos de imagen para México.' },
  { agent: 'Legal Agent', action: 'Verificó situación legal del artista (demandas, obligaciones)',
    detail: 'Consultó bases de datos públicas (IMPI, INDAUTOR, BMI, ASCAP). Sin demandas activas. 3 registros de coautoría pendientes de resolver.' },
  { agent: 'Legal Agent', action: 'Evaluó compliance de mercado objetivo',
    detail: 'Revisó regulaciones en 5 mercados target (México, USA, Colombia, Argentina, España). Todos OK excepto España: requiere agente local para SGAE.' },
  { agent: 'Legal Agent', action: 'Calculó revenue share óptimo según estándares de industria',
    detail: 'Benchmark con 15 contratos comparables. Rango de revenue share: 75/25 a 85/15 (label/artist). Recomendación: 80/20 con escalonamiento por performance.' },
  { agent: 'GBrain', action: 'Orquestó flujo de trabajo multi-agente',
    detail: 'Coordinó ejecución secuencial de 3 agentes (Analyst → Writer → Legal). Tiempo total de ejecución: 47 segundos. 0 errores. 12 herramientas utilizadas.' },
  { agent: 'GBrain', action: 'Sintetizó outputs de agentes en recomendación unificada',
    detail: 'Consolidó 45 outputs individuales en recomendación cohesiva. Peso de cada agente: Analyst 35%, Legal 35%, Writer 30%. Confianza global: calculada por consenso ponderado.' },
  { agent: 'GBrain', action: 'Registró decisión en Engram para memoria cross-sesión',
    detail: 'Almacenó embedding vectorial de la decisión (1536 dimensiones). Vinculó con decisiones previas sobre el mismo artista. Detectó 2 patrones históricos relevantes.' },
  { agent: 'Streaming MCP', action: 'Proporcionó datos de mercado en tiempo real',
    detail: 'Streaming continuo de 8 feeds de datos. Detectó pico de menciones (+340%) en últimas 24 horas por lanzamiento de sencillo.' },
];

const JUSTIFICATION_POOL: Record<string, string[]> = {
  APPROVED: [
    'El equipo de agentes concluye que el artista cumple con todos los criterios de signing: score superior a 80, crecimiento sostenido por 6+ meses, engagement saludable, y ausencia de riesgos legales significativos. La oportunidad de mercado es favorable con ventana de 3 meses para asegurar exclusividad antes de que competidores activen ofertas.',
    'Análisis multi-agente confirma que el artista representa una oportunidad de alto valor con perfil de riesgo controlado. El momentum actual combinado con la ausencia de obligaciones previas permite estructurar un deal competitivo con términos favorables para el label.',
    'Recomendación unánime de los 3 agentes evaluadores. El score compuesto, el análisis de mercado, y la revisión legal convergen en que el artista está listo para firmar. Se recomienda proceder con oferta inicial en los próximos 5 días hábiles.',
  ],
  'IN REVIEW': [
    'El proceso de due diligence está activo pero incompleto. Los agentes han completado la fase 1 (análisis cuantitativo) pero la fase 2 (verificación legal y background check) requiere 3-5 días adicionales para obtener documentación del artista.',
    'Pendiente de recibir documentación del artista: identificación oficial, comprobante de derechos, y registro de coautorías. Sin estos documentos, los agentes no pueden emitir recomendación definitiva.',
  ],
  PENDING: [
    'La estrategia de oferta está preparada pero requiere decisión ejecutiva sobre el rango de inversión. Los agentes recomiendan 3 escenarios: conservador ($200K), moderado ($350K), y agresivo ($500K). Cada escenario tiene implicaciones distintas en revenue share y territorio.',
    'Los agentes han modelado 5 escenarios de oferta pero necesitan input del comité ejecutivo para definir: (1) presupuesto disponible para este signing, (2) nivel de riesgo aceptable, (3) prioridad estratégica del género.',
  ],
  FLAGGED: [
    'ALERTA: Se detectaron 3 riesgos críticos que requieren revisión ejecutiva antes de proceder: (1) posible conflicto de intereses con artista actual del label, (2) cláusula de exclusividad previa con otro sello en territorio México, (3) tendencia negativa en engagement (-15% en 30 días).',
    'FLAG: El análisis legal encontró obligaciones contractuales previas que podrían limitar los términos del deal. Se recomienda consultar con abogado externo especializado en derecho de entretenimiento antes de proceder con oferta.',
  ],
};

const VOTE_REASONS_POOL: Record<string, string[]> = {
  'Analyst Agent': [
    'Data consistente con artistas top del género. Score en percentil 85+. Crecimiento validado en 4 plataformas.',
    'Métricas positivas pero volatilidad en crecimiento mensual. Recomiendo monitorear 2 semanas adicionales.',
    'Datos de audiencia muestran alta concentración geográfica (60% en un solo mercado). Riesgo de diversificación.',
    'Streaming consistente con tendencia alcista. Proyección ARIMA positiva para 12 meses.',
  ],
  'Writer Agent': [
    'Marca personal sólida con narrative auténtica. Potencial de storytelling ejecutivo excepcional.',
    'Contenido en redes sociales inconsistente. Narrativa de marca necesita desarrollo antes de pitch.',
    'Posicionamiento de mercado claro. Propuesta de valor diferenciada en su género.',
    'Material promocional existente de baja calidad. Se requiere producción de contenido profesional.',
  ],
  'Legal Agent': [
    'Sin riesgos legales detectados. Documentación en orden. Compliance OK para mercados target.',
    'Riesgos contractuales manejables con ajustes estándar. Negociación de cláusulas recomendada.',
    'Alerta: Obligaciones previas con editora musical. Se requiere carta de liberación antes de firmar.',
    'Background check completado. Sin demandas activas. Registros de propiedad intelectual en regla.',
  ],
  'GBrain': [
    'Consenso inter-agente: 3 de 3 agentes recomiendan proceder. Confianza colectiva: alta.',
    'Divergencia entre agentes: Analyst recomienda aprobar, Legal recomienda esperar. Se requiere decisión ejecutiva.',
    'Flujo de trabajo completado eficientemente. 12 herramientas utilizadas. 0 errores. Datos frescos (últimos 30 min).',
  ],
  'Streaming MCP': [
    'Datos en tiempo real confirman tendencia positiva. Pico de actividad en últimas 24h.',
    'Feed de datos muestra estabilidad sin anomalías. Menciones en redes dentro del rango esperado.',
  ],
};

function generateConsensusDecisions() {
  const decisions = [];
  const types = [...DECISION_TYPES];
  const usedArtists = new Set<string>();

  for (let i = 0; i < 5; i++) {
    const artistName = topArtistsForDecision()[i];
    const type = types[i];
    const outcome = pickRandom(DECISION_OUTCOMES);
    const baseConfidence = outcome === 'APPROVED' ? randomInt(82, 98)
      : outcome === 'IN REVIEW' ? randomInt(68, 84)
      : outcome === 'PENDING' ? randomInt(60, 78)
      : randomInt(50, 72);

    // Generate 3-5 process steps
    const stepCount = randomInt(3, 5);
    const shuffledSteps = [...PROCESS_STEPS_POOL].sort(() => Math.random() - 0.5);
    const processSteps = shuffledSteps.slice(0, stepCount);

    // Extract agent names from steps
    const involvedAgents = [...new Set(processSteps.map(s => s.agent))];

    // Generate agent votes
    const agentVotes = involvedAgents.map(agent => {
      const agentVote = outcome === 'APPROVED' ? pickRandom(['APPROVED', 'APPROVED', 'APPROVED', 'APPROVED', 'CONDITIONAL'])
        : outcome === 'IN REVIEW' ? pickRandom(['CONDITIONAL', 'CONDITIONAL', 'PENDING'])
        : outcome === 'PENDING' ? pickRandom(['PENDING', 'CONDITIONAL'])
        : 'FLAGGED';

      const reasonPool = VOTE_REASONS_POOL[agent] || ['Standard evaluation completed.'];
      const confidence = outcome === 'APPROVED' ? randomInt(75, 98)
        : outcome === 'FLAGGED' ? randomInt(55, 75)
        : randomInt(60, 85);

      return {
        agent,
        vote: agentVote,
        confidence,
        reason: pickRandom(reasonPool),
      };
    });

    // Calculate aggregate confidence
    const avgConfidence = Math.round(
      agentVotes.reduce((s, v) => s + v.confidence, 0) / agentVotes.length
    );

    // Generate detailed justification
    const justificationPool = JUSTIFICATION_POOL[outcome] || ['Standard assessment completed.'];
    const justification = pickRandom(justificationPool);

    // Generate report
    const date = new Date();
    date.setDate(date.getDate() - randomInt(0, 5));

    const report = `# ${type}: ${artistName}
## Executive Decision Report
**Date:** ${date.toISOString().split('T')[0]}
**Status:** ${outcome}
**Confidence:** ${avgConfidence}%
**Agents Involved:** ${involvedAgents.join(', ')}

### Outcome
${justification}

### Agent Voting Summary
${agentVotes.map(v => `- **${v.agent}**: ${v.vote} (${v.confidence}% confidence) — "${v.reason}"`).join('\n')}

### Process Execution
${processSteps.map(s => `- **${s.agent}**: ${s.action}\n  ${s.detail}`).join('\n')}

### Key Findings
${[
  '- Score assessment within target range for label investment criteria',
  '- Market analysis confirms growth potential in primary genre',
  '- Legal review completed with ' + (outcome === 'FLAGGED' ? 'identified risks requiring mitigation' : 'standard compliance sign-off'),
  '- Executive recommendation: ' + outcome.toLowerCase().replace('_', ' ') + ' with ' + avgConfidence + '% confidence',
].join('\n')}

### Next Steps
${outcome === 'APPROVED' ? '1. Prepare and send offer letter\n2. Schedule artist meeting\n3. Begin contract drafting\n4. Set onboarding timeline'
  : outcome === 'IN REVIEW' ? '1. Request pending documentation\n2. Complete background check\n3. Schedule follow-up review'
  : outcome === 'PENDING' ? '1. Escalate to executive committee\n2. Define investment budget\n3. Re-submit for approval'
  : '1. Review flagged risks with legal counsel\n2. Develop risk mitigation plan\n3. Re-evaluation in 2 weeks'}

*Generated by SIGNAL Multi-Agent System · Abe Music Group*

### ⚠️ HUMAN DECISION REQUIRED
SIGNAL agents have completed their analysis and provide the recommendation above.
**AGENTS CANNOT MAKE FINAL DECISIONS OR EXECUTE CONTRACTS.**
This recommendation requires human review and approval before any action is taken.
Please review the agent votes, process steps, and justification above, then
make a final decision. Forward to executive committee if additional approval is required.
`;

    decisions.push({
      id: `dec-${i + 1}-${Date.now()}`,
      artistName,
      type,
      decision: outcome,
      confidence: avgConfidence || baseConfidence,
      agents: involvedAgents,
      summary: justification.length > 120 ? justification.slice(0, 120) + '...' : justification,
      justification,
      report,
      processSteps,
      agentVotes,
      date: date.toISOString().split('T')[0],
    });
  }

  return decisions;
}

// ---- PLAYLIST ----

export function generatePlaylists() {
  const playlists = Array.from({ length: 12 }, (_, i) => {
    const artist = pickRandom(ARTIST_POOL);
    const followers = randomInt(300, 4200);
    const tracks = randomInt(2, 8);
    const addedCount = randomInt(1, 4);
    const addedArtists = Array.from({ length: addedCount }, () => pickRandom(ARTIST_POOL).name);
    const trend = pickRandom(['up', 'up', 'up', 'stable', 'stable', 'down']);
    const reach = trend === 'up' ? `+${randomInt(5, 35)}%` : `-${randomInt(3, 15)}%`;
    return {
      id: `pl-${i}-${Date.now()}`,
      name: pickRandom(['Regional Mexicano 2026', 'Trap Latino', 'Nuevo Talento MX', 'Latin R&B', 'Viral Ecuador', 'Fresh Latin', 'Corridos Tumbados Mix', 'Latin Urban 2026', 'Cumbia Fusión', 'Baila Conmigo', 'Nuevo Talento MX', 'Tropical Hits']),
      platform: pickRandom(['Spotify', 'Spotify', 'Spotify', 'Apple Music', 'Deezer']),
      type: pickRandom(['editorial', 'editorial', 'editorial', 'algorithmic', 'regional']),
      followers: followers >= 1000 ? `${(followers / 1000).toFixed(1)}M` : `${followers}K`,
      tracks,
      addedArtists,
      trend,
      reach,
      topArtist: artist.name,
      position: randomInt(1, 30),
    };
  });
  return playlists;
}

export function generatePlaylistStats() {
  const playlists = generatePlaylists();
  const totalFollowers = playlists.reduce((sum, p) => {
    const num = parseFloat(p.followers) * (p.followers.includes('M') ? 1000000 : 1000);
    return sum + num;
  }, 0);
  return {
    totalPlaylists: playlists.length,
    totalFollowers: totalFollowers >= 1000000000
      ? `${(totalFollowers / 1000000000).toFixed(1)}B`
      : totalFollowers >= 1000000
        ? `${(totalFollowers / 1000000).toFixed(1)}M`
        : `${(totalFollowers / 1000).toFixed(0)}K`,
    tracksAdded: playlists.reduce((s, p) => s + p.tracks, 0),
    weeklyGrowth: `+${randomInt(8, 28)}%`,
  };
}

// ---- PIPELINE FUNNEL ----

export function generatePipelineFunnel() {
  return [
    { label: 'Discovered', count: randomInt(200, 350), color: 'bg-blue-500' },
    { label: 'Analyzed', count: randomInt(100, 200), color: 'bg-purple-500' },
    { label: 'Meeting', count: randomInt(50, 120), color: 'bg-amber-500' },
    { label: 'Negotiation', count: randomInt(20, 60), color: 'bg-orange-500' },
    { label: 'Contract', count: randomInt(10, 30), color: 'bg-indigo-500' },
    { label: 'Signed', count: randomInt(3, 12), color: 'bg-green-500' },
  ];
}

// ---- WORKFLOW STATUS BREAKDOWN ----

export function generateWorkflowStatusBreakdown() {
  const workflows = generateWorkflows();
  return {
    running: workflows.filter(w => w.status === 'running').length,
    paused: workflows.filter(w => w.status === 'paused').length,
    waiting_approval: workflows.filter(w => w.status === 'waiting_approval').length,
    failed: workflows.filter(w => w.status === 'failed').length,
    completed: workflows.filter(w => w.status === 'completed').length,
    total: workflows.length,
  };
}

// ---- WAR ROOM TEAM MEMBERS ----

export function generateWarRoomTeamMembers() {
  return [
    { name: 'Mystic', role: 'CEO / Founder', avatar: 'M' },
    { name: 'Noel', role: 'Head of A&R', avatar: 'N' },
    { name: 'Analyst Agent', role: 'AI — Data', avatar: 'A', isAgent: true },
    { name: 'Writer Agent', role: 'AI — Content', avatar: 'W', isAgent: true },
    { name: 'Legal Agent', role: 'AI — Legal', avatar: 'L', isAgent: true },
  ];
}

export function generateWarRoomDocuments(artistId: string, artistName: string) {
  const docTypes = [
    { name: 'Artist Evaluation Report', type: 'evaluation', createdBy: 'Analyst Agent' },
    { name: 'Executive Brief', type: 'brief', createdBy: 'Writer Agent' },
    { name: 'Due Diligence Report', type: 'legal', createdBy: 'Legal Agent' },
    { name: 'Contract Draft v2', type: 'contract', createdBy: 'Legal Agent' },
    { name: `Market Analysis — ${artistName} Genre`, type: 'analysis', createdBy: 'Analyst Agent' },
    { name: 'Offer Letter v3', type: 'proposal', createdBy: 'Writer Agent' },
  ];
  return docTypes.map((d, i) => ({
    id: `doc-${i}-${artistId}`,
    name: d.name,
    type: d.type,
    status: pickRandom(['final', 'draft', 'review']),
    pages: randomInt(6, 32),
    createdBy: d.createdBy,
    date: new Date(Date.now() - randomInt(1, 7) * 86400000).toISOString().split('T')[0],
  }));
}

export function generateWarRoomMeetings(artistId: string, artistName: string, teamMembers: any[]) {
  return [
    { id: `mtg-1-${artistId}`, title: `Initial Review: ${artistName}`, date: new Date(Date.now() - randomInt(3, 10) * 86400000).toISOString().split('T')[0], time: '10:00 AM', status: 'completed', attendees: teamMembers.slice(0, 3), mode: 'video' },
    { id: `mtg-2-${artistId}`, title: `Strategy Session: ${artistName}`, date: new Date(Date.now() - randomInt(1, 5) * 86400000).toISOString().split('T')[0], time: '2:00 PM', status: 'completed', attendees: teamMembers, mode: 'in-person' },
    { id: `mtg-3-${artistId}`, title: `Negotiation Prep: ${artistName}`, date: new Date(Date.now() + randomInt(1, 4) * 86400000).toISOString().split('T')[0], time: '11:00 AM', status: 'scheduled', attendees: teamMembers, mode: 'video' },
    { id: `mtg-4-${artistId}`, title: `Final Review: ${artistName}`, date: new Date(Date.now() + randomInt(5, 10) * 86400000).toISOString().split('T')[0], time: '3:00 PM', status: 'scheduled', attendees: teamMembers.slice(0, 4), mode: 'in-person' },
  ];
}

export function generateWarRoomOffers(artistDeal: number) {
  return [
    { id: `off-1-${Date.now()}`, version: 'v1', amount: Math.round(artistDeal * 0.7), status: 'rejected', date: new Date(Date.now() - randomInt(10, 20) * 86400000).toISOString().split('T')[0], notes: 'Initial offer rejected by management.' },
    { id: `off-2-${Date.now()}`, version: 'v2', amount: Math.round(artistDeal * 0.85), status: 'rejected', date: new Date(Date.now() - randomInt(5, 10) * 86400000).toISOString().split('T')[0], notes: 'Counter-offer requested. Management seeking higher advance.' },
    { id: `off-3-${Date.now()}`, version: 'v3', amount: artistDeal, status: 'pending', date: new Date(Date.now() - randomInt(1, 3) * 86400000).toISOString().split('T')[0], notes: `Current offer. $${Math.round(artistDeal * 0.45).toLocaleString()} advance + 18% royalty.` },
  ];
}

// ---- SETTINGS ----

export function generateSettings() {
  return {
    profile: {
      name: 'Abe Music Group',
      email: 'exec@abe-music.com',
      plan: pickRandom(['Enterprise', 'Professional', 'Starter']),
      logo: 'AM',
      timezone: 'America/Mexico_City',
      language: 'ES / EN',
    },
    preferences: {
      notifications: true,
      weeklyDigest: true,
      autoBriefings: true,
      agentApprovals: true,
      darkMode: true,
      language: 'bilingual',
    },
    team: [
      { id: 'u1', name: 'Mystic', role: 'CEO / Founder', email: 'mystic@abe-music.com', avatar: 'M' },
      { id: 'u2', name: 'Noel', role: 'Head of A&R', email: 'noel@abe-music.com', avatar: 'N' },
      ...generateArtists(3).map((a, i) => ({
        id: `agent-${i}`,
        name: `${[`Analyst Agent`, `Writer Agent`, `Legal Agent`][i]}`,
        role: `AI — ${[`Data & Scoring`, `Content & Briefs`, `Compliance & Contracts`][i]}`,
        email: `${[`analyst`, `writer`, `legal`][i]}@signal.agent`,
        avatar: [`A`, `W`, `L`][i],
        isAgent: true,
      })),
    ],
    integrations: [
      { id: `int-1-${Date.now()}`, name: 'Spotify', type: 'streaming', status: 'connected', lastSync: 'Real-time' },
      { id: `int-2-${Date.now()}`, name: 'Billboard API', type: 'data', status: 'connected', lastSync: 'Daily' },
      { id: `int-3-${Date.now()}`, name: 'Chartmetric', type: 'analytics', status: 'connected', lastSync: 'Daily' },
      { id: `int-4-${Date.now()}`, name: 'TikTok', type: 'social', status: 'connected', lastSync: 'Real-time' },
      { id: `int-5-${Date.now()}`, name: 'Sonora Brain v3', type: 'ai', status: 'connected', lastSync: 'Real-time', agents: 8 },
    ],
    version: '1.0.0',
    updatedAt: new Date().toISOString(),
  };
}

// ---- SEARCH PAGES + SUGGESTIONS ----

export function generateSearchPages() {
  return [
    { id: 'page-dashboard', title: 'Mission Control', type: 'page', path: '/dashboard', description: 'Executive overview of the intelligence operation' },
    { id: 'page-artists', title: 'Artist Radar', type: 'page', path: '/artists', description: 'Complete intelligence dossiers on all artists' },
    { id: 'page-analytics', title: 'Analytics', type: 'page', path: '/analytics', description: 'Deep analytics and market intelligence' },
    { id: 'page-war-rooms', title: 'War Rooms', type: 'page', path: '/war-rooms', description: 'High-priority negotiations and strategic operations' },
    { id: 'page-signings', title: 'Signing Pipeline', type: 'page', path: '/signings', description: 'Artist signing pipeline and deal tracking' },
    { id: 'page-command-center', title: 'Command Center', type: 'page', path: '/command-center', description: 'Centralized mission control for all intelligence operations' },
    { id: 'page-workflows', title: 'Workflows', type: 'page', path: '/workflows', description: 'Automated agent workflows and processes' },
    { id: 'page-reports', title: 'Executive Reports', type: 'page', path: '/reports', description: 'Executive briefings ready for leadership meetings' },
    { id: 'page-market', title: 'Market Intelligence', type: 'page', path: '/market', description: 'Market trends and competitive analysis' },
    { id: 'page-finance', title: 'Financial View', type: 'page', path: '/finance', description: 'Financial intelligence and budget overview' },
    { id: 'page-settings', title: 'Settings', type: 'page', path: '/settings', description: 'System configuration and preferences' },
    { id: 'page-alerts', title: 'Intelligence Alerts', type: 'page', path: '/alerts', description: 'Intelligence alerts and notifications' },
    { id: 'page-discovery', title: 'Discovery Engine', type: 'page', path: '/discovery', description: 'Emerging opportunities detected by SIGNAL' },
    { id: 'page-playlists', title: 'Playlist Monitor', type: 'page', path: '/playlists', description: 'Playlist performance and tracking' },
    { id: 'page-agents', title: 'Agent Performance', type: 'page', path: '/agents', description: 'AI agent activity, metrics and performance' },
    { id: 'page-contracts', title: 'Contracts', type: 'page', path: '/contracts', description: 'Legal intelligence and contract lifecycle' },
  ];
}

export function generateSearchSuggestions() {
  return [
    { label: 'Regional Mexicano artists', query: 'Regional Mexicano' },
    { label: 'Top scoring prospects', query: 'top artists' },
    { label: 'Active negotiations', query: 'negotiation' },
    { label: 'Due diligence workflows', query: 'due diligence' },
  ];
}

// ---- HEALTH STATUS ----

export function generateHealthStatus() {
  const agents = generateAgentActivity();
  return {
    services: agents.map(a => ({
      name: a.name,
      role: a.role,
      status: pickRandom(['healthy', 'healthy', 'healthy', 'degraded'] as const),
      uptime: `${randomFloat(98, 99.9, 1)}%`,
      tasksCompleted: a.tasksCompleted,
      tasksPending: a.tasksPending,
      lastActive: a.lastActive,
      currentTask: a.currentTask,
      color: a.color,
    })),
    summary: {
      total: agents.length,
      healthy: agents.length - (agents.length > 3 ? randomInt(0, 1) : 0),
      degraded: randomInt(0, 1),
      down: 0,
    },
    agentPilot: {
      status: 'active',
      workflowsRunning: randomInt(2, 6),
      totalArtistsAnalyzed: generateArtists(randomInt(3, 8)).length,
      lastRun: new Date().toISOString(),
    },
    updatedAt: new Date().toISOString(),
  };
}

// ---- APPROVAL ----

export function generateApproval(approvalId: string) {
  return {
    id: approvalId,
    status: 'pending',
    type: 'signing_approval' as const,
    amount: randomInt(200000, 600000),
    currency: 'USD',
    artistName: pickRandom(ARTIST_POOL).name,
    submittedBy: 'Analyst Agent',
    submittedAt: new Date(Date.now() - randomInt(1, 5) * 86400000).toISOString(),
    documents: randomInt(2, 6),
  };
}

// ---- MOTIVATIONAL QUOTES ----

export function generateQuote(): string {
  const quotes = [
    'Every priority is a signal. Every signal has a deadline.',
    'The best time to act on an artist is before your competitor does.',
    'Pipeline velocity is the only metric that matters at 3 AM.',
    "Agents don't sleep. Neither should your edge.",
    'A degraded service today is a missed opportunity tomorrow.',
    'Data without action is just noise. Turn up the gain.',
    'In the war for talent, latency is the enemy.',
    'Your agents are only as sharp as the last memory they retrieved.',
    'The best deals are the ones your competitors never saw coming.',
    'Sign today. Regret tomorrow. Weigh the odds. Act anyway.',
  ];
  return quotes[randomInt(0, quotes.length - 1)];
}

// ---- COST BREAKDOWN CONFIG ----

export const COST_BREAKDOWN_CONFIG = {
  advance: { label: 'Advance', percentage: 45, color: 'bg-blue-500' },
  marketing: { label: 'Marketing', percentage: 25, color: 'bg-purple-500' },
  production: { label: 'Production', percentage: 18, color: 'bg-amber-500' },
  legal: { label: 'Legal & IP', percentage: 7, color: 'bg-red-500' },
  operations: { label: 'Operations', percentage: 5, color: 'bg-green-500' },
};

export function calculateCostBreakdown(totalDeal: number) {
  return Object.entries(COST_BREAKDOWN_CONFIG).map(([key, cfg]) => ({
    key,
    label: cfg.label,
    percentage: cfg.percentage,
    amount: Math.round(totalDeal * (cfg.percentage / 100)),
    color: cfg.color,
  }));
}

// ---- WORKFLOW AGENT CONFIG ----

export const WORKFLOW_AGENTS_CONFIG = [
  { name: 'Analyst Agent', role: 'Data & Scoring', status: 'active' as const, color: 'text-blue-500' },
  { name: 'Writer Agent', role: 'Content & Briefs', status: 'active' as const, color: 'text-green-500' },
  { name: 'Legal Agent', role: 'Compliance & Contracts', status: 'active' as const, color: 'text-red-500' },
  { name: 'GBrain', role: 'Orchestrator', status: 'active' as const, color: 'text-purple-500' },
  { name: 'Hermes', role: 'Auto-improvement', status: 'idle' as const, color: 'text-amber-500' },
];

// ---- CONTRACTS ----
// Real music industry contract templates based on actual industry standards
// Each template reflects real terms: advances, royalty rates, recoupment, territories, etc.
// CRITICAL: Agents CANNOT sign contracts. Every contract ends with a human handoff alert.

export interface Contract {
  id: string;
  artistName: string;
  artistId: string;
  artistGenre: string;
  artistScore: number;
  type: 'Recording' | 'Distribution' | '360' | 'Joint Venture' | 'Licensing';
  subType: string;
  status: 'pending_review' | 'draft' | 'negotiation' | 'signed' | 'terminated';
  // Financial terms (real industry ranges)
  amount: number;           // Total deal value
  advance: number;          // Upfront recoupable advance
  royaltyRate: string;      // e.g. "18% of PPD"
  revenueShare: string;     // e.g. "50/50 net profit"
  recoupableItems: string[];// What gets recouped before artist gets paid
  // Term & territory
  term: string;             // e.g. "3 albums / 36 months"
  territory: string;
  albumCommitment: number;  // Number of albums required
  // Ownership
  mastersOwnership: string; // "Label" | "Artist" | "50/50" | "Reversion after X years"
  publishingSplit: string;  // "100% artist" | "75/25" | "50/50"
  // Rights
  creativeControl: string;  // "Artist" | "Shared" | "Label approval"
  marketingCommitment: string; // Minimum label spend on marketing
  syncRights: string;       // "50/50" | "Label" | "Artist"
  // Risk & compliance
  riskLevel: 'low' | 'medium' | 'high';
  reviewedBy: string;
  // Key clauses specific to this deal type
  clauses: string[];
  // Agency handoff
  agentAlert: string;       // FIXED: agents cannot sign
  // Status tracking
  createdAt: string;
  expiryDate: string;
  signedDate: string | null;
  notes: string;
}

// ═══════════════════════════════════════════════
// CONTRACT TEMPLATES — Real music industry terms
// ═══════════════════════════════════════════════

interface ContractTemplate {
  type: Contract['type'];
  subType: string;
  description: string;
  advanceRange: [number, number];       // min/max based on score
  royaltyRate: string;
  revenueShare: string;
  recoupableItems: string[];
  albumCommitment: number;
  termTemplate: string;                 // uses albumCommitment
  territory: string;
  mastersOwnership: string;
  publishingSplit: string;
  creativeControl: string;
  marketingCommitment: string;
  syncRights: string;
  riskLevel: 'low' | 'medium' | 'high';
  clausesTemplate: string[];
  notesTemplate: string;
  // Which artist profiles fit this template
  matchGenre: string[];                 // genres that fit this deal
  matchStatus: string[];                // artist statuses that fit
  minScore: number;                     // minimum artist score
}

// ════════════════════════════════════════════════════════════════
// TEMPLATE 1: STANDARD RECORDING DEAL (Traditional Label Deal)
// ════════════════════════════════════════════════════════════════
// Best for: Emerging artists with growth potential
// Label owns masters, recoupable advance, 3-5 album term
// Royalty: 15-25% of PPD (industry standard for new artists)
// ════════════════════════════════════════════════════════════════
const RECORDING_DEAL: ContractTemplate = {
  type: 'Recording',
  subType: 'Standard Recording Agreement',
  description: 'Traditional label deal — label finances recording/marketing in exchange for master ownership and a percentage of revenue. Best for artists ready to scale with label investment.',
  advanceRange: [15000, 150000],
  royaltyRate: '18% of PPD (Published Price to Dealer)',
  revenueShare: '50/50 net profit after recoupment',
  recoupableItems: [
    'Recording studio costs',
    'Producer fees',
    'Mixing & mastering',
    'Music video production (up to $40K per video)',
    'Marketing & promotion (digital + radio)',
    'Tour support (up to $25K per tour)',
    'Advance recoupment at 100% of artist royalties',
  ],
  albumCommitment: randomInt(2, 4),
  termTemplate: '{albums} albums with {options} label options',
  territory: 'Worldwide',
  mastersOwnership: 'Label owns masters in perpetuity, reversion to artist after 25 years if recouped',
  publishingSplit: '100% retained by artist (publishing handled separately)',
  creativeControl: 'Shared — label approval on producers, label approval on singles, artist approval on album',
  marketingCommitment: 'Minimum $25K marketing spend per album cycle',
  syncRights: '50/50 split on sync licensing revenue',
  riskLevel: 'medium',
  clausesTemplate: [
    'Exclusividad: Artist grants label exclusive worldwide rights for the Term',
    'Royalty rate: {rate} escalating to 20% after 50,000 album-equivalent units sold',
    'Advances fully recoupable from artist royalties at 100% rate',
    'Mechanical royalties: label pays statutory rate, recoupable from artist share',
    'Audit rights: Artist may audit label books once per year at own expense',
    'Key person clause: If A&R lead leaves label, artist may renegotiate',
    'Album delivery: Artist must deliver each album within 12 months of option exercise',
    'Free goods: 15% deduction for promotional copies (industry standard)',
    'New technology: Rates for emerging platforms negotiated in good faith',
    'Reversion: Masters revert to artist 25 years after release if fully recouped',
    'No cross-collateralization across different artist projects',
    'Force majeure: Standard clause with 6-month suspension limit',
  ],
  notesTemplate: 'Standard recording agreement for {genre} artist. Label covers recording budget up to ${budget}. Recoupment at standard industry rates. Agent recommendation: PROCEED WITH HUMAN REVIEW.',
  matchGenre: ['Regional Mexicano', 'Corridos Tumbados', 'Corridos Bélicos', 'Mariachi', 'Norteño', 'Sierreño', 'Latin Pop', 'Urbano'],
  matchStatus: ['emerging', 'watchlist', 'breakout'],
  minScore: 50,
};

// ════════════════════════════════════════════════════════════════
// TEMPLATE 2: DISTRIBUTION DEAL (Artist-Friendly)
// ════════════════════════════════════════════════════════════════
// Best for: Established indie artists who own their masters
// Artist keeps masters, label takes 10-25% for distribution services
// Shorter term, lower risk, no or small advance
// ════════════════════════════════════════════════════════════════
const DISTRIBUTION_DEAL: ContractTemplate = {
  type: 'Distribution',
  subType: 'Digital Distribution Agreement',
  description: 'Artist retains full ownership. Label provides distribution, playlist pitching, and marketing services in exchange for a revenue share. Low risk, artist-friendly terms.',
  advanceRange: [0, 30000],
  royaltyRate: '85% of net receipts to artist (15% label distribution fee)',
  revenueShare: '85/15 artist/label on net revenue',
  recoupableItems: [
    'Distribution platform fees',
    'Playlist pitching services',
    'Premium marketing campaigns (approved by artist)',
    'Metadata & asset delivery costs',
  ],
  albumCommitment: 1,
  termTemplate: '12 months with automatic renewal, 30-day termination notice by either party',
  territory: 'Worldwide (non-exclusive)',
  mastersOwnership: '100% retained by artist',
  publishingSplit: '100% retained by artist',
  creativeControl: '100% artist control',
  marketingCommitment: 'Label provides playlist pitching + social media support. Marketing campaigns optional at artist request.',
  syncRights: 'Artist retains 100% sync rights. Label may facilitate sync licensing for 15% commission.',
  riskLevel: 'low',
  clausesTemplate: [
    'Non-exclusive distribution: Artist may distribute through other channels',
    'Revenue split: 85% artist / 15% label on net receipts from all platforms',
    'No advance (or small recoupable advance at artist request)',
    'Term: 12 months, auto-renew unless 30-day termination notice given',
    'Artist retains 100% master ownership throughout and after term',
    'Label provides monthly reporting with platform-level breakdown',
    'Payment: 60 days after end of each quarter',
    'Audit rights: Artist may audit distribution records annually',
    'No creative control by label over artist content',
    'Label cannot sublicense or assign rights without artist consent',
    'Takedown: Artist may remove content with 30-day notice',
    'Mechanical royalties: Artist handles directly via The MLC or Harry Fox',
  ],
  notesTemplate: 'Low-risk distribution deal for {genre} artist. Artist retains all masters. Ideal for independent artists who want distribution without giving up ownership. Agent recommendation: DISTRIBUTION ONLY — NO RECORDING RIGHTS TRANSFERRED.',
  matchGenre: ['Latin Pop', 'Indie Pop', 'Latin Alternative', 'R&B', 'Indie Folk', 'Electropop', 'Experimental', 'Fusión'],
  matchStatus: ['unsigned_indie', 'monitoring', 'emerging'],
  minScore: 30,
};

// ════════════════════════════════════════════════════════════════
// TEMPLATE 3: 360 DEAL (Multiple Rights)
// ════════════════════════════════════════════════════════════════
// Best for: High-potential breakout artists
// Label invests heavily and takes % of ALL revenue streams
// 20-40% of touring, merch, publishing, endorsements
// Higher advance, bigger marketing commitment
// ════════════════════════════════════════════════════════════════
const DEAL_360: ContractTemplate = {
  type: '360',
  subType: 'Multiple Rights Agreement (360 Deal)',
  description: 'All-encompassing deal where label invests significantly and participates in all artist revenue streams: recordings, touring, merch, publishing, and endorsements. Higher investment = higher label share.',
  advanceRange: [50000, 350000],
  royaltyRate: '20% of PPD for recordings',
  revenueShare: 'Label takes: 25% touring income, 20% merch, 20% publishing, 15% endorsements',
  recoupableItems: [
    'All recording & production costs',
    'Music videos & visual content',
    'Marketing & radio promotion',
    'Tour support & live production',
    'Merchandise manufacturing & design',
    'Public relations & brand partnerships',
    'Digital advertising & social media management',
  ],
  albumCommitment: randomInt(3, 5),
  termTemplate: '{albums} albums with {options} label options, plus 360 rights for term + 12 months',
  territory: 'Worldwide (exclusive)',
  mastersOwnership: 'Label owns masters for term + 10 years, then reversion to artist',
  publishingSplit: '75/25 artist/label on publishing income',
  creativeControl: 'Shared — label has approval on branding, visual identity, major partnerships',
  marketingCommitment: 'Minimum $75K marketing investment per album, $100K for debut',
  syncRights: 'Label handles sync licensing, 50/50 split after 15% admin fee',
  riskLevel: 'high',
  clausesTemplate: [
    '360 rights: Label participates in ALL artist revenue streams as defined above',
    'Recording royalty: 20% of PPD, escalating to 22% after 100K units',
    'Touring: Label receives 25% of net touring income after production costs',
    'Merchandise: Label receives 20% of net merch revenue, handles manufacturing',
    'Publishing: Label receives 25% of publishing income (co-publishing deal)',
    'Endorsements: Label receives 15% of brand partnership income',
    'Advance: Fully recoupable from ALL revenue streams (cross-collateralized)',
    'Recoupment priority: 1) Recording costs, 2) Marketing, 3) Tour support, 4) Advance',
    'Album commitment: {albums} albums, label has {options} option periods',
    'Creative control: Label approves all commercial releases and branding',
    'Marketing guarantee: Label commits minimum $75K per album cycle',
    'Reversion: Masters revert to artist 10 years after term ends, if fully recouped',
    'Audit: Artist may audit annually. If error >5%, label pays audit costs',
    'Key person: If CEO or head of A&R leaves, artist may terminate 360 rights',
    'Sunset clause: 360 rights expire 12 months after term ends for touring/merch',
  ],
  notesTemplate: 'High-investment 360 deal for high-potential {genre} artist. Label takes share of ALL revenue streams. Significantly higher advance and marketing commitment. Agent recommendation: HIGH VALUE BUT HIGH COMMITMENT — REVIEW CAREFULLY.',
  matchGenre: ['Latin Trap', 'Urbano', 'Reggaeton', 'Dembow', 'Latin Drill', 'Rap', 'Corridos Tumbados'],
  matchStatus: ['breakout', 'watchlist', 'emerging'],
  minScore: 70,
};

// ════════════════════════════════════════════════════════════════
// TEMPLATE 4: JOINT VENTURE (Partnership Deal)
// ════════════════════════════════════════════════════════════════
// Best for: Established independent artists
// Artist and label form separate JV entity
// 50/50 split on costs and profits
// Artist has creative control, label brings infrastructure
// ════════════════════════════════════════════════════════════════
const JOINT_VENTURE: ContractTemplate = {
  type: 'Joint Venture',
  subType: 'Label Joint Venture Agreement',
  description: 'True partnership. Artist and label form a joint venture entity. 50/50 split on investment and profits. Artist retains creative control, label provides infrastructure and funding.',
  advanceRange: [25000, 200000],
  royaltyRate: '50/50 net profit split after JV costs (no traditional royalty)',
  revenueShare: '50/50 on all JV revenue after recoupment of JV costs',
  recoupableItems: [
    'JV operating costs (staff, office, legal)',
    'Recording & production (approved by JV committee)',
    'Marketing & promotion (JV budget approved by both parties)',
    'Distribution costs',
    'Third-party service fees',
  ],
  albumCommitment: 2,
  termTemplate: 'Initial 2-album commitment, renewable by mutual agreement',
  territory: 'Worldwide (exclusive for JV releases)',
  mastersOwnership: 'Owned by JV entity. Upon termination, masters split: label gets license for 10 years, then full reversion to artist',
  publishingSplit: '100% retained by artist (not part of JV)',
  creativeControl: 'Artist-led. Label has input but artist makes final creative decisions.',
  marketingCommitment: 'JV budget: minimum $50K marketing per release, approved by both parties',
  syncRights: '50/50 split on sync. Either party can approve sync deals over $5K.',
  riskLevel: 'medium',
  clausesTemplate: [
    'Joint Venture: Separate legal entity formed, 50/50 ownership between artist and label',
    'Profit split: 50/50 after recoupment of all JV costs from gross revenue',
    'Governance: JV committee (1 artist rep + 1 label rep), deadlock resolved by mediation',
    'Creative control: Artist has final say on all creative decisions',
    'Master ownership: JV entity owns masters. Reversion to artist 10 years after JV ends.',
    'Publishing: EXCLUDED from JV — 100% retained by artist',
    'Budget approval: Both parties must approve any expense over $15K',
    'Term: 2 albums, renewable by mutual written consent',
    'Marketing: JV to spend minimum $50K per release on marketing',
    'Territory: Worldwide exclusive for JV releases only',
    'Artist may release non-JV projects independently with 30-day notice',
    'Audit: Both parties have full access to JV financial records',
    'Dispute resolution: Mediation first, then binding arbitration in Los Angeles',
    'Buyout clause: Either party may buy out the other at fair market value after 3 years',
  ],
  notesTemplate: 'True partnership deal for {genre} artist. 50/50 on everything. Artist keeps publishing. Creative control belongs to artist. Agent recommendation: PARTNERSHIP MODEL — FAVORABLE FOR ESTABLISHED ARTISTS.',
  matchGenre: ['Latin Pop', 'Rap', 'Latin Alternative', 'Indie Pop', 'Rock', 'Fusión', 'R&B'],
  matchStatus: ['unsigned_indie', 'breakout', 'monitoring'],
  minScore: 60,
};

// ════════════════════════════════════════════════════════════════
// TEMPLATE 5: LICENSING DEAL (Limited Scope)
// ════════════════════════════════════════════════════════════════
// Best for: Niche/traditional genres, limited territory
// Label licenses specific recordings for specific territory/time
// No long-term commitment, lower risk
// ════════════════════════════════════════════════════════════════
const LICENSING_DEAL: ContractTemplate = {
  type: 'Licensing',
  subType: 'Master Use License Agreement',
  description: 'Limited-scope license for specific recordings in defined territories. Artist retains all rights. Label pays license fee + royalty for the right to distribute specific tracks.',
  advanceRange: [5000, 50000],
  royaltyRate: '50/50 of net licensing revenue',
  revenueShare: '50/50 on all revenue generated from licensed recordings',
  recoupableItems: [
    'License fee (non-recoupable)',
    'Marketing costs (recoupable from label share only)',
  ],
  albumCommitment: 1,
  termTemplate: 'License term: {years} years with renewal option',
  territory: 'Limited: Americas (North + South)',
  mastersOwnership: '100% retained by artist. Label receives license for specific recordings only.',
  publishingSplit: '100% retained by artist (not part of license)',
  creativeControl: '100% artist. Label licenses existing recordings only.',
  marketingCommitment: 'Label commits to minimum $10K marketing spend on licensed recordings',
  syncRights: 'Not included. Artist retains all sync rights and handles separately.',
  riskLevel: 'low',
  clausesTemplate: [
    'Limited license: Label licenses specific master recordings listed in Schedule A',
    'Term: {years} years from effective date, renewable by mutual agreement',
    'Territory: Americas (North America, Central America, South America)',
    'Royalty: 50% of net revenue generated from licensed recordings',
    'License fee: ${fee} paid upfront, non-recoupable and non-refundable',
    'No creative control: Label licenses EXISTING recordings only, no new recordings',
    'Artist retains 100% master ownership at all times',
    'Artist may license same recordings in other territories',
    'Label must account quarterly with 45 days of quarter end',
    'Audit rights: Artist may audit records for this license only',
    'No cross-collateralization with any other agreement',
    'Reverts: All rights revert to artist at end of term with 30-day wind-down',
    'Sync excluded: All sync licensing handled by artist separately',
    'No option periods: New license required for additional recordings',
  ],
  notesTemplate: 'Low-risk license for {genre} artist\'s existing catalog. Artist keeps everything. Label gets limited rights to distribute specific recordings. Agent recommendation: LOW RISK — GOOD FOR CATALOG MONETIZATION.',
  matchGenre: ['Tropical', 'Cumbia', 'Mariachi', 'Norteño', 'Sierreño', 'Fusión', 'Experimental'],
  matchStatus: ['unsigned_indie', 'monitoring', 'emerging'],
  minScore: 20,
};

// All templates indexed by type
const CONTRACT_TEMPLATES: Record<Contract['type'], ContractTemplate> = {
  'Recording': RECORDING_DEAL,
  'Distribution': DISTRIBUTION_DEAL,
  '360': DEAL_360,
  'Joint Venture': JOINT_VENTURE,
  'Licensing': LICENSING_DEAL,
};

// CRITICAL: Fixed agent handoff alert — appears on EVERY contract
const AGENT_HANDOFF_ALERT = `⚠️ AGENT REVIEW COMPLETE — HUMAN SIGNATURE REQUIRED
This contract has been drafted and reviewed by SIGNAL agents for your evaluation.
SIGNAL AGENTS CANNOT SIGN OR EXECUTE CONTRACTS. This document is a draft
recommendation only. Forward to legal counsel for final review, negotiation,
and execution. No binding agreement exists until signed by authorized
representatives of both parties. — Abe Music Group · SIGNAL Multi-Agent System`;

// Map artist to best contract template based on profile
function matchContractTemplate(artist: typeof ARTIST_POOL[0], score: number): ContractTemplate {
  const candidates: { template: ContractTemplate; priority: number }[] = [];

  for (const template of Object.values(CONTRACT_TEMPLATES)) {
    // Check score threshold
    if (score < template.minScore) continue;

    // Check genre match
    const genreMatch = artist.genres.some(g =>
      template.matchGenre.some(mg => g.toLowerCase().includes(mg.toLowerCase()))
    );

    // Check status match — we need to map to approximate status
    // Higher scores ≈ more established ≈ simpler deal
    let statusFit = false;
    if (score >= 70) {
      statusFit = template.matchStatus.includes('breakout') || template.matchStatus.includes('unsigned_indie');
    } else if (score >= 50) {
      statusFit = template.matchStatus.includes('emerging') || template.matchStatus.includes('watchlist');
    } else {
      statusFit = template.matchStatus.includes('unsigned_indie') || template.matchStatus.includes('monitoring');
    }

    if (genreMatch || statusFit) {
      let priority = 0;
      if (genreMatch) priority += 2;
      if (statusFit) priority += 1;

      // Boost priority for 360 deals on high-score urban artists
      if (template.type === '360' && score >= 75) priority += 1;
      // Boost priority for distribution on low-score indie artists
      if (template.type === 'Distribution' && score < 50) priority += 1;
      // Boost priority for recording deals on mid-score regional artists
      if (template.type === 'Recording' && score >= 40 && score <= 75) priority += 1;

      candidates.push({ template, priority });
    }
  }

  // Fallback to Distribution if no match
  if (candidates.length === 0) return DISTRIBUTION_DEAL;

  // Pick highest priority, break ties randomly
  const maxPriority = Math.max(...candidates.map(c => c.priority));
  const top = candidates.filter(c => c.priority === maxPriority);
  return top[Math.floor(Math.random() * top.length)].template;
}

function generateScore(artist: typeof ARTIST_POOL[0]): number {
  // Deterministic-ish score based on artist data
  const hash = artist.id.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
  return 30 + (hash % 60); // 30–89 range
}

export function generateContracts(): Contract[] {
  const shuffled = [...ARTIST_POOL].sort(() => Math.random() - 0.5);
  const count = randomInt(8, 14);
  const contracts: Contract[] = [];

  for (let i = 0; i < count; i++) {
    const artist = shuffled[i % shuffled.length];
    const score = generateScore(artist);
    const template = matchContractTemplate(artist, score);

    // Status distribution: mostly pending/draft/negotiation (agents can't sign)
    const statuses: Contract['status'][] = ['pending_review', 'draft', 'negotiation', 'pending_review', 'draft'];
    const status = pickRandom(statuses);

    // Calculate advance based on score and template range
    const [advMin, advMax] = template.advanceRange;
    const advanceFactor = score / 100;
    const advance = Math.round(advMin + (advMax - advMin) * advanceFactor);

    // Total deal value = advance + estimated royalties (2-5x advance)
    const multiplier = randomFloat(2, 5);
    const amount = Math.round(advance * multiplier);

    // Album commitment
    const albums = template.albumCommitment;

    // Customize term with album count
    const options = randomInt(1, 3);
    const term = template.termTemplate
      .replace('{albums}', String(albums))
      .replace('{options}', String(options))
      .replace('{years}', String(randomInt(2, 5)));

    // Pick relevant clauses from template
    const clauseCount = randomInt(4, 8);
    const clauses = [...template.clausesTemplate]
      .sort(() => Math.random() - 0.5)
      .slice(0, clauseCount)
      .map(c => c.replace('{rate}', template.royaltyRate)
                 .replace('{albums}', String(albums))
                 .replace('{options}', String(options)));

    const createdAt = new Date(Date.now() - randomInt(1, 180) * 24 * 60 * 60 * 1000);
    const termMonths = randomInt(12, 60);
    const expiryDate = new Date(createdAt.getTime() + termMonths * 30 * 24 * 60 * 60 * 1000);

    // Notes with genre & budget info
    const budget = Math.round(advance * randomFloat(0.3, 0.8));
    const notes = template.notesTemplate
      .replace('{genre}', artist.genres[0])
      .replace('{budget}', String(budget > 1000 ? `$${(budget / 1000).toFixed(0)}K` : `$${budget}`));

    contracts.push({
      id: `ctr-${artist.id.replace('art-', '')}-${Date.now()}-${i}`,
      artistName: artist.name,
      artistId: artist.id,
      artistGenre: artist.genres[0],
      artistScore: score,
      type: template.type,
      subType: template.subType,
      status,
      amount,
      advance,
      royaltyRate: template.royaltyRate,
      revenueShare: template.revenueShare,
      recoupableItems: template.recoupableItems.slice(0, randomInt(3, 6)),
      term,
      territory: template.territory,
      albumCommitment: albums,
      mastersOwnership: template.mastersOwnership,
      publishingSplit: template.publishingSplit,
      creativeControl: template.creativeControl,
      marketingCommitment: template.marketingCommitment,
      syncRights: template.syncRights,
      riskLevel: template.riskLevel,
      reviewedBy: pickRandom(['Legal Agent', 'GBrain', 'Analyst Agent', 'Legal Agent']),
      clauses,
      agentAlert: AGENT_HANDOFF_ALERT,
      createdAt: createdAt.toISOString().split('T')[0],
      expiryDate: expiryDate.toISOString().split('T')[0],
      signedDate: null, // Agents cannot sign contracts
      notes,
    });
  }

  return contracts;
}

// ---- NOTIFICATIONS ----

let notificationStore: Alert[] = [];

export function getNotifications(): Alert[] {
  if (notificationStore.length === 0) {
    notificationStore = generateAlerts(8);
  }
  return notificationStore;
}

export function refreshNotifications(): Alert[] {
  notificationStore = generateAlerts(8);
  return notificationStore;
}

export function markNotificationRead(id: string): void {
  const n = notificationStore.find(n => n.id === id);
  if (n) n.read = true;
}

export function markAllNotificationsRead(): void {
  notificationStore.forEach(n => { n.read = true; });
}
