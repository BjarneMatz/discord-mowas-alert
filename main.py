import logo_handle
import discord_bot


def main():
    # prepare startup
    logo_handle.fetch_logos()

    # start bot
    discord_bot.start()


if __name__ == "__main__":
    main()
