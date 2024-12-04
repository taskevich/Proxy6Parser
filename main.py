from selenium_worker import SeleniumWorker


def main():
    proxy = "149.126.222.69:50100@salabul:NxatNEaDEj"

    worker = SeleniumWorker(proxy)
    worker.get("https://px6.me/")

    with open("accounts.txt", mode="r+") as file:
        file.seek(0)
        credentials_data = file.readline().strip()

    if not credentials_data:
        raise RuntimeError("Нет данных на авторизацию")

    email, password = credentials_data.split(":")
    worker.login(email, password)
    worker.get_proxies()


if __name__ == "__main__":
    main()
