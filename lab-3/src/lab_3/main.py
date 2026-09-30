from lab_3.bootstrap.application import create_app

app = create_app()


def dev():
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
