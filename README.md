# Qwicker

Welcome to Qwicker, an innovative attendance tracking system designed to simplify and enhance the way attendance is managed at educational institutions. This project utilizes a combination of MySQL and Azure Functions to create a dynamic and efficient system for both students and professors.

## Features

- **Dynamic Code Generation**: Professors can start an attendance session that generates a new code every 30 seconds.
- **Real-Time Verification**: Students enter the code to mark their attendance; codes are verified in real-time.
- **Database Integration**: Utilizes a MySQL database to store all attendance records securely and efficiently.
- **Scalable Architecture**: Built with Azure Functions to ensure scalability and handle multiple requests smoothly.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- MySQL Server
- Node.js
- Azure account with Azure Functions

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jorgevart/qwicker_code.git
Install necessary packages

Open your web browser and navigate to http://localhost:3000 to view the interface.

Professors: Log in through the professor portal, select a course, and start the attendance session.

Students: Log in through the student portal, select the same course, and enter the displayed code to mark attendance.
