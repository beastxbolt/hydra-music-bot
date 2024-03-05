import json

def prefix(bot, ctx):
    if str(ctx.channel.type) == "private":
        default_prefix = [".", f"<@!{bot.user.id}>"]
        return default_prefix

    with open("./prefix.json", "r") as f:
        prefixes = json.load(f)
        id = str(ctx.guild.id)
        default_prefix = prefixes["default_prefix"]
    return prefixes.get(id, default_prefix)