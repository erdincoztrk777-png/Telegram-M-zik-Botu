import os
import telebot
from yt_dlp import YoutubeDL

# @BotFather'dan aldığınız Token'ı buraya yazın
BOT_TOKEN = "8849161569:AAEBdl4gnP7nwjLYHraO_VD0ygSjgavqNsk"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba! Bana indirmek istediğin şarkının adını veya SoundCloud linkini yaz, hemen göndereyim. 🎵")

@bot.message_handler(func=lambda message: True)
def search_and_send_music(message):
    query = message.text
    chat_id = message.chat.id
    
    status_msg = bot.send_message(chat_id, f"🔍 '{query}' aranıyor, lütfen bekleyin...")
    
    # YouTube engellerini aşmak için SoundCloud araması tanımlıyoruz
    if query.startswith("http"):
        search_query = query
    else:
        search_query = f"scsearch1:{query}" # SoundCloud üzerinde ara
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'preferredcodec': 'mp3'
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_info = info['entries']
            else:
                video_info = info
                
            filename = ydl.prepare_filename(video_info)
            
            # Dosya uzantısını kontrol et ve doğrula
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                for ext in ['.m4a', '.mp3', '.ogg', '.opus', '.wav']:
                    if os.path.exists(base + ext):
                        filename = base + ext
                        break

            bot.edit_message_text("🚀 Şarkı indirildi! Telegram'a yükleniyor...", chat_id, status_msg.message_id)
            
            with open(filename, 'rb') as audio:
                bot.send_audio(chat_id, audio, caption=f"🎵 {video_info.get('title')} - İndiren: @{bot.get_me().username}")
            
            os.remove(filename)
            bot.delete_message(chat_id, status_msg.message_id)
            
    except Exception as e:
        # Eğer SoundCloud'da da sorun olursa YouTube tekli format dene (Alternatif yedek plan)
        try:
            ydl_opts['default_search'] = 'ytsearch1'
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=True)
                video_info = info['entries'] if 'entries' in info else info
                filename = ydl.prepare_filename(video_info)
                
                with open(filename, 'rb') as audio:
                    bot.send_audio(chat_id, audio, caption=f"🎵 {video_info.get('title')}")
                os.remove(filename)
                bot.delete_message(chat_id, status_msg.message_id)
        except Exception as e2:
            bot.edit_message_text(f"❌ Şarkı teliften veya korumadan dolayı indirilemedi. Lütfen başka bir şarkı adı deneyin.", chat_id, status_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
