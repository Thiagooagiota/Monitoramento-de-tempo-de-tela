import psycopg
from datetime import date
    
def banco_puxar(data_where):
    DATABASE_URL = 'postgresql://neondb_owner:npg_yhCYPL6JISw9@ep-raspy-thunder-ah9iqt48-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

    conn = psycopg.connect(DATABASE_URL)

    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM tempo_de_tela WHERE data_uso = %s""", (data_where,))
        rows = cur.fetchall()
        
        for row in rows:
            # row[0] é o datetime.date
            app = row[1]
            data = row[2].strftime("%d/%m/%Y")  # Formato: dia/mês/ano
            duracao = str(row[3])
            
            print(f'jogo: {app}, data: {data}, tempo de uso: {duracao}')
        return rows
    conn.close()

def banco_puxar_tudo():
    DATABASE_URL = 'postgresql://neondb_owner:npg_yhCYPL6JISw9@ep-raspy-thunder-ah9iqt48-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

    conn = psycopg.connect(DATABASE_URL)

    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM tempo_de_tela""")
        rows = cur.fetchall()
        
        for row in rows:
            # row[0] é o datetime.date
            app = row[1]
            data = row[2].strftime("%d/%m/%Y")  # Formato: dia/mês/ano
            duracao = str(row[3])
            
            print(f'jogo: {app}, data: {data}, tempo de uso: {duracao}')
        return rows
    conn.close()

def banco_adicionar(app_usado, data_uso, tempo_de_uso):
    DATABASE_URL = 'postgresql://neondb_owner:npg_yhCYPL6JISw9@ep-raspy-thunder-ah9iqt48-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

    conn = psycopg.connect(DATABASE_URL)

    if isinstance(data_uso, date):
        data_uso = data_uso.isoformat()

    # Arredonda para o segundo inteiro mais próximo
    segundos = round(float(tempo_de_uso))          # 24.537 → 25, 38.2 → 38

    # Opcional: arredondar para múltiplos de 5 segundos (mais "redondo")
    # segundos = round(float(tempo_de_uso) / 5) * 5

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO tempo_de_tela (app_usado, data_uso, tempo_de_uso)
            VALUES (%s, %s, make_interval(secs => %s))
            ON CONFLICT (app_usado, data_uso) 
            DO UPDATE SET 
                tempo_de_uso = tempo_de_tela.tempo_de_uso + make_interval(secs => %s)
        """, (app_usado, data_uso, segundos, segundos))

        conn.commit()

    conn.close()