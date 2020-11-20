"""
holds informative type of commands
"""
from world.conditions import DetectInvis
from evennia import EvForm
from evennia.utils import evmore, crop
from evennia.utils.utils import inherits_from
from commands.command import Command
from world.utils.act import Announce, act
from world.utils.utils import can_see_obj, is_book, is_equipment, is_equipped, is_invis, is_obj, can_pickup, is_wielded, is_worn


class CmdAffect(Command):
    """
    Shows current affects on you

    Usage:
        affect
    """

    key = 'affect'
    aliases = ['af']

    def func(self):
        ch = self.caller

        conditions = ch.conditions.conditions
        traits = ch.traits.traits
        ch.msg("You are affected by the following:\n")
        msg = "Conditions:\n"
        # conditions
        for con in conditions:
            msg += f"|g{str(con).replace('_', ' ').capitalize()}|n\n"

        # traits
        msg += "\nTraits:\n"
        for trait in traits:
            msg += f"|g{str(trait).replace('_', ' ').capitalize()}|n\n"

        ch.msg(msg)
        #spells


class CmdRead(Command):
    """
    Books are enjoyable to read no matter
    who or where you hail from. Grab a book,
    pick a spot, and let it take you away on
    an adventure.

    Usage:
        read <bookname>
        read <num>.book
    """

    key = 'read'

    def func(self):
        def show_book(book):
            title = book.db.title
            author = book.db.author
            contents = book.db.contents
            date = book.db.date

            book_contents = f"\n|gTitle|w: {title}\n|gAuthor|w: {author}\n|gDate|w: {date}\n\n|n{contents}"
            evmore.msg(ch, book_contents)

        ch = self.caller
        if not self.args:
            ch.msg("what do you want to read?")
            return

        obj_name = self.args.strip()
        pos, book = None, None
        if "." in obj_name:
            pos, book = obj_name.split('.')
            if book != 'book':
                ch.msg("if using dot expression, you must use book")
                return
            try:
                pos = int(pos)
            except:
                ch.msg("not a valid position number")
                return
        cntr = 1
        for obj in ch.contents:

            if is_book(obj):
                if obj_name in obj.db.name and not pos and not book:  # using object name instead of dot expression
                    show_book(obj)
                    return
                else:
                    # assume we are using dot expression
                    if cntr == pos:
                        show_book(obj)
                        return
                    cntr += 1
        ch.msg("You couldn't find anything to read")


class CmdEquipment(Command):
    """
    view currently worn equipment

    Usage:
        eq
        equipment
    """

    key = 'equipment'
    aliases = ['equip', 'eq']
    locks = "cmd:all()"

    def func(self):
        ch = self.caller
        wear_loc = ch.equipment._valid_wear_loc

        # # equipment
        table = self.styled_table(border=None)
        for loc in wear_loc:
            obj = ch.equipment.location[loc.name]
            if is_obj(obj):
                if not can_see_obj(ch, obj):
                    sdesc = "|C<something>|n"
                else:
                    sdesc = obj.obj_desc()
            else:
                sdesc = "|Mnothing|n"
            table.add_row(loc.display_msg, sdesc)

        msg = f"You are using\n{table}"
        ch.msg(msg)


class CmdInventory(Command):
    """
    view inventory
    Usage:
      inventory
      inv
    Shows your inventory.
    """

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """check inventory"""
        ch = self.caller
        items = list(ch.contents)
        if not items:
            string = "You are not carrying anything."
        else:
            from evennia.utils.ansi import raw as raw_ansi

            items.sort(key=lambda x: x.db.sdesc.lower())
            table = self.styled_table(border="header")
            for item in items:
                if is_worn(item) or is_wielded(item):
                    continue

                if not can_see_obj(ch, item):
                    sdesc = "<something>"
                else:
                    sdesc = f"{item.obj_desc()}"
                table.add_row("{}|n".format(raw_ansi(sdesc)))
            string = f"|wYou are carrying:\n{table}"
        ch.msg(string)


class CmdLook(Command):
    """
    Look at location of object

    Usage:
        look
        look <obj>
        look <character>

    """

    key = "look"
    aliases = ['l', 'ls']
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        ch = self.caller
        if not self.args:
            target = ch.location
            if not target:
                ch.msg("You have no location to look at!")
                return

            room_msg = ""

            # get room title
            room_msg += f"|c{target.name}|n\n"

            #get room_desc
            room_msg += f"|G{target.db.desc}|n\n\n"

            # get room exits

            # get room contents
            # get objects
            for obj in target.contents:
                if inherits_from(obj, 'typeclasses.characters.Character'):
                    if obj.id == ch.id:
                        continue
                    room_msg += f"{obj.name.capitalize()}\n"
                if is_obj(obj):
                    if is_invis(obj) and not ch.conditions.has(DetectInvis):
                        continue
                    else:
                        room_msg += f"{obj.obj_desc()}\n"
            ch.msg(room_msg)
            return

        # try looking for obj in room based on name or aliases
        obj_name = self.args.strip()
        for obj in ch.location.contents:
            if obj.db.name:
                if obj_name in obj.db.name:
                    ch.msg(obj.db.edesc)
                    return
        # try looking for an obj in your inventory, if found send back edesc
        for obj in ch.contents:
            if is_equipped(obj):
                continue
            if obj_name in obj.db.name:
                ch.msg(obj.db.edesc)
                return
        ch.msg("You don't see anything like that.")

        # self.msg((ch.at_look(target), {"type": "look"}), options=None)


class CmdScore(Command):
    """
    show information about yourself

    Usage:
        score
    """

    key = 'score'
    locks = "cmd:all()"

    def func(self):
        ch = self.caller

        def green_or_red(num):
            if num < 0:
                return f"|r{num}|n"
            elif num > 0:
                return f"|g{num}|n"
            else:
                return f"{num}"

        #TODO change path to EvForm to  use
        form = EvForm("resources.score_form")
        form.map({
            1: ch.name.capitalize(),
            2: ch.stats.str.base,
            3: green_or_red(ch.stats.str.bonus),
            4: ch.stats.agi.base,
            5: green_or_red(ch.stats.agi.bonus),
            6: ch.stats.end.base,
            7: green_or_red(ch.stats.end.bonus),
            8: ch.stats.wp.base,
            9: green_or_red(ch.stats.wp.bonus),
            10: ch.attrs.level.value,
            11: ch.stats.lck.base,
            12: green_or_red(ch.stats.lck.bonus),
            13: ch.stats.int.base,
            14: green_or_red(ch.stats.int.bonus),
            15: ch.stats.prs.base,
            16: green_or_red(ch.stats.prs.bonus),
            17: ch.stats.prc.base,
            18: green_or_red(ch.stats.prc.bonus),
            19: str(ch.attrs.birthsign.value),
            20: ch.attrs.race.value.name.capitalize(),
            21: ch.attrs.gender.value.value.capitalize()
        })
        ch.msg(form)
