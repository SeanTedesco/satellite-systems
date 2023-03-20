import argparse

def parse_cmdline():
    parser = argparse.ArgumentParser(description='Control Camera Module.')

    subparser = parser.add_subparsers()

    shot_parser = subparser.add_parser('shot', help='Capture a single image.')
    shot_parser.add_argument('-f', '--filename', type=str, help='Name of output file.')
    shot_parser.set_defaults(function=do_shot)

    video_parser = subparser.add_parser('video', help='Record a video.')
    video_parser.add_argument('-f', '--filename', type=str, help='Name of output file.')
    video_parser.set_defaults(function=do_video)

    converter_parser = subparser.add_parser('convert', help='Convert to and from Images and Base64 strings.')
    converter_parser.add_argument('-f', '--filename', type=str, help='Path to the image file.')
    converter_parser.add_argument('-b', '--base64', action='store_true', help='Change to base64 to iamge conversion.')
    converter_parser.set_defaults(function=do_conversion)

    return parser.parse_args()

def do_shot(camera, options):
    camera.shot()

def do_video(camera, options):
    camera.video()

def do_conversion(camera, options):
    file_path = options.filename
    use_base64 = options.base64
    if use_base64:
        camera.base64_to_image(file_path)
    else:
        camera.image_to_base64(file_path)

def main():
    from .picam import PiCam

    option = parse_cmdline()
    cam = PiCam()
    option.function(cam, options=option)

if __name__ == '__main__':
    main()
