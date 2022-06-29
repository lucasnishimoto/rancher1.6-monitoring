import mysql.connector, os, time, schedule
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

con = mysql.connector.connect(host=variaveis['MYSQL_HOST'],database=variaveis['MYSQL_DATABASE'],user=variaveis['MYSQL_USER'],password=variaveis['MYSQL_PASSWORD'])
client = InfluxDBClient(host=variaveis['INFLUXDB_HOST'],port=variaveis['INFLUXDB_PORT'], database=variaveis['INFLUXDB_DB'])

##############################################HOST########################################################################

def host():
  try:
      consulta_sql = "SELECT json_image(data, '$.hostname'), json_image(data, '$.agentIpAddress') FROM host"
      cursor = con.cursor()
      cursor.execute(consulta_sql)
      linhas = cursor.fetchall()
      print("Número total de registros retornados: ", cursor.rowcount)
      print("\nMostrando os hosts cadastrados")
      for linha in linhas:
          print("Hostname:", linha[0])
          print("IP:", linha[1], "\n")
      for linha in linhas:
        data = [{
             "measurement": "host",
            "fields": {
                  "Ambiente": variaveis['ENVIRONMENT']
             },
            "tags": {
              'Hostname': linha[0],
              'Ips': linha[1]
            }
        }]
        client.write_points(data) 
  except Error as e:
      print("Erro ao acessar tabela MySQL", e)
##############################################SERVICE########################################################################
def service():
  try:
      consulta_sql = "SELECT name, state, health_state, json_image(data, '$.imageUuid') FROM service;"
      cursor = con.cursor()
      cursor.execute(consulta_sql)
      linhas = cursor.fetchall()
      print("Número total de registros retornados: ", cursor.rowcount)
      print("\nMostrando os serviços cadastrados")
      for linha in linhas:
        print('Name:', linha[0])
        print('State:', linha[1])
        print('Health_state:', linha[2])
        print('Image:', linha[3])
      for linha in linhas:
        data = [{
             "measurement": "service",
             "tags": {
                  'Name': linha[0],
                  'State': linha[1],
                  'Health_state': linha[2],
                  'Image': linha[3],
             },
             "fields": {
                  "Ambiente": variaveis['ENVIRONMENT']
             }
        }]
        client.write_points(data) 
  except Error as e:
      print("Erro ao acessar tabela MySQL", e)

schedule.every(1).minutes.do(host)
schedule.every(1).minutes.do(service)
while True:
    schedule.run_pending()
    time.sleep(1)