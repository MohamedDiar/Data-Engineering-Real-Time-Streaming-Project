-- try.sql
INSTALL 'azure';
SET azure_storage_connection_string = '{connection_string}';
SET azure_transport_option_type = 'curl';
Load 'azure';

SELECT *
FROM read_parquet('azure://' || '{container_name}' || '/aggregates/**/*.parquet');
