#!/usr/bin/env bash
# ============================================================================
# agent-loop.sh — Loop de mejora continua para Custodio RAT
# ----------------------------------------------------------------------------
# Invoca el comando `audit-loop` de opencode en bucle hasta que el score
# global alcance el objetivo o se agoten las iteraciones.
#
# Uso:
#   ./scripts/agent-loop.sh              # modo apply (default: aplica fixes)
#   ./scripts/agent-loop.sh --dry-run    # modo dry-run (solo audita)
#   ./scripts/agent-loop.sh --apply      # modo apply (explícito)
#   ./scripts/agent-loop.sh --max-iter=15 --target-score=9.5
#   ./scripts/agent-loop.sh --help
#
# Requirements:
#   - bash 4+
#   - opencode CLI instalado y accesible (PATH o ruta explícita)
#   - git (para commits de red de seguridad)
#   - El comando `.opencode/command/audit-loop.md` debe existir
# ============================================================================

set -euo pipefail

# ----------------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------------
MAX_ITER=10
TARGET_SCORE=9.0
MODE="apply"               # "apply" | "dry-run"
OPENCODE_BIN="opencode"    # override con OPENCODE_BIN=/ruta/a/opencode
COMMAND_NAME="audit-loop"
LOG_DIR=".opencode/agent-memory"
PROJECT_ROOT="$(pwd)"

# Paths protegidas (no se commitean cambios en ellas)
PROTECTED_PATHS=(
    "paso/"
    ".opencode/opencode.json"
    ".opencode/command/"
    ".opencode/agent/"
    "package.json"
    "package-lock.json"
    "requirements.txt"
    "pyproject.toml"
    "tsconfig.json"
)

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
print_banner() {
    echo "================================================================"
    echo "  Custodio RAT — Agent Loop"
    echo "  Mode:           ${MODE}"
    echo "  Target score:   ${TARGET_SCORE}"
    echo "  Max iterations: ${MAX_ITER}"
    echo "  OpenCode bin:   ${OPENCODE_BIN}"
    echo "  Started:        $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "================================================================"
}

print_help() {
    grep -E "^# (Uso|Usage|Use)" "$0" | sed 's/^# //'
    echo ""
    echo "Opciones:"
    echo "  --dry-run           Solo audita, no aplica fixes."
    echo "  --apply             Aplica fixes automáticamente (default)."
    echo "  --max-iter=N        Máximo de iteraciones (default: 10)."
    echo "  --target-score=X    Score objetivo (default: 9.0)."
    echo "  --opencode-bin=PATH Ruta al binario de opencode (default: opencode)."
    echo "  --help              Muestra esta ayuda."
    echo ""
    echo "Variables de entorno:"
    echo "  OPENCODE_BIN        Override del binario de opencode."
    echo "  MAX_ITER            Override de max iteraciones."
    echo "  TARGET_SCORE        Override de score objetivo."
}

die() {
    echo "[ERROR] $*" >&2
    exit 1
}

info() {
    echo "[INFO]  $*"
}

warn() {
    echo "[WARN]  $*" >&2
}

# ----------------------------------------------------------------------------
# Parse args
# ----------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)        MODE="dry-run"; shift ;;
        --apply)          MODE="apply"; shift ;;
        --max-iter=*)     MAX_ITER="${1#*=}" ; shift ;;
        --target-score=*) TARGET_SCORE="${1#*=}" ; shift ;;
        --opencode-bin=*) OPENCODE_BIN="${1#*=}" ; shift ;;
        --help|-h)        print_help; exit 0 ;;
        *)                die "Argumento desconocido: $1. Usá --help." ;;
    esac
done

# Override desde env si están seteadas
MAX_ITER="${MAX_ITER:-${MAX_ITER}}"
TARGET_SCORE="${TARGET_SCORE:-${TARGET_SCORE}}"
OPENCODE_BIN="${OPENCODE_BIN:-${OPENCODE_BIN}}"

# ----------------------------------------------------------------------------
# Validaciones iniciales
# ----------------------------------------------------------------------------
print_banner

command -v "$OPENCODE_BIN" >/dev/null 2>&1 || die "No se encontró opencode CLI: '$OPENCODE_BIN'. Instalalo o usá --opencode-bin=PATH."
command -v git >/dev/null 2>&1 || die "git no está instalado."
[[ -d ".git" ]] || die "No estás en la raíz de un repo git."
[[ -f ".opencode/command/${COMMAND_NAME}.md" ]] || die "Comando .opencode/command/${COMMAND_NAME}.md no existe."

mkdir -p "$LOG_DIR"

# ----------------------------------------------------------------------------
# Loop
# ----------------------------------------------------------------------------
declare -i ITER=0
LAST_SCORE=""
SCORE_HISTORY=()

