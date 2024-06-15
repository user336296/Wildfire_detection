import cv2
import numpy as np
import telebot
import threading

Alarm_Status = False
Telegram_Status = False
Fire_Reported = 0

# BOT
TOKEN = '6865981280:AAEzXgVAt43joQ-CIcw1oKSCne11mW279mo'
CHAT_ID = '2012650197'  # ID бота

bot = telebot.TeleBot(TOKEN, parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_telegram_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

video = cv2.VideoCapture("wild_fire.mp4")  # видео с камеры дрона(в нашем случае просто запись)

while True:
    (grabbed, frame) = video.read()
    if not grabbed:
        break

    original_frame = frame.copy()

    frame = cv2.resize(frame, (960, 540))

    blur = cv2.GaussianBlur(frame, (21, 21), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    lower = [18, 50, 50]
    upper = [35, 255, 255]
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    mask = cv2.inRange(hsv, lower, upper)

    output = cv2.bitwise_and(frame, hsv, mask=mask)

    no_red = cv2.countNonZero(mask)

    if int(no_red) > 15000:
        Fire_Reported = Fire_Reported + 1

    cv2.imshow("Original Video", original_frame)  # исходник
    cv2.imshow("Processed Frame", output)  # после обработки

    if Fire_Reported >= 1:

        if not Telegram_Status:
            threading.Thread(target=send_telegram_message, args=("Warning! Fire has been detected!",)).start()
            Telegram_Status = True

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
video.release()