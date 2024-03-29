from discord.ext import commands as cmd
import asyncio


async def async_cursor_to_list(cursor):
    result = []
    while await cursor.fetch_next():
        result.append(await cursor.next())

    return result


def datetime_to_string(datetime):
    return datetime.strftime("%d. %b %Y - %H:%M")


def clean_content(content):
    content = content.replace("@everyone", "@\u200beveryone")
    content = content.replace("@here", "@\u200bhere")
    return content


def format_number(number):
    return "{:,}".format(number)


async def ask_question(ctx, question, converter=str):
    question_msg = await ctx.send(**ctx.em(question, type="wait_for"))
    try:
        msg = await ctx.bot.wait_for(
            event="message",
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            timeout=60
        )

    except asyncio.TimeoutError:
        raise cmd.CommandError("**Canceled template creation**, because you didn't respond.")

    else:
        try:
            return converter(msg.content)
        except ValueError:
            convert_name = str(converter).replace("int", "number").replace("float", "decimal number")
            raise cmd.CommandError(f"`{msg.content}` is **not a valid {convert_name}**.")

        finally:
            try:
                await msg.delete()
            except Exception:
                pass

    finally:
        await question_msg.delete()
