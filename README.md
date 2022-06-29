### Funcionalidade
```sh
    - Metrica de Host (Ativos, inativos, atualizando);
    - Metrica de Serviços (Ativos, inativos, atualizando, rollback);
```
### Variaveis de ambiente
```sh
    Rancher/MySQL:
      - MYSQL_DATABASE
      - MYSQL_USER
      - MYSQL_PASSWORD
      - MYSQL_HOST
    influxDB:
      - INFLUXDB_HOST
      - INFLUXDB_PORT
    Ambiente:
      - ENVIRONMENT
```
### Funções que tem que ter no mariadb
================= FUNCTION IMAGE =======================================
```
CREATE DEFINER=`root`@`localhost` FUNCTION  `json_image`(
details TEXT,
required_field VARCHAR (255)
) RETURNS text CHARSET latin1
BEGIN
SET details = TRIM(LEADING '{' FROM TRIM(details));
SET details = TRIM(TRAILING '}' FROM TRIM(details));
RETURN TRIM(
    BOTH '"' FROM SUBSTRING_INDEX(
        SUBSTRING_INDEX(
            SUBSTRING_INDEX(
                details,
                CONCAT(
                    '"',
                    SUBSTRING_INDEX(required_field,'$.', - 1),
                    '":'
                ),
                - 1
            ),
            ',"',
            1
        ),
        ',',
        -1
    )
) ;
END
```

======================================= FUNCITION EXTRACT =======================================
```
CREATE DEFINER=`root`@`localhost` FUNCTION  `json_extract`(
details TEXT,
required_field VARCHAR (255)
) RETURNS text CHARSET latin1
BEGIN
SET details = TRIM(LEADING '{' FROM TRIM(details));
SET details = TRIM(TRAILING '}' FROM TRIM(details));
RETURN TRIM(
    BOTH '"' FROM SUBSTRING_INDEX(
        SUBSTRING_INDEX(
            SUBSTRING_INDEX(
                details,
                CONCAT(
                    '"',
                    SUBSTRING_INDEX(required_field,'$.', - 1),
                    '":'
                ),
                - 1
            ),
            ',"',
            1
        ),
        '":',
        -1
    )
) ;
END
```
