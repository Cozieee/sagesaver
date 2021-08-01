from enum import Enum
from sagesaver.entities.factories import *
from ..installation import *

class EntityTypes(Enum):
	NOTEBOOK = ('notebook', 'Notebook', NotebookFactory, NotebookInstallation)
	MYSQL = ('mysql', 'MySQL', MysqlFactory, MysqlInstallation)
	MONGO = ('mongo', 'Mongo', MongoFactory, MongoInstallation)
	USER = ('user', 'User', UserFactory, None)

	def __init__(self, label, name, factory, installation):
		self.label = label
		self.name = name
		self.factory = factory
		self.installation = installation
		
	def __str__(self):
		return self.name