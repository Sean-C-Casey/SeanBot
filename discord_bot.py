from checker import RedditChecker
import discord
from discord.ext import commands, tasks
import logging
import settings as env

class CheckerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._checker = RedditChecker()
        self.check_reddit.start()
        
    
    @tasks.loop(minutes=5)
    async def check_reddit(self):
        server = self.bot.get_guild(808086919358840892)
        channel = discord.utils.get(server.channels, name="bot")
        # print(self.bot.user, channel)

        results = self._checker.search_posts()
        cases = results.get("cases")
        hospitalizations = results.get("hospitalizations")
        msg_parts = []

        # If no new results, then bail; nothing to report
        if cases is None and hospitalizations is None:
            return
        
        # Handle cases post
        if cases is None:
            msg_parts.append("No new case data :(\n")
        else:
            case_img_url = cases.get("img_url")
            cases_post_url = cases.get("url")
            if case_img_url is None:
                msg_parts.append("New COVID-19 Edmonton case data posted (but no chart): {}".format(cases_post_url))
            else:
                #msg_parts.append(case_img_url)
                msg_parts.append("New COVID-19 Edmonton case data posted: {}\n".format(cases_post_url))
        
        # Handle hospitalizations post
        if hospitalizations is None:
            msg_parts.append("No new hospitalization data :(")
        else:
            hospitalization_img_url = hospitalizations.get("img_url")
            hospitalizations_post_url = hospitalizations.get("url")
            if hospitalization_img_url is None:
                msg_parts.append("New COVID-19 Edmonton hospitalization data posted (but no chart): {}".format(hospitalizations_post_url))
            else:
                #msg_parts.append(hospitalization_img_url)
                msg_parts.append("New COVID-19 Edmonton hospitalization data posted: {}".format(hospitalizations_post_url))

        await channel.send("\n".join(msg_parts))
    

    @check_reddit.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="!")

# @bot.event
# async def on_ready():
#     print(f"{bot.user} has connected to Discord!")
#     server = discord.utils.get(bot.guilds, id=808086919358840892)
#     print(f"Member of {server.name} (id: {server.id})")

bot.add_cog(CheckerCog(bot))
bot.run(env.DISCORD_BOT_TOKEN)