while [[ $ITER -lt $MAX_ITER ]]; do
    ITER+=1
    info ">>> Iteración ${ITER}/${MAX_ITER} (mode=${MODE})"

    # Snapshot del commit actual para referencia
    PRE_COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo 'no-commit-yet')"

    # Correr opencode con el comando audit-loop
    LOG_FILE="${LOG_DIR}/loop-$(date -u +%Y%m%dT%H%M%S)-iter-${ITER}.log"

    info "Lanzando opencode (log: ${LOG_FILE})..."

    # Capturar stdout y stderr. El comando emite el bloque === LOOP_RESULT ===
    # al final, que parseamos abajo.
    if ! "$OPENCODE_BIN" run "/${COMMAND_NAME}" \
            --mode "$MODE" \
            --iteration "$ITER" \
            --max-iter "$MAX_ITER" \
            --target-score "$TARGET_SCORE" \
            > "$LOG_FILE" 2>&1; then
        warn "opencode terminó con código no-cero. Log: ${LOG_FILE}"
        warn "Revisá el log y decidí si continuás. Abortando por seguridad."
        exit 2
    fi

    # Parsear el bloque LOOP_RESULT
    if ! RESULT=$(awk '/^=== LOOP_RESULT ===$/{flag=1;next}/^=== END_LOOP_RESULT ===$/{flag=0}flag' "$LOG_FILE"); then
        warn "No se encontró bloque LOOP_RESULT en el log. Abortando."
        exit 3
    fi

    SCORE_AFTER=$(echo "$RESULT" | awk -F': ' '/^score_after:/{print $2}' | tr -d '[:space:]')
    SCORE_BEFORE=$(echo "$RESULT" | awk -F': ' '/^score_before:/{print $2}' | tr -d '[:space:]')
    DELTA=$(echo "$RESULT" | awk -F': ' '/^delta:/{print $2}' | tr -d '[:space:]')
    FIXES=$(echo "$RESULT" | awk -F': ' '/^fixes_applied:/{print $2}' | tr -d '[:space:]')
    CRIT=$(echo "$RESULT" | awk -F': ' '/^critical_findings:/{print $2}' | tr -d '[:space:]')
    HIGH=$(echo "$RESULT" | awk -F': ' '/^high_findings:/{print $2}' | tr -d '[:space:]')
    EXIT_MET=$(echo "$RESULT" | awk -F': ' '/^exit_criterion_met:/{print $2}' | tr -d '[:space:]')

    info "Score: ${SCORE_BEFORE} → ${SCORE_AFTER} (Δ ${DELTA}) | fixes: ${FIXES} | crit: ${CRIT} | high: ${HIGH}"

    SCORE_HISTORY+=("$SCORE_AFTER")
    LAST_SCORE="$SCORE_AFTER"

    # Si estamos en modo apply, commit con tag de score
    if [[ "$MODE" == "apply" ]]; then
        # Verificar que no se tocaron paths protegidas
        if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
            # Detectar cambios en paths protegidas y revertir esos
            for protected in "${PROTECTED_PATHS[@]}"; do
                if git status --porcelain -- "$protected" 2>/dev/null | grep -q .; then
                    warn "Cambios detectados en path protegida: ${protected} — revirtiendo."
                    git checkout -- "$protected"
                fi
            done

            # Si todavía hay cambios, commitear
            if [[ -n "$(git status --porcelain 2>/dev/null)" ]]; then
                git add -A
                git commit -q -m "agent-loop(iter=${ITER}, score=${SCORE_BEFORE}->${SCORE_AFTER}, delta=${DELTA}, fixes=${FIXES})"
                info "Commit creado. HEAD: $(git rev-parse --short HEAD)"
            fi
        else
            info "Sin cambios para commitear."
        fi
    else
        info "(dry-run) No se commitea nada."
    fi

    # Chequear criterio de salida
    if [[ "$EXIT_MET" == "yes" ]]; then
        info "✓ Criterio de salida cumplido: score ${SCORE_AFTER} >= ${TARGET_SCORE}"
        echo ""
        echo "================================================================"
        echo "  Loop terminado con éxito"
        echo "  Iteraciones:    ${ITER}"
        echo "  Score final:    ${SCORE_AFTER}"
        echo "  Score inicial:  ${SCORE_BEFORE}"
        echo "  Historia:       ${SCORE_HISTORY[*]}"
        echo "================================================================"
        exit 0
    fi

    # Detectar oscilación (sube y baja sin tendencia)
    if [[ ${#SCORE_HISTORY[@]} -ge 3 ]]; then
        LAST3=("${SCORE_HISTORY[@]: -3}")
        # Si el medio es mayor que los extremos, osciló
        if (( $(echo "${LAST3[1]} > ${LAST3[0]}" | bc -l 2>/dev/null || echo 0) )) && \
           (( $(echo "${LAST3[1]} > ${LAST3[2]}" | bc -l 2>/dev/null || echo 0) )); then
            warn "Score oscilando en las últimas 3 iteraciones: ${LAST3[*]}"
            warn "Abortando por falta de convergencia."
            exit 4
        fi
    fi
done

# Si llegamos acá, agotamos iteraciones
warn "Se agotaron las iteraciones (${MAX_ITER}). Score final: ${LAST_SCORE}"
echo ""
echo "================================================================"
echo "  Loop terminado sin convergencia"
echo "  Iteraciones:    ${MAX_ITER}"
echo "  Score final:    ${LAST_SCORE}"
echo "  Historia:       ${SCORE_HISTORY[*]}"
echo "================================================================"
exit 5
