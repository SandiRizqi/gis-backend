import psycopg2



def inactive_hotspot(host, database, user, password, port, query):
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, port=port)
    curr = conn.cursor()
    curr.execute(query)
    conn.commit()
    conn.close()
    print("Inactive successfully")