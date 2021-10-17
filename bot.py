from checker import RedditChecker
import datetime as dt
import discord
from discord.ext import commands, tasks
import logging
import os
import settings as env

class CheckerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._checker = RedditChecker()
        self.check_reddit.start()
        
    
    @tasks.loop(minutes=5)
    async def check_reddit(self):
        # Don't bother checking if u/mikesmith929 already posted today
        if self.posted_today():
            return False

        server = self.bot.get_guild(808086919358840892)
        channel = discord.utils.get(server.channels, name="bot")
        # print(self.bot.user, channel)

        results = self._checker.search_posts()
        cases = results.get("cases")
        hospitalizations = results.get("hospitalizations")

        # If no new results, then bail; nothing to report
        if cases is None and hospitalizations is None:
            return False
        
        # Logging
        if cases is not None and hospitalizations is None:
            logger.info("Found new case data!")
        elif cases is None and hospitalizations is not None:
            logger.info("Found new hospitalization data!")
        else:
            logger.info("Found new case and hospitalization data!")
        
        # Handle cases post
        if cases is None:
            await channel.send("No new case data :(")
        else:
            case_img_url = cases.get("img_url")
            cases_post_url = cases.get("url")
            if case_img_url is None:
               await channel.send("New COVID-19 Edmonton case data posted (but no chart): {}".format(cases_post_url))
            else:
               await channel.send("New COVID-19 Edmonton case data posted: {}".format(cases_post_url))
        
        # Handle hospitalizations post
        if hospitalizations is None:
            await channel.send("No new hospitalization data :(")
        else:
            hospitalization_img_url = hospitalizations.get("img_url")
            hospitalizations_post_url = hospitalizations.get("url")
            if hospitalization_img_url is None:
                await channel.send("New COVID-19 Edmonton hospitalization data posted (but no chart): {}".format(hospitalizations_post_url))
            else:
                await channel.send("New COVID-19 Edmonton hospitalization data posted: {}".format(hospitalizations_post_url))

        return True
    

    @check_reddit.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()
        logger.info("Beginning monitoring background task")

    
    def posted_today(self):
        # Check if posts already made today
        cases_date = dt.datetime.strptime(self._checker.db_conn.retrieve_post_date(
            "Edmonton Cases of COVID-19"
        ), "%B %d %Y").date()
        hospitalizations_date = dt.datetime.strptime(self._checker.db_conn.retrieve_post_date(
            "Edmonton Vaccination & Hospitalization Cases of COVID-19"
        ), "%B %d %Y").date()
        today = dt.date.today()
        return (cases_date == today and hospitalizations_date == today)
    

    @commands.command(name="check-reddit")
    async def check_command(self, ctx):
        if self.posted_today():
            await ctx.send("Already posted today.")
        else:
            logger.info("Reddit check manually initiated via Discord bot command by user %s" % ctx.message.author.name)
            new_posts = await self.check_reddit()
            if new_posts is False:
                await ctx.send("Nothing new yet :(")


if __name__ == "__main__":
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    log_file = os.path.join(env.BASE_DIR, "info.log")
    log_handler = logging.FileHandler(filename=log_file, encoding="utf-8", mode="w")
    log_handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s'))
    logger.addHandler(log_handler)
    
    bot = commands.Bot(command_prefix="!")

    # @bot.event
    # async def on_ready():
    #     print(f"{bot.user} has connected to Discord!")
    #     server = discord.utils.get(bot.guilds, id=808086919358840892)
    #     print(f"Member of {server.name} (id: {server.id})")

    bot.add_cog(CheckerCog(bot))
    bot.run(env.DISCORD_BOT_TOKEN)