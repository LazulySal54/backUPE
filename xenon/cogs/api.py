from discord.ext import commands as cmd
from aiohttp import web


class Api(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connected = 0
        self.app = web.Application()
        self.app.add_routes([
            web.get("/health", self.liveness_probe),
            web.get("/ready", self.readiness_probe)
        ])
        self.runner = web.AppRunner(self.app)
        self.bot.loop.create_task(self.start_app())

    @cmd.Cog.listener()
    async def on_connect(self):
        self.connected += 1

    def cog_unload(self):
        self.bot.loop.create_task(self.runner.cleanup())

    async def start_app(self):
        await self.runner.setup()
        site = web.TCPSite(self.runner, port=9090)
        await site.start()

    async def liveness_probe(self, request):
        if self.bot.is_ready():
            raise web.HTTPOk()

        raise web.HTTPNotAcceptable()

    async def readiness_probe(self, request):
        if self.connected >= self.bot.config.shards_per_pod:
            raise web.HTTPOk()

        raise web.HTTPNotAcceptable()


def setup(bot):
    bot.add_cog(Api(bot))
