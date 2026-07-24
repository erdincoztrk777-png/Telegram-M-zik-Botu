import os
import telebot
from yt_dlp import YoutubeDL

# @BotFather'dan aldığınız Token'ı buraya tırnaklar içine yazın
BOT_TOKEN = "8849161569:AAEBdl4gnP7nwjLYHraO_VD0ygSjgavqNsk"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba! Bana indirmek istediğin şarkının adını yaz, senin için bulup göndereyim. 🎵")

@bot.message_handler(func=lambda message: True)
def search_and_send_music(message):
    query = message.text
    chat_id = message.chat.id
    
    # Kullanıcıya işlemin başladığını bildir
    status_msg = bot.send_message(chat_id, f"🔍 '{query}' YouTube'da aranıyor, lütfen bekleyin...")
    
    # yt-dlp ayarları (Sadece en iyi ses kalitesini mp3/m4a olarak indirmek için)
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'default_search': 'ytsearch1', # İlk sonucu al
        'noplaylist': True,
        'quiet': True
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Şarkıyı ara ve bilgilerini al
            info = ydl.extract_info(query, download=True)
            
            # Eğer arama sonucu liste olarak döndüyse ilk elemanı al
            if 'entries' in info:
                video_info = info['entries'][0]
            else:
                video_info = info
                
            filename = ydl.prepare_filename(video_info)
            # Eğer uzantı değiştiyse kontrol et
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                filename = base + ".m4a"

            # Şarkı adını düzenle ve Telegram'a ses dosyası olarak gönder
            bot.edit_message_text("🚀 Şarkı bulundu! Telegram'a yükleniyor...", chat_id, status_msg.message_id)
            
            with open(filename, 'rb') as audio:
                bot.send_audio(chat_id, audio, caption=f"🎵 {video_info.get('title')} - İndiren: @{bot.get_me().username}")
            
            # Temizlik: Sunucuda yer kaplamaması için indirilen dosyayı sil
            os.remove(filename)
            bot.delete_message(chat_id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Bir hata oluştu veya şarkı bulunamadı. Lütfen tekrar deneyin.", chat_id, status_msg.message_id)
        print(f"Hata detayı: {e}")

# Botu sürekli aktif tut
if __name__ == "__main__":
    print("Bot başarıyla çalıştırıldı...")
    bot.infinity_polling()
