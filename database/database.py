import aiosqlite



DATABASE = "database/bot.db"



async def create_database():


    async with aiosqlite.connect(
        DATABASE
    ) as db:


        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS applications(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            department TEXT,

            channel_id INTEGER

            )
            """
        )


        await db.commit()




async def add_application(

    user_id,

    department,

    channel_id

):


    async with aiosqlite.connect(
        DATABASE
    ) as db:


        await db.execute(

            """
            INSERT INTO applications

            (user_id, department, channel_id)

            VALUES (?, ?, ?)

            """,

            (

                user_id,

                department,

                channel_id

            )

        )


        await db.commit()




async def get_application(channel_id):


    async with aiosqlite.connect(
        DATABASE
    ) as db:


        cursor = await db.execute(

            """
            SELECT user_id

            FROM applications

            WHERE channel_id = ?

            """,

            (
                channel_id,
            )

        )


        result = await cursor.fetchone()


        return result[0] if result else None