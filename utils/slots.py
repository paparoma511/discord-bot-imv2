from config import (

    NORULES,
    EVENTS,
    DISCORD,

    NORULES_SLOTS,
    EVENTS_SLOTS,
    DISCORD_SLOTS

)



def get_department_slots(guild):


    departments = {


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



    text = ""



    for name, data in departments.items():


        count = 0



        for member in guild.members:


            for role in member.roles:


                if role.id in data["roles"]:

                    count += 1

                    break




        slots = data["slots"]



        if count >= slots:


            emoji = "❌"

            status = "Мест нет"



        else:


            emoji = "✅"

            status = f"Свободно мест: {slots-count}"




        text += (

            f"{emoji} **{name}** — "

            f"`{count}/{slots}`\n"

            f"└ {status}\n\n"

        )



    return text