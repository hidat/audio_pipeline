import MetaModel
import MetaView
import sys


def main():
    if len(sys.argv) < 2:
        print('asdkj')
        exit(2)
        
    directory = sys.argv[1]
    meta_model = MetaModel.process_directory(directory)
    
    while meta_model.has_next():
        releases, tracks = meta_model.get_meta()
        for dir, release_info in releases.items():
            frame = MetaView.MetaFrame(release_info, tracks)
            frame.mainloop()
    
    # while meta_model.has_next():
        # releases, tracks = meta_model.get_meta()
        # for dir, release_info in releases.items():
            # MetaView.display_metadata(release_info, tracks)

main()
