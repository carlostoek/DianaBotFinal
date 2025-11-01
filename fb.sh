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

# Obtener información básica del PR
echo "Extrayendo información general..."
gh pr view $PR_NUM --json title,body,number 2>/dev/null > /tmp/pr_basic.json

# Obtener comentarios de conversación
echo "Extrayendo comentarios de conversación..."
gh pr view $PR_NUM --json comments 2>/dev/null > /tmp/pr_comments.json

# Obtener reviews (comentarios generales de review)
echo "Extrayendo reviews generales..."
gh pr view $PR_NUM --json reviews 2>/dev/null > /tmp/pr_reviews.json

# Obtener comentarios en archivos específicos (review comments en líneas de código)
echo "Extrayendo comentarios en código..."
gh api repos/:owner/:repo/pulls/$PR_NUM/comments 2>/dev/null > /tmp/pr_review_comments.json

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
.body + "\n\n"' /tmp/pr_basic.json >> "$OUTPUT_FILE"

# Agregar comentarios de conversación
echo "COMENTARIOS EN LA CONVERSACIÓN:" >> "$OUTPUT_FILE"
echo "------------------------------------------------------------" >> "$OUTPUT_FILE"
CONV_COUNT=$(jq '.comments | length' /tmp/pr_comments.json)

if [ "$CONV_COUNT" -gt 0 ]; then
    jq -r '.comments[] | 
    "👤 @" + .author.login + " (" + .createdAt + "):\n" + 
    .body + "\n" + 
    "-" * 60 + "\n"' /tmp/pr_comments.json >> "$OUTPUT_FILE"
else
    echo "No hay comentarios en la conversación." >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# Agregar reviews generales
echo "REVIEWS GENERALES:" >> "$OUTPUT_FILE"
echo "------------------------------------------------------------" >> "$OUTPUT_FILE"
REVIEW_COUNT=$(jq '.reviews | length' /tmp/pr_reviews.json)

if [ "$REVIEW_COUNT" -gt 0 ]; then
    jq -r '.reviews[] | 
    "👤 @" + .author.login + " [" + .state + "] (" + .submittedAt + "):\n" + 
    (if .body != "" then .body else "(Sin comentario general)" end) + "\n" + 
    "-" * 60 + "\n"' /tmp/pr_reviews.json >> "$OUTPUT_FILE"
else
    echo "No hay reviews generales." >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# Agregar comentarios en código (LO MÁS IMPORTANTE)
echo "COMENTARIOS EN ARCHIVOS ESPECÍFICOS:" >> "$OUTPUT_FILE"
echo "============================================================" >> "$OUTPUT_FILE"
CODE_COMMENT_COUNT=$(jq '. | length' /tmp/pr_review_comments.json)

if [ "$CODE_COMMENT_COUNT" -gt 0 ]; then
    jq -r 'group_by(.path) | .[] | 
    "\n📄 ARCHIVO: " + .[0].path + "\n" +
    "=" * 60 + "\n" +
    (sort_by(.position) | .[] | 
        "  📍 Línea " + (.line // .original_line | tostring) + 
        " | @" + .user.login + " [" + .created_at + "]:\n" +
        "  💬 " + .body + "\n" +
        (if .diff_hunk then 
            "  \n  Código relacionado:\n" +
            "  ```\n" +
            (.diff_hunk | split("\n") | .[] | "  " + .) + "\n" +
            "  ```\n"
        else "" end) +
        "  " + "-" * 58 + "\n"
    )' /tmp/pr_review_comments.json >> "$OUTPUT_FILE"
else
    echo "No hay comentarios en archivos específicos." >> "$OUTPUT_FILE"
fi

# Agregar resumen final
echo "" >> "$OUTPUT_FILE"
echo "============================================================" >> "$OUTPUT_FILE"
echo "RESUMEN:" >> "$OUTPUT_FILE"
echo "------------------------------------------------------------" >> "$OUTPUT_FILE"
echo "  📝 Comentarios en conversación: $CONV_COUNT" >> "$OUTPUT_FILE"
echo "  ⭐ Reviews generales: $REVIEW_COUNT" >> "$OUTPUT_FILE"
echo "  📄 Comentarios en código: $CODE_COMMENT_COUNT" >> "$OUTPUT_FILE"
echo "============================================================" >> "$OUTPUT_FILE"

# Limpiar archivos temporales
rm -f /tmp/pr_basic.json /tmp/pr_comments.json /tmp/pr_reviews.json /tmp/pr_review_comments.json

echo "✅ Feedback completo guardado en: $OUTPUT_FILE"
echo ""
echo "📊 Resumen:"
echo "  📝 Comentarios en conversación: $CONV_COUNT"
echo "  ⭐ Reviews generales: $REVIEW_COUNT"
echo "  📄 Comentarios en código: $CODE_COMMENT_COUNT"
echo ""
echo "💡 Ahora puedes usar este archivo con Claude Code:"
echo "   cat $OUTPUT_FILE"
echo ""
echo "🤖 O directamente:"
echo "   claude-code --message \"Lee $OUTPUT_FILE y corrige todos los issues mencionados\""
