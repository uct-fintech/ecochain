# EcoChain API

## Setup

Follow these steps to set up the EcoChain API:

1. **Clone the Repository:**

   Clone the EcoChain repository to your local machine and navigate to the project directory using the following commands:

   ```
   git clone https://github.com/Henri-99/ecochain/
   cd ecochain
   ```

2. **Create a Virtual Environment:**

   It is recommended to use a virtual environment to isolate the project dependencies. You can create a virtual environment using Python's built-in `venv` module:

   ```
   python -m venv env
   ```

3. **Install Dependencies:**

   Install the required Python packages and libraries by running the following command. This will install all the dependencies listed in the 'requirements.txt' file.

   ```
   pip install -r requirements.txt
   ```

4. **Initialize the Database (First-Time Only):**

   If you are setting up the EcoChain API for the first time, you need to initialize the database by running the following command:

   ```
   python app.py --init
   ```

   This command will create the necessary database tables and perform any initial setup required for the application.

5. **Start the API:**

   To start the EcoChain API, simply run the following command:

   ```
   python app.py
   ```

   The API should now be up and running, and you can access it by visiting `http://localhost:5000` in your web browser or using API client tools like Postman.
