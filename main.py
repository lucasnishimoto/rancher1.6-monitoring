import mysql.connector, os, schedule
from icecream import ic
from mysql.connector import Error
from influxdb import InfluxDBClient

variaveis = dict(
    MYSQL_HOST=os.environ.get('MYSQL_HOST'),
    MYSQL_DATABASE=os.environ.get('MYSQL_DATABASE'),
    MYSQL_USER=os.environ.get('MYSQL_USER'),
    MYSQL_PASSWORD=os.environ.get('MYSQL_PASSWORD'),
    INFLUXDB_HOST=os.environ.get('INFLUXDB_HOST'),
    INFLUXDB_PORT=os.environ.get('INFLUXDB_PORT'),
    INFLUXDB_DB=os.environ.get('INFLUXDB_DB'),
    ENVIRONMENT=os.environ.get('ENVIRONMENT')
)

con = mysql.connector.connect(host=variaveis['MYSQL_HOST'], database=variaveis['MYSQL_DATABASE'],
                              user=variaveis['MYSQL_USER'], password=variaveis['MYSQL_PASSWORD'])
client = InfluxDBClient(host=variaveis['INFLUXDB_HOST'],
                        port=variaveis['INFLUXDB_PORT'], database=variaveis['INFLUXDB_DB'])


def container_fields():
    try:
        host_query = "SELECT state AS Status, json_image(data, '$.hostname') AS Hostname, json_image(data, '$.agentIpAddress') AS IP FROM host"
        service_query = "SELECT service.name, account.name as environment, service.state as state, \
      service.health_state, json_image(service.data, '$.imageUuid') as Image FROM service INNER JOIN \
      environment ON service.environment_id = environment.ID INNER JOIN account ON environment.account_id = account.id GROUP BY state, environment;"
        cursor = con.cursor()

        cursor.execute(host_query)
        host_rows = cursor.fetchall()
        print(f'Número total de registros retornados: , {cursor.rowcount}')
        print(f'\nMostrando os hosts cadastrados')

        for row in host_rows:
            data = [{
                "measurement": "rancher_host",
                "tags": {
                    "Ambiente": variaveis['ENVIRONMENT']
                },
                "fields": {
                    'State': row[0],
                    'Hostname': row[1],
                    'IP': row[2]
                }
            }]
            ic(data)
            client.write_points(data)

        cursor.execute(service_query)
        service_rows = cursor.fetchall()
        print(f'Número total de registros retornados: , {cursor.rowcount}')
        print(f'\nMostrando os serviços cadastrados')

        for row in service_rows:
            data = [{
                "measurement": "rancher_service",
                "fields": {
                    'Name': row[0],
                    'Environment': row[1],
                    'State': row[2],
                    'Health_state': row[3],
                    'Image': row[4],
                },
                "tags": {
                    "Ambiente": variaveis['ENVIRONMENT']
                }
            }]
            ic(data)
            client.write_points(data)

    except Error as e:
        print(f'Erro ao acessar tabela MySQL, {e}')


def main():
    schedule.every(0.9).minutes.do(container_fields)
    while True:
        schedule.run_pending()


if __name__ == '__main__':
    main()
