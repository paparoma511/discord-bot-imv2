from config import (
    NORULES,
    EVENTS,
    DISCORD,

    NORULES_SLOTS,
    EVENTS_SLOTS,
    DISCORD_SLOTS
)


DEPARTMENTS = {

    "NORULES": {

        "roles": NORULES,

        "slots": NORULES_SLOTS

    },


    "EVENTS": {

        "roles": EVENTS,

        "slots": EVENTS_SLOTS

    },


    "DISCORD": {

        "roles": DISCORD,

        "slots": DISCORD_SLOTS

    }

}



def get_slots(guild, department):


    data = DEPARTMENTS[department]


    count = 0


    for member in guild.members:

        for role in member.roles:

            if role.id in data["roles"]:

                count += 1

                break



    return {

        "used": count,

        "max": data["slots"],

        "free": max(
            data["slots"] - count,
            0
        )

    }





def get_department_slots(guild):


    text = ""


    for name in DEPARTMENTS:


        slots = get_slots(
            guild,
            name
        )


        if slots["free"] > 0:

            emoji = "✅"

        else:

            emoji = "❌"



        text += (

            f"{emoji} **{name}** "

            f"`{slots['used']}/{slots['max']}`\n"

            f"Свободно: `{slots['free']}`\n\n"

        )


    return text