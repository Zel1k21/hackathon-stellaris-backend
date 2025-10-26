from internal.api.server import run

if __name__ == "__main__":
    load_dotenv("deploy/.env")
    run()
