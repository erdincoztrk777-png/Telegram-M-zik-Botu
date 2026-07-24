import os
import telebot
import requests

# @BotFather'dan aldığınız Token'ı buraya yazın
BOT_TOKEN = "8849161569:AAEBdl4gnP7nwjLYHraO_VD0ygSjgavqNsk"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Merhaba! Bana indirmek istediğin şarkının adını yaz, senin için hemen bulup göndereyim. 🎵")

@bot.message_handler(func=lambda message: True)
def download_music(message):
    query = message.text
    chat_id = message.chat.id
    
    status_msg = bot.send_message(chat_id, f"🔍 '{query}' aranıyor ve hazırlanıyor, lütfen bekleyin...")
    
    try:
        # Ücretsiz ve engelsiz müzik arama/indirme API'si
        search_url = f"https://deezer.com{query}&limit=1"
        response = requests.get(search_url).json()
        
        if not response.get('data'):
            bot.edit_message_text("❌ Aradığınız şarkı bulunamadı. Lütfen başka bir şarkı adı deneyin.", chat_id, status_msg.message_id)
            return
            
        track = response['data'][0]
        title = track['title']
        artist = track['artist']['name']
        audio_url = track['preview'] # Şarkının önizleme/ses dosyası linki
        
        if not audio_url:
            bot.edit_message_text("❌ Şarkının ses dosyasına ulaşılamadı.", chat_id, status_msg.message_id)
            return
            
        bot.edit_message_text("🚀 Şarkı bulundu! Telegram'a yükleniyor...", chat_id, status_msg.message_id)
        
        # Ses dosyasını indirip Telegram'a gönderme
        audio_data = requests.get(audio_url).content
        filename = f"{artist} - {title}.mp3"
        
        with open(filename, 'wb') as f:
            f.write(audio_data)
            
        with open(filename, 'rb') as audio:
            bot.send_audio(chat_id, audio, caption=f"🎵 {artist} - {title}\nİndiren: @{bot.get_me().username}")
            
        os.remove(filename)
        bot.delete_message(chat_id, status_msg.message_id)
        
    except Exception as e:
        bot.edit_message_text("❌ Sunucu bağlantısında bir sorun oluştu, lütfen az sonra tekrar deneyin.", chat_id, status_msg.message_id)
        print(f"Hata: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
