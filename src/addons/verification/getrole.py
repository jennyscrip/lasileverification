from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error
from discord import Embed
from resources.exceptions import Message, UserNotVerified, Error, BloxlinkBypass, Blacklisted, PermissionError # pylint: disable=import-error
from resources.constants import GREEN_COLOR, VERIFY_URL # pylint: disable=import-error

format_update_embed, guild_obligations = Bloxlink.get_module("roblox", attrs=["format_update_embed", "guild_obligations"])
get_options = Bloxlink.get_module("trello", attrs="get_options")
post_event = Bloxlink.get_module("utils", attrs=["post_event"])



class GetRoleCommand(Bloxlink.Module):
    """get your server roles"""

    def __init__(self):
        self.category = "Account"
        self.cooldown = 5
        self.aliases = ["getroles", "get-roles", "get-role"]
        self.slash_enabled = True
        self.slash_ack = True

    @Bloxlink.flags
    async def __main__(self, CommandArgs):
        trello_board = CommandArgs.trello_board
        guild_data = CommandArgs.guild_data
        guild = CommandArgs.guild
        author = CommandArgs.author
        response = CommandArgs.response
        prefix = CommandArgs.prefix

        trello_options = {}

        if trello_board:
            trello_options, _ = await get_options(trello_board)
            guild_data.update(trello_options)

        try:
            old_nickname = author.display_name

            added, removed, nickname, errors, warnings, roblox_user = await guild_obligations(
                author,
                guild                = guild,
                guild_data           = guild_data,
                roles                = True,
                nickname             = True,
                trello_board         = CommandArgs.trello_board,
                cache                = False,
                response             = response,
                dm                   = False,
                exceptions           = ("BloxlinkBypass", "Blacklisted", "UserNotVerified", "PermissionError", "RobloxDown", "RobloxAPIError")
            )

        except BloxlinkBypass:
            raise Message("Since you have the `Bloxlink Bypass` role, I was unable to update your roles/nickname.", type="info")

        except Blacklisted as b:
            if isinstance(b.message, str):
                raise Error(f"{author.mention} has an active restriction for: `{b}`")
            else:
                raise Error(f"{author.mention} has an active restriction from Bloxlink.")

        except UserNotVerified:
            await response.reply("To verify with Bloxlink, please visit our website at "
                                f"<{VERIFY_URL}>. It won't take long!\nStuck? See this video: <https://www.youtube.com/watch?v=hq496NmQ9GU>", hidden=True)

        except PermissionError as e:
            raise Error(e.message)

        else:
            welcome_message, embed = await format_update_embed(roblox_user, author, added=added, removed=removed, errors=errors, warnings=warnings, nickname=nickname if old_nickname != nickname else None, prefix=prefix, guild_data=guild_data)

            await post_event(guild, guild_data, "verification", f"{author.mention} ({author.id}) has **verified** as `{roblox_user.username}`.", GREEN_COLOR)

            await response.send(content=welcome_message, embed=embed, mention_author=True)
