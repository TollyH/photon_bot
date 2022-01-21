import sys

from photon_bot import PhotonBot


def main():
    if len(sys.argv) == 1:
        print("You must provide the path to a valid config file")
        sys.exit(1)
    bot = PhotonBot(sys.argv[1])
    bot.start()


if __name__ == "__main__":
    main()
