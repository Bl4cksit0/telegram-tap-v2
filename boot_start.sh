#!/data/data/com.termux/files/usr/bin/bash
# Ejecutado por Termux:Boot al encender el celular.
# Se copia automaticamente a ~/.termux/boot/ por setup.sh

# Esperar a que la red este lista
sleep 15

cd ~/telegram-bot-tap

# Reinicia el bot automaticamente si crashea
while true; do
    python main.py >> bot.log 2>&1
    echo "$(date '+%Y-%m-%d %H:%M:%S') [BOOT] proceso terminado, reiniciando en 60s..." >> bot.log
    sleep 60
done
