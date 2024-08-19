from ui.app import App

if __name__ == "__main__":
    import sys
    import os
    
    # Set up the working directory to be the script's directory
    # This ensures we can always find our media/icons folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Get target folder from command line args if provided
    target_folder = sys.argv[1] if len(sys.argv) > 1 else None
    
    app = App()
    if target_folder:
        app.explorer.current_path = target_folder
        app.explorer.refresh_tree()
    app.mainloop() 