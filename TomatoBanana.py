from audio_pipeline.tb_ui.controller import MetaControl
import argparse


def main():
    parser = argparse.ArgumentParser(description="Tag audio files with metadata")
    parser.add_argument('-d', '--release_directory', default=None, help="Directory containing release directories to be processed")
    parser.add_argument('-c', '--copy', default=None, help="Specify a directory to copy files to.")
    args = parser.parse_args()
    
    controller = MetaControl.MetaController(args.release_directory, args.copy)
    
    controller.app.mainloop()


if __name__ == "__main__":
    main()