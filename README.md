# TWC Finance

This Python program is designed to run on a server, monitoring a specified directory for the upload of Excel files. Once an Excel file is detected, the program reads and validates each row before inserting the validated data into a Data Mart using MySQL.

## Features

- **Automated Validation**: The program automatically validates each row of data in the Excel file, ensuring accuracy and compliance with predefined criteria.

- **MySQL Integration**: Validated data is seamlessly inserted into a MySQL Data Mart, providing a centralized and structured storage solution.

- **Directory Monitoring**: The program continuously monitors a specified directory for new Excel file uploads, allowing for real-time data processing.

## Getting Started

To get started with the Excel File Validator and Data Mart Loader, follow the steps below:

### Prerequisites

- Python (v3.6 or higher) : [click here](https://www.python.org/downloads/).
- MySQL Server (XAMPP) : [click here](https://www.apachefriends.org/download.html).
- Additional Python packages (specified in requirements.txt)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/eraldss1/twc-finance.git
   ```

2. Navigate to the project directory:

   ```bash
   cd twc-finance
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the program by editing the configuration file (twc_config.yml) with your MySQL connection details and directory path. There is example inside the config directory.

   ```bash
   host: ""
   port:
   user: ""
   password: ""
   database: ""

   directory_to_watch : ""
   ```

### Usage

Upload Excel files to the specified directory, and the program will automatically validate each row and insert the valid data into the MySQL Data Mart.
