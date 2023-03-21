from .gui import GUI
from ..radio.rf24 import RF24

def do_led_flash(**kwargs):
    color = kwargs.get("led_color", "ALL")
    print(f"flashing {color} leds")

def do_take_picture(**kwargs):
    print("taking picture")

def do_send_message(**kwargs):
    entry = kwargs.get("entry", "default")
    message = entry.get()
    print(f"sending {message} to satellite")
    try:
        radio = RF24(1)
        radio.transmit(message)
    except:
        print("could not connect to radio!")


def main():

    # create an instance of a GUI
    gui = GUI()
    gui.set_config()
    gui.make_fullscreen()

    # populate the GUI with widgets 
    gui.add_title("SATELLITE SYSTEMS GROUND STATION")
    gui.add_button("Flash LEDs", (1,1), do_led_flash)
    gui.add_button("Take Picture", (2,1), do_take_picture)
    message_entry = gui.add_entry("Message...", (1,2))
    gui.add_button("Send Message", (2,2), do_send_message, **{'entry':message_entry})
    gui.add_button("Quit Application",(3,1), gui.root.quit)
    gui.add_text_box((3,2))

    # run the gui application
    gui.run()


if __name__ == '__main__':
    main() 