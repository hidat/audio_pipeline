from audio_pipeline.tb_ui.controller import MetaControl
import sys

def main():
    directory = None
    if len(sys.argv) >= 2:
        directory = sys.argv[1]
                
    controller = MetaControl.MetaController(directory)
    
    controller.app.mainloop()


if __name__ == "__main__":
    main()