# DESKTOP.MINUX.IO

## What is minux?

Minux is more :) 

## Features

- plugin based architecture

## Technologies Used

- **Tkinter:** For creating the graphical user interface.
- **Firebase Firestore:** For storing and managing task data.
- **Folium:** For generating and displaying the map.
- **PyQt5:** For displaying the map in a separate window using a web view.

## Setup and Installation

1. Install the required Python packages (minux_requirements.txt)
2. Set up a Firebase project and download the service account key JSON file.
3. Create a `.env` file in the root directory of the project with the following environment variables:

    ```dotenv
    WINDOW_TITLE=Your App Title
    WELCOME_MESSAGE=Welcome Message
    SERVICE_ACCOUNT_KEY_PATH=path/to/your/service_account_key.json
    WINDOW_WIDTH=800
    WINDOW_HEIGHT=600
    ABOUT_MESSAGE=About message for your app
    ```

4. Run the application:

    ```bash
    python minux.py
    ```

## License

This project is [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) licensed.
