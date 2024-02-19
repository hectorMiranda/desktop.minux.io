# Control Center Application

## Overview

This application serves as a control center demo for a consulting company. It features a dashboard with various functionalities, including task management, map visualization, and placeholder features for future AI and help sections.

## Features

- **Dashboard:** A user-friendly interface with quick access to different sections of the application.
- **Task Management:** Create and manage tasks, with the ability to mark tasks as done and view their completion status.
- **Map Visualization:** Display a map showing the top 20 most important cities in the state of Veracruz, Mexico, with random completion percentages for each city.
- **AI Section:** Placeholder for future AI-related features.
- **Help Section:** Placeholder for future help and documentation features.

## Technologies Used

- **Tkinter:** For creating the graphical user interface.
- **Firebase Firestore:** For storing and managing task data.
- **Folium:** For generating and displaying the map.
- **PyQt5:** For displaying the map in a separate window using a web view.
- **Python-dotenv:** For loading environment variables from a `.env` file.

## Setup and Installation

1. Install the required Python packages:

    ```bash
    pip install tkinter firebase-admin folium PyQt5 python-dotenv
    ```

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
    python main.py
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
