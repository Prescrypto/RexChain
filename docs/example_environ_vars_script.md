## Ejemplo variables de entorno
================================

```
#!/bin/bash

echo "-------- Setting environmental variables into ~/.profile..."
source ~/.profile

# DEBUG_STATE
if [ -z "$DEBUG_STATE" ] || [ "$DEBUG_STATE" != True ]; then
  echo "export DEBUG_STATE=True" >> ~/.profile
fi
# SECRET_KEY
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" != "SomeKeyEncrypted123/&$/%&(=" ]; then
  echo "export SECRET_KEY='SomeKeyEncrypted123/&$/%&(='" >> ~/.profile
fi
# AUTO_MIGRATE
if [ -z "$AUTO_MIGRATE" ] || [ "$AUTO_MIGRATE" != False ]; then
  echo "export AUTO_MIGRATE=False" >> ~/.profile
fi
# LOAD_FIXTURES
if [ -z "$LOAD_FIXTURES" ] || [ "$LOAD_FIXTURES" != False ]; then
  echo "export LOAD_FIXTURES=False" >> ~/.profile
fi
# DATABASE_URL
if [ -z "$DATABASE_URL" ] || [ "$DATABASE_URL" != 'postgres://cxuko:cxuko@localhost/mydb' ]; then
  echo "export DATABASE_URL='postgres://cxuko:cxuko@localhost/mydb'" >> ~/.profile
fi

echo "DONE"

```




## Ejemplo de activarlas
$ sudo chmod +x ./config/environ_variables.sh
$ ./config/environ_variables.sh