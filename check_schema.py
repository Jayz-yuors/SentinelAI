from ai.database.postgres.connection import get_connection


def main():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'sentinelai_analysis'
            ORDER BY ordinal_position
            """
        )

        rows = cursor.fetchall()

        print("\nSENTINELAI_ANALYSIS TABLE SCHEMA\n")
        print("-" * 60)

        for column_name, data_type in rows:
            print(f"{column_name:<25} {data_type}")

        print("-" * 60)

        cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    main()