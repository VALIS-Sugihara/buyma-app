from .._client import Client
from ..channels import lyst


Lyst = lyst.Lyst()
Client = Client(Lyst)
Client.search(keywords=["Margiela"])
Client.collect()
Client.exit()