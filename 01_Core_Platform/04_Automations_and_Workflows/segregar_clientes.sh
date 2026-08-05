#!/bin/bash
# Script de Segregación Agentic Native para Sonora Digital Corp
# Mueve archivos de clientes a estructura estándar según extensión
# Crea 05_Agentic_Skills para cada cliente

set -e

BASE_DIR="/home/mystic/Documentos/Sonora Digital Corp Nuevo/02_Client_Projects"

echo "=========================================="
echo "  SEGREGACIÓN AGENTIC NATIVE"
echo "  Sonora Digital Corp"
echo "=========================================="
echo ""

# Encontrar todos los directorios de clientes
for client_dir in "$BASE_DIR"/*; do
    if [ ! -d "$client_dir" ]; then continue; fi
    
    client_name=$(basename "$client_dir")
    
    # Ignorar carpetas especiales
    case "$client_name" in
        Clientes_Old|Audiovisuales_Old)
            echo "⚠ Saltando carpeta _Old: $client_name"
            continue
            ;;
    esac
    
    echo "📁 Cliente: $client_name"
    
    # 1. Crear estructura estándar (incluyendo 05_Agentic_Skills)
    mkdir -p "$client_dir/01_Discovery"
    mkdir -p "$client_dir/02_Source_Code"
    mkdir -p "$client_dir/03_Media_Assets/Audio"
    mkdir -p "$client_dir/03_Media_Assets/Visual"
    mkdir -p "$client_dir/04_Deployment"
    mkdir -p "$client_dir/05_Agentic_Skills"
    echo "  ✓ Estructura Agentic creada"
    
    # 2. Mover archivos del raíz del cliente según extensión
    
    # Audios
    find "$client_dir" -maxdepth 1 -type f \( -iname '*.mp3' -o -iname '*.wav' -o -iname '*.aac' -o -iname '*.m4a' -o -iname '*.ogg' -o -iname '*.flac' -o -iname '*.wma' \) 2>/dev/null | while read -r file; do
        if [ -f "$file" ]; then
            mv "$file" "$client_dir/03_Media_Assets/Audio/" 2>/dev/null && echo "    → $(basename "$file") → 03_Media_Assets/Audio"
        fi
    done
    
    # Visuales
    find "$client_dir" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.mp4' -o -iname '*.svg' -o -iname '*.gif' -o -iname '*.webp' -o -iname '*.avif' -o -iname '*.mov' -o -iname '*.webm' -o -iname '*.mkv' \) 2>/dev/null | while read -r file; do
        if [ -f "$file" ]; then
            mv "$file" "$client_dir/03_Media_Assets/Visual/" 2>/dev/null && echo "    → $(basename "$file") → 03_Media_Assets/Visual"
        fi
    done
    
    # Código/Config
    find "$client_dir" -maxdepth 1 -type f \( -iname '*.py' -o -iname '*.js' -o -iname '*.ts' -o -iname '*.tsx' -o -iname '*.jsx' -o -iname '*.json' -o -iname '*.feature' -o -iname '*.yaml' -o -iname '*.yml' -o -iname '*.env' -o -iname '*.sh' -o -iname '*.bash' -o -iname '*.zsh' -o -iname '*.sql' -o -iname '*.html' -o -iname '*.css' -o -iname '*.scss' -o -iname '*.sass' -o -iname '*.less' -o -iname '*.xml' -o -iname '*.toml' -o -iname '*.ini' -o -iname '*.cfg' -o -iname '*.conf' -o -iname '*.dockerfile' -o -iname '*.dockerignore' -o -iname '*.gitignore' -o -iname '*.lock' -o -iname '*.requirements' -o -iname '*.gradle' -o -iname '*.properties' -o -iname '*.proto' -o -iname '*.graphql' -o -iname '*.prisma' -o -iname '*.svelte' -o -iname '*.vue' -o -iname '*.php' -o -iname '*.rb' -o -iname '*.go' -o -iname '*.rs' -o -iname '*.java' -o -iname '*.kt' -o -iname '*.swift' -o -iname '*.m' -o -iname '*.h' -o -iname '*.c' -o -iname '*.cpp' -o -iname '*.hpp' -o -iname '*.cs' -o -iname '*.fs' -o -iname '*.fsx' -o -iname '*.fsi' -o -iname '*.ml' -o -iname '*.mli' -o -iname '*.erl' -o -iname '*.hrl' -o -iname '*.ex' -o -iname '*.exs' -o -iname '*.elm' -o -iname '*.purs' -o -iname '*.lhs' -o -iname '*.jl' -o -iname '*.r' -o -iname '*.R' -o -iname '*.rmd' -o -iname '*.Rmd' -o -iname '*.ipynb' -o -iname '*.pl' -o -iname '*.pm' -o -iname '*.t' -o -iname '*.lua' -o -iname '*.moon' -o -iname '*.nim' -o -iname '*.nims' -o -iname '*.nimble' -o -iname '*.dart' -o -iname '*.groovy' -o -iname '*.gvy' -o -iname '*.gy' -o -iname '*.gsh' -o -iname '*.scala' -o -iname '*.sc' -o -iname '*.kts' -o -iname '*.clj' -o -iname '*.cljs' -o -iname '*.cljc' -o -iname '*.edn' -o -iname '*.cr' -o -iname '*.ecr' -o -iname '*.shards' \) 2>/dev/null | while read -r file; do
        if [ -f "$file" ]; then
            mv "$file" "$client_dir/02_Source_Code/" 2>/dev/null && echo "    → $(basename "$file") → 02_Source_Code"
        fi
    done
    
    # Bases de datos
    find "$client_dir" -maxdepth 1 -type f \( -iname '*.db' -o -iname '*.sqlite' -o -iname '*.sqlite3' -o -iname '*.sqlitedb' -o -iname '*.mdb' -o -iname '*.accdb' -o -iname '*.frm' -o -iname '*.myd' -o -iname '*.myi' -o -iname '*.ibd' -o -iname '*.dbf' -o -iname '*.ndx' -o -iname '*.nsx' -o -iname '*.ntx' -o -iname '*.cdb' -o -iname '*.sdb' -o -iname '*.ddb' -o -iname '*.hdb' -o -iname '*.fdb' \) 2>/dev/null | while read -r file; do
        if [ -f "$file" ]; then
            mv "$file" "$client_dir/04_Deployment/" 2>/dev/null && echo "    → $(basename "$file") → 04_Deployment"
        fi
    done
    
    # Documentos
    find "$client_dir" -maxdepth 1 -type f \( -iname '*.md' -o -iname '*.txt' -o -iname '*.pdf' -o -iname '*.docx' -o -iname '*.doc' -o -iname '*.odt' -o -iname '*.rtf' -o -iname '*.tex' -o -iname '*.epub' -o -iname '*.mobi' -o -iname '*.azw' -o -iname '*.azw3' -o -iname '*.djvu' -o -iname '*.djv' -o -iname '*.chm' -o -iname '*.hlp' -o -iname '*.log' -o -iname '*.rst' -o -iname '*.adoc' -o -iname '*.asciidoc' -o -iname '*.textile' -o -iname '*.creole' -o -iname '*.mediawiki' -o -iname '*.wiki' -o -iname '*.org' -o -iname '*.pod' -o -iname '*.man' -o -iname '*.1' -o -iname '*.2' -o -iname '*.3' -o -iname '*.4' -o -iname '*.5' -o -iname '*.6' -o -iname '*.7' -o -iname '*.8' -o -iname '*.9' -o -iname '*.nroff' -o -iname '*.me' -o -iname '*.ms' -o -iname '*.mm' -o -iname '*.mom' -o -iname '*.groff' -o -iname '*.roff' -o -iname '*.tmac' -o -iname '*.1b' -o -iname '*.3pm' -o -iname '*.3perl' -o -iname '*.3x' -o -iname '*.3p' -o -iname '*.3posix' -o -iname '*.3m' -o -iname '*.3bsd' -o -iname '*.3v' -o -iname '*.3net' -o -iname '*.3socket' -o -iname '*.3avr' -o -iname '*.3lua' -o -iname '*.3c' -o -iname '*.3tcl' -o -iname '*.3tk' \) 2>/dev/null | while read -r file; do
        if [ -f "$file" ]; then
            mv "$file" "$client_dir/01_Discovery/" 2>/dev/null && echo "    → $(basename "$file") → 01_Discovery"
        fi
    done
    
    # 3. Reorganizar archivos sueltos en subdirectorios no estándar
    find "$client_dir" -type f \
        ! -path "*/01_Discovery/*" \
        ! -path "*/02_Source_Code/*" \
        ! -path "*/03_Media_Assets/*" \
        ! -path "*/04_Deployment/*" \
        ! -path "*/05_Agentic_Skills/*" \
        ! -path "*/node_modules/*" \
        ! -path "*/.git/*" \
        ! -path "*/__pycache__/*" \
        ! -path "*/.venv/*" \
        ! -path "*/.pytest_cache/*" \
        ! -path "*/.ruff_cache/*" \
        ! -path "*/.mypy_cache/*" \
        ! -path "*/.tox/*" \
        ! -path "*/.egg-info/*" \
        ! -path "*/dist/*" \
        ! -path "*/build/*" \
        ! -path "*/.next/*" \
        ! -path "*/.nuxt/*" \
        ! -path "*/.cache/*" \
        ! -path "*/tmp/*" \
        ! -path "*/temp/*" \
        ! -path "*/.tmp/*" \
        ! -path "*/.temp/*" \
        ! -path "*/coverage/*" \
        ! -path "*/.coverage/*" \
        ! -path "*/htmlcov/*" \
        ! -path "*/.sass-cache/*" \
        ! -path "*/.parcel-cache/*" \
        ! -path "*/.webpack/*" \
        ! -path "*/.gradle/*" \
        ! -path "*/target/*" \
        ! -path "*/out/*" \
        ! -path "*/bin/*" \
        ! -path "*/obj/*" \
        ! -path "*/vendor/*" \
        ! -path "*/.bundle/*" \
        ! -path "*/.gem/*" \
        ! -path "*/.cargo/*" \
        ! -path "*/.rustup/*" \
        ! -path "*/.npm/*" \
        ! -path "*/.yarn/*" \
        ! -path "*/.pnpm-store/*" \
        ! -path "*/.bower/*" \
        ! -path "*/.composer/*" \
        ! -path "*/.nuget/*" \
        ! -path "*/.paket/*" \
        ! -path "*/.dart-tool/*" \
        ! -path "*/.pub-cache/*" \
        ! -path "*/.flutter/*" \
        ! -path "*/.android/*" \
        ! -path "*/.ios/*" \
        ! -path "*/.idea/*" \
        ! -path "*/.vscode/*" \
        ! -path "*/.vs/*" \
        ! -path "*/.sublime/*" \
        ! -path "*/.emacs.d/*" \
        ! -path "*/.vim/*" \
        ! -path "*/.neovim/*" \
        ! -path "*/.zsh/*" \
        ! -path "*/.bash/*" \
        ! -path "*/.fish/*" \
        ! -path "*/.profile/*" \
        ! -path "*/.bashrc/*" \
        ! -path "*/.zshrc/*" \
        ! -path "*/.vimrc/*" \
        ! -path "*/.gitconfig/*" \
        ! -path "*/.gitattributes/*" \
        ! -path "*/.gitmodules/*" \
        ! -path "*/.editorconfig/*" \
        ! -path "*/.dockerignore/*" \
        ! -path "*/.eslintignore/*" \
        ! -path "*/.prettierignore/*" \
        ! -path "*/.stylelintignore/*" \
        ! -path "*/.jshintignore/*" \
        ! -path "*/.npmignore/*" \
        ! -path "*/.yarnignore/*" \
        ! -path "*/.pnpignore/*" \
        ! -path "*/.bowerignore/*" \
        ! -path "*/.composerignore/*" \
        ! -path "*/.nugetignore/*" \
        ! -path "*/.paketignore/*" \
        ! -path "*/.dartignore/*" \
        ! -path "*/.pubignore/*" \
        ! -path "*/.flutterignore/*" \
        ! -path "*/.androidignore/*" \
        ! -path "*/.iosignore/*" \
        ! -path "*/.ideaignore/*" \
        ! -path "*/.vscodeignore/*" \
        ! -path "*/.vsignore/*" \
        ! -path "*/.sublimeignore/*" \
        ! -path "*/.emacsignore/*" \
        ! -path "*/.vimignore/*" \
        ! -path "*/.neovimignore/*" \
        ! -path "*/.zshignore/*" \
        ! -path "*/.bashignore/*" \
        ! -path "*/.fishignore/*" \
        ! -path "*/.profileignore/*" \
        ! -path "*/.bashrcignore/*" \
        ! -path "*/.zshrcignore/*" \
        ! -path "*/.vimrcignore/*" \
        ! -path "*/.gitconfigignore/*" \
        ! -path "*/.gitattributesignore/*" \
        ! -path "*/.gitmodulesignore/*" \
        ! -path "*/.editorconfigignore/*" \
        2>/dev/null | while read -r file; do
        
        if [ ! -f "$file" ]; then continue; fi
        
        filename=$(basename "$file")
        ext="${filename##*.}"
        ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
        
        # Determinar destino basado en extensión
        dest=""
        case "$ext" in
            mp3|wav|aac|m4a|ogg|flac|wma)
                dest="03_Media_Assets/Audio"
                ;;
            png|jpg|jpeg|mp4|svg|gif|webp|avif|mov|webm|mkv)
                dest="03_Media_Assets/Visual"
                ;;
            py|js|ts|tsx|jsx|json|feature|yaml|yml|env|sh|bash|zsh|sql|html|css|scss|sass|less|xml|toml|ini|cfg|conf|dockerfile|dockerignore|gitignore|lock|requirements|gradle|properties|proto|graphql|prisma|svelte|vue|php|rb|go|rs|java|kt|swift|m|h|c|cpp|hpp|cs|fs|fsx|fsi|ml|mli|erl|hrl|ex|exs|elm|purs|lhs|jl|r|rmd|ipynb|pl|pm|t|lua|moon|nim|nims|nimble|dart|groovy|gvy|gy|gsh|scala|sc|kts|clj|cljs|cljc|edn|cr|ecr|shards|p8)
                dest="02_Source_Code"
                ;;
            db|sqlite|sqlite3|sqlitedb|mdb|accdb|frm|myd|myi|ibd|dbf|ndx|nsx|ntx|cdb|sdb|ddb|hdb|fdb)
                dest="04_Deployment"
                ;;
            md|txt|pdf|docx|doc|odt|rtf|tex|epub|mobi|azw|azw3|djvu|djv|chm|hlp|log|rst|adoc|asciidoc|textile|creole|mediawiki|wiki|org|pod|man|nroff|me|ms|mm|mom|groff|roff|tmac|1|2|3|4|5|6|7|8|9)
                dest="01_Discovery"
                ;;
        esac
        
        if [ -n "$dest" ]; then
            target="$client_dir/$dest"
            mkdir -p "$target"
            mv "$file" "$target/" 2>/dev/null && echo "    → $filename → $dest"
        fi
    done
    
    echo ""
done

echo "=========================================="
echo "  SEGREGACIÓN COMPLETADA"
echo "=========================================="
echo ""
