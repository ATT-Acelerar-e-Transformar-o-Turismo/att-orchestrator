# Project Overview

This project is a microservices-based application designed for tourism data analysis and visualization. It is composed of several services, each with a specific responsibility, orchestrated using Docker Compose. The services are managed as Git submodules.

## Architecture

The application follows a microservices architecture, with the following components:

*   **User Interface:** A React-based single-page application that provides the user interface for the application. It is built with Vite and uses TailwindCSS for styling.
*   **User Service:** Manages user authentication and authorization.
*   **Data Collector:** Responsible for collecting data from various sources.
*   **Resource Service:** Manages data resources.
*   **Indicator Service:** Processes data and calculates indicators.
*   **Knowledge Base:** Provides a knowledge base for the application.
*   **Reverse Proxy:** Nginx is used as a reverse proxy to route requests to the appropriate service.
*   **Message Queues:** RabbitMQ is used for asynchronous communication between services.
*   **Authentication:** Keycloak is used for user authentication and authorization.

## Building and Running

The project is orchestrated using Docker Compose. To build and run the project, you will need to have Docker and Docker Compose installed.

1.  **Clone the repository and submodules:**

    ```bash
    git clone --recurse-submodules https://github.com/ATT-Acelerar-e-Transformar-o-Turismo/att-orchestrator.git
    ```

2.  **Start the application:**

    ```bash
    docker-compose up -d
    ```

This will start all the services in the background. You can then access the user interface by navigating to `http://localhost` in your browser.

## Development Conventions

*   **Microservices:** Each microservice is developed and maintained in its own repository and included as a Git submodule.
*   **API:** The services communicate with each other through REST APIs.
*   **Asynchronous Communication:** RabbitMQ is used for asynchronous communication between services to decouple them and improve scalability.
*   **Styling:** The user interface uses TailwindCSS for styling.
*   **Testing:** The user interface has end-to-end tests written with Playwright.
