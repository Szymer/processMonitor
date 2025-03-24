# Process Monitor  

## Requirements  
- Python 3.8+  
- Django==5.1.7
- PostgreSQL/MySQL (if using a database other than SQLite)  
- Virtualenv (optional)  

## Installation and Setup  

### 1. Clone the Repository  
```bash
git clone https://github.com/Szymer/processMonitor.git
cd processMonitor
git checkout pm-0.0.4
```

### 2. Create and Activate a Virtual Environment  
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies  
```bash
pip install -r requirements.txt
```

### 4. Configure the Database  
If using SQLite, no configuration is needed.  
For PostgreSQL/MySQL:  
- Edit `settings.py`, section `DATABASES`  
- Manually create the database if required  

### 5. Apply Migrations  
```bash
python manage.py migrate
```

### 6. Create a Superuser (Optional)  
To manage users and data in the Django Admin Panel, create a superuser:  
```bash
python manage.py createsuperuser
```
Provide a username, email, and password when prompted.  

### 7. Run the Server  
```bash
python manage.py runserver
```
The application should now be accessible at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).  
start at [http://127.0.0.1:8000/home](http://127.0.0.1:8000/home)

### 8. Django Admin Panel  
The admin panel is available at:  
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)  

Log in with the superuser credentials to manage users and other models.  

## Running Tests  
To run tests:  
```bash
python manage.py test
```

## Additional Information  
- If using an `.env` file, include an `.env.example` with sample configuration.  
- If Celery/Redis tasks are used, describe how to start them.  
