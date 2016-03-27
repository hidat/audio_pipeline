import tb_ui.controller as TB
import sys

def main():
    directory = None
    if len(sys.argv) >= 2:
        directory = sys.argv[1]
                
    controller = TB.MetaControl.MetaController(directory)
    
    controller.app.mainloop()


if __name__ == "__main__":
    main()