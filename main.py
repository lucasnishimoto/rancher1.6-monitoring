import mysql.connector
import os
import schedule
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


def host():
    try:
        consulta_sql = "SELECT state AS Status, json_image(data, '$.hostname') AS Hostname, json_image(data, '$.agentIpAddress') AS IP FROM host"
        cursor = con.cursor()
        cursor.execute(consulta_sql)
        linhas = cursor.fetchall()
        print(f'Número total de registros retornados: , {cursor.rowcount}')
        print(f'\nMostrando os hosts cadastrados')

        for linha in linhas:
            data = [{
                "measurement": "rancher_host",
                "tags": {
                    "Ambiente": variaveis['ENVIRONMENT']
                },
                "fields": {
                    'State': linha[0],
                    'Hostname': linha[1],
                    'IP': linha[2]
                }
            }]
            ic(data)
            client.write_points(data)
    except Error as e:
        print(f'Erro ao acessar tabela MySQL, {e}')
######################################################################################################################


def service():
    try:
        consulta_sql = "select service.name, account.name as environment, service.state as state, \
      service.health_state, json_image(service.data, '$.imageUuid') as Image from service 	inner join \
      environment on service.environment_id = environment.ID inner join account on environment.account_id = account.id group by state, environment;"
        cursor = con.cursor()
        cursor.execute(consulta_sql)
        linhas = cursor.fetchall()
        print(f'Número total de registros retornados: , {cursor.rowcount}')
        print(f'\nMostrando os serviços cadastrados')
        for linha in linhas:
            data = [{
                "measurement": "rancher_service",
                "fields": {
                    'Name': linha[0],
                    'Environment': linha[1],
                    'State': linha[2],
                    'Health_state': linha[3],
                    'Image': linha[4],
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
    schedule.every(0.9).minutes.do(host)
    schedule.every(0.9).minutes.do(service)
    while True:
        schedule.run_pending()


if __name__ == '__main__':
    main()
