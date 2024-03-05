from discord.ext import commands
import contextlib
import io
import textwrap
import traceback


class _eval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')


    @commands.command(name="eval")
    async def _eval(self, ctx, *, code: str):
        """Evaluates a snippet of Python code."""

        # Define some environment vars for the function.
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result
        }

        env.update(globals())

        # Clean up the code and define our 'stdout'.
        cleaned_code = self.cleanup_code(code)
        stdout = io.StringIO()

        # Wrap the code into a async function.
        to_compile = f"async def func():\n{textwrap.indent(cleaned_code, '  ')}"

        # try to 'compile' the function.
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env["func"]
        try:
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            await ctx.message.add_reaction("\U00002705")

            if ret is None:
                if value:
                    await ctx.send(f"```py\n{value}\n```")
            else:
                self._last_result = ret
                await ctx.send(f"```py\n{value}{ret}\n```")


def setup(bot):
    bot.add_cog(_eval(bot))