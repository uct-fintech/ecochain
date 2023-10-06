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

## API Documentation

### Home

- **Endpoint**: `/`
- **Method**: `GET`
- **Description**: A welcome message for the EcoChain app.

**Response**:
```json
{
  "status": "success",
  "message": "Welcome to EcoChain"
}
```

---

### Login

- **Endpoint**: `/login`
- **Methods**: `GET`, `POST`
- **Description**: Authenticate and log in the user.

**POST Request Body**:

| Parameter | Description           |
|:---------:|:---------------------:|
| email     | The user's email.     |
| password  | The user's password.  |

**Responses**:

- Successful login:
```json
{
  "status": "success",
  "message": "Logged in successfully"
}
```

- Invalid email or password:
```json
{
  "status": "error",
  "message": "Invalid email or password"
}
```

- GET request:
```json
{
  "status": "info",
  "message": "GET request for login"
}
```

---

### Logout

- **Endpoint**: `/logout`
- **Method**: `POST`
- **Description**: Log out the current user.

**Response**:
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

### Register

- **Endpoint**: `/register`
- **Methods**: `GET`, `POST`
- **Description**: Register a new user.

**POST Request Body**:

| Parameter | Description           |
|:---------:|:---------------------:|
| email     | The user's email.     |
| password  | The user's password.  |

**Responses**:

- Successful registration:
```json
{
  "status": "success",
  "message": "User registered and logged in successfully"
}
```

- Email already in use:
```json
{
  "status": "error",
  "message": "Email is already in use"
}
```

- Registration error:
```json
{
  "status": "error",
  "message": "An error occurred while registering the user"
}
```

- GET request:
```json
{
  "status": "info",
  "message": "GET request for register"
}
```

---

### Protected

- **Endpoint**: `/protected`
- **Method**: `GET`
- **Description**: Access sensitive information (requires user authentication).

**Response**:
```json
{
  "status": "success",
  "message": "You've successfully accessed a protected route",
  "id": "UserID",
  "email": "UserEmail"
}
```

---

### Get Reports

- **Endpoint**: `/get_reports`
- **Method**: `GET`
- **Description**: Retrieve reports based on the user's company ID (requires user authentication).

**Response**:
```json
{
  "status": "success",
  "message": "You've successfully accessed report data",
  "id": "CompanyID"
}
```

---

**Note**: The `/protected` and `/get_reports` endpoints require user authentication. Make sure you have a valid session for accessing these endpoints.
