from enum import Enum
from sagesaver.entities.factories import *
from .installation import *

class EntityTypes(Enum):
	NOTEBOOK = ('notebook', 'Notebook', NotebookFactory, NotebookInstallation)
	MYSQL = ('mysql', 'MySQL', MysqlFactory, MysqlInstallation)
	MONGO = ('mongo', 'Mongo', MongoFactory, MongoInstallation)
	USER = ('user', 'User', UserFactory, None)
	SEED = ('seed', None, None, None)

	def __init__(self, label, title, factory, installation):
		self.label = label
		self.title = title
		self.factory = factory
		self.installation = installation
		
	def __str__(self):
		return self.title