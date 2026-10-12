import os
import sys
import time
import random
from gpiozero import LED, Button, Buzzer
from PIL import Image, ImageDraw, ImageFont

from waveshare_epd import epd2in13_V4

# GPIO assignments
btn_start = Button(23) #pin 16
btn_action = Button(5) #29
led_red = LED(27) #13
led_green = LED(22) #15
buzzer = Buzzer(4) #7

epd = epd2in13_V4.EPD()
best_time = None

def draw_screen(status_text, sub_text=""):
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    #header
    draw.rectangle([(0, 0), (epd.height - 1, 18)], fill=0)
    draw.text((55, 3), "REFLEX TESTER GAME", fill=255, font=font)

    # Status Message
    draw.text((10, 35), status_text, fill=0, font=font)
    draw.text((10, 55), sub_text, fill=0, font=font)

    # High Score Footer
    best_str = f"Best Record: {best_time} ms" if best_time else "Best Record: None"
    draw.line([(10, 85), (epd.height - 10, 85)], fill=0)
    draw.text((10, 95), best_str, fill=0, font=font)

    epd.init_fast()
    epd.display_fast(epd.getbuffer(image))
    epd.sleep()

def main():
    global best_time
    print("starting game - Ctrl+C to exit")

    epd.init()
    epd.Clear()
    epd.sleep()

    draw_screen("Press START (right side)", "to begin")

    try:
        while True:
            if btn_start.is_pressed:
                buzzer.beep(on_time=0.1, off_time=0.1, n=1)
                draw_screen("ready", "watch for green LED")

                led_red.on()
                delay = random.uniform(2.0, 5.0)
                start_wait = time.time()

                early_press = False
                while time.time() - start_wait < delay:
                    if btn_action.is_pressed:
                        early_press = True
                        break
                    time.sleep(0.01)

                led_red.off()

                if early_press:
                    buzzer.beep(on_time=0.5, off_time=0.1, n=1)
                    draw_screen("TOO EARLY", "Wait for Green LED.")
                    time.sleep(2)
                    draw_screen("Press START (right side)", "to try again.")
                    continue

                led_green.on()
                start_time = time.time()

                while not btn_action.is_pressed:
                    if time.time() - start_time > 3.0:
                        break

                reaction_time = int((time.time() - start_time) * 1000)
                led_green.off()

                if reaction_time >= 3000:
                    draw_screen("TIMEOUT", "No response detected.")
                else:
                    buzzer.beep(on_time=0.08, off_time=0.05, n=2)
                    if best_time is None or reaction_time < best_time:
                        best_time = reaction_time
                        draw_screen(f"NEW RECORD: {reaction_time} ms")
                    else:
                        draw_screen(f"Time: {reaction_time} ms", "nt")

                time.sleep(3)
                draw_screen("Press START (right side)", "to try again.")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nExiting")
        led_red.off()
        led_green.off()
        epd.init()
        epd.Clear()
        epd.sleep()

if __name__ == '__main__':
    main()
            

