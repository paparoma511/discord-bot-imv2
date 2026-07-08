import discord

from config import ADMIN_ROLE_IDS



def is_admin(member: discord.Member):

    return any(

        role.id in ADMIN_ROLE_IDS

        for role in member.roles

    )