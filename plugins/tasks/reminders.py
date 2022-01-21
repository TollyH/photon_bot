"""The task that pushes reminders out to users."""
import datetime

import discord
import discord.ext.tasks

import utils
from photon_bot import PhotonBot


def register_tasks(bot: PhotonBot):
    @discord.ext.tasks.loop(seconds=60)
    async def push_reminders():
        with utils.Database(bot.config['DatabaseConnection']) as database:
            reminder_list = database.fetch(
                "SELECT due_datetime, user_id, content FROM reminders "
                + "WHERE due_datetime <= %s;", (datetime.datetime.now(),)
            )
            for reminder in reminder_list:
                user = bot.discord_bot.get_user(reminder[1])
                if user is not None:
                    successful = True
                    try:
                        await user.send(
                            "**Hey!** You asked me to remind you about this:"
                            + f"\n```{reminder[2]}```"
                        )
                    except discord.Forbidden:
                        successful = False
                    if successful:
                        database.modify(
                            "DELETE FROM reminders WHERE due_datetime = %s "
                            + "AND user_id = %s AND content = %s LIMIT 1;",
                            reminder
                        )

    @push_reminders.before_loop
    async def wait_for_ready():
        # Do not start pushing reminders until bot is logged in
        await bot.discord_bot.wait_until_ready()

    push_reminders.start()
