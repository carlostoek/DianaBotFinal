#!/bin/bash

# GitHub PR Feedback Extractor
# Extrae TODOS los comentarios de un PR incluyendo los comentarios en líneas de código

if [ -z "$1" ]; then
    echo "Uso: $0 [número-de-pr]"
    echo "Ejemplo: $0 6"
    exit 1
fi

PR_NUM=$1
OUTPUT_FILE="pr_${PR_NUM}_feedback.txt"

echo "📋 Obteniendo feedback completo del PR #$PR_NUM..."
echo ""

# Limpiar archivo de salida si existe
> "$OUTPUT_FILE"

# Obtener información básica del PR
echo "Extrayendo información general..."
gh pr view $PR_NUM --json title,body,number 2>/dev/null > /tmp/pr_basic_$$.json

# Obtener comentarios de conversación
echo "Extrayendo comentarios de conversación..."
gh pr view $PR_NUM --json comments 2>/dev/null > /tmp/pr_comments_$$.json

# Obtener reviews (comentarios generales de review)
echo "Extrayendo reviews generales..."
gh pr view $PR_NUM --json reviews 2>/dev/null > /tmp/pr_reviews_$$.json

# Obtener comentarios en archivos específicos (review comments en líneas de código)
echo "Extrayendo comentarios en código..."
gh api repos/:owner/:repo/pulls/$PR_NUM/comments 2>/dev/null > /tmp/pr_review_comments_$$.json

# Generar el archivo de salida
cat > "$OUTPUT_FILE" << 'HEADER'
============================================================
PULL REQUEST FEEDBACK COMPLETO
============================================================

HEADER

# Agregar información básica
jq -r '"PULL REQUEST #" + (.number | tostring) + ": " + .title + "\n" + 
"=" * 60 + "\n\n" +
"DESCRIPCIÓN:\n" + 
"-" * 60 + "\n" +
(.body // "Sin descripción") + "\n\n"' /tmp/pr_basic_$$.json >> "$OUTPUT_FILE"

# Agregar comentarios de conversación
{
    echo "COMENTARIOS EN LA CONVERSACIÓN:"
    echo "------------------------------------------------------------"
} >> "$OUTPUT_FILE"

CONV_COUNT=$(jq '.comments | length' /tmp/pr_comments_$$.json 2>/dev/null || echo "0")

if [ "$CONV_COUNT" -gt 0 ]; then
    jq -r '.comments[] | 
    "👤 @" + .author.login + " (" + .createdAt + "):\n" + 
    .body + "\n" + 
    "-" * 60 + "\n"' /tmp/pr_comments_$$.json >> "$OUTPUT_FILE" 2>/dev/null
else
    echo "No hay comentarios en la conversación." >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# Agregar reviews generales
{
    echo "REVIEWS GENERALES:"
    echo "------------------------------------------------------------"
} >> "$OUTPUT_FILE"

REVIEW_COUNT=$(jq '.reviews | length' /tmp/pr_reviews_$$.json 2>/dev/null || echo "0")

if [ "$REVIEW_COUNT" -gt 0 ]; then
    jq -r '.reviews[] | 
    "👤 @" + .author.login + " [" + .state + "] (" + .submittedAt + "):\n" + 
    (if .body != "" and .body != null then .body else "(Sin comentario general)" end) + "\n" + 
    "-" * 60 + "\n"' /tmp/pr_reviews_$$.json >> "$OUTPUT_FILE" 2>/dev/null
else
    echo "No hay reviews generales." >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# Agregar comentarios en código (LO MÁS IMPORTANTE)
{
    echo "COMENTARIOS EN ARCHIVOS ESPECÍFICOS:"
    echo "============================================================"
} >> "$OUTPUT_FILE"

CODE_COMMENT_COUNT=$(jq '. | length' /tmp/pr_review_comments_$$.json 2>/dev/null || echo "0")

if [ "$CODE_COMMENT_COUNT" -gt 0 ]; then
    # Procesar comentarios agrupados por archivo
    jq -r '
    # Agrupar por archivo
    group_by(.path) | 
    map(
        # Para cada grupo de archivo
        "\n📄 ARCHIVO: " + .[0].path + "\n" +
        ("=" * 60) + "\n" +
        (
            # Ordenar comentarios por línea
            sort_by(.line // .original_line // 0) | 
            map(
                "  📍 Línea " + ((.line // .original_line // 0) | tostring) + 
                " | @" + .user.login + ":\n" +
                "  💬 " + .body + "\n" +
                (if .diff_hunk then 
                    "  \n  Código:\n" +
                    "  ```\n" +
                    (.diff_hunk | split("\n") | map("  " + .) | join("\n")) + "\n" +
                    "  ```\n"
                else "" end) +
                "  " + ("-" * 58) + "\n"
            ) | join("")
        )
    ) | join("")
    ' /tmp/pr_review_comments_$$.json >> "$OUTPUT_FILE" 2>/dev/null
else
    echo "No hay comentarios en archivos específicos." >> "$OUTPUT_FILE"
fi

# Agregar resumen final
{
    echo ""
    echo "============================================================"
    echo "RESUMEN:"
    echo "------------------------------------------------------------"
    echo "  📝 Comentarios en conversación: $CONV_COUNT"
    echo "  ⭐ Reviews generales: $REVIEW_COUNT"
    echo "  📄 Comentarios en código: $CODE_COMMENT_COUNT"
    echo "============================================================"
} >> "$OUTPUT_FILE"

# Limpiar archivos temporales
rm -f /tmp/pr_basic_$$.json /tmp/pr_comments_$$.json /tmp/pr_reviews_$$.json /tmp/pr_review_comments_$$.json

echo "✅ Feedback completo guardado en: $OUTPUT_FILE"
echo ""
echo "📊 Resumen:"
echo "  📝 Comentarios en conversación: $CONV_COUNT"
echo "  ⭐ Reviews generales: $REVIEW_COUNT"
echo "  📄 Comentarios en código: $CODE_COMMENT_COUNT"
echo ""
echo "💡 Ahora puedes usar este archivo con Claude Code:"
echo "   cat $OUTPUT_FILE"
