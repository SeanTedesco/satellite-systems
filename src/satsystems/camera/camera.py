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

    return parser.parse_args()

def do_shot(camera, **kwargs):
    print(f'do shot with: {kwargs}')
    camera.shot()

def do_video(camera, **kwargs):
    print(f'do video with: {kwargs}')
    camera.video()

def main():
    from .picam import PiCam

    options = parse_cmdline()
    cam = PiCam()
    options.function(cam, option=options)

if __name__ == '__main__':
    main()
