if __name__ == "__main__":
    from uvicorn import run
    run(app="app.main:app", host="localhost", port=8080, reload=True)
