
#Ese código es el punto de entrada para ejecutar una aplicación web hecha con Flask.

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9911)