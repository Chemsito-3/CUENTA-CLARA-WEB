# conftest.py - Simula módulos externos para las pruebas
import sys
from unittest.mock import MagicMock

# Simula mysql
mock_mysql = MagicMock()
sys.modules['mysql']                   = mock_mysql
sys.modules['mysql.connector']         = mock_mysql
sys.modules['mysql.connector.pooling'] = mock_mysql

# Simula jwt
mock_jwt = MagicMock()
sys.modules['jwt'] = mock_jwt