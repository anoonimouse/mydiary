import os
from mydiary import create_app

config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)

if __name__ == '__main__':
    # Run on all network interfaces to allow mobile access
    # Access via: http://<your-local-ip>:5000
    app.run(host='0.0.0.0', port=5000, debug=True)
