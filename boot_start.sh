#!/data/data/com.termux/files/usr/bin/bash
# Este script lo ejecuta Termux:Boot al encender el celular.
# Se copia automaticamente a ~/.termux/boot/ por setup.sh

# Esperar a que la red este lista
sleep 15

cd ~/telegram-bot-tap
python main.py >> bot.log 2>&1
