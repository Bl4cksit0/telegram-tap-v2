#!/data/data/com.termux/files/usr/bin/bash
# Ejecutar este script UNA SOLA VEZ desde Termux para instalar todo

echo "=== Instalando dependencias del sistema ==="
pkg update -y
pkg install -y python git

echo "=== Instalando dependencias Python ==="
pip install -r requirements.txt

echo "=== Configurando archivo .env ==="
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "IMPORTANTE: Edita el archivo .env con tus credenciales:"
    echo "  nano .env"
    echo ""
    echo "Necesitas:"
    echo "  API_ID y API_HASH -> https://my.telegram.org"
    echo "  PHONE             -> tu numero con codigo de pais (ej: +5491112345678)"
    echo "  GROUP             -> username del grupo a monitorear"
fi

echo ""
echo "=== Configurando inicio automatico con Termux:Boot ==="
mkdir -p ~/.termux/boot
cp boot_start.sh ~/.termux/boot/start_bot.sh
chmod +x ~/.termux/boot/start_bot.sh

echo ""
echo "=== Listo! ==="
echo "Para iniciar el bot manualmente: bash run.sh"
echo "Para que arranque automatico al encender: instala Termux:Boot desde F-Droid"
