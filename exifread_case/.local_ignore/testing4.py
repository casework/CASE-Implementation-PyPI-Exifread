from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, FOAF, XSD

g = Graph()
ex = Namespace("http://example.org/")


# How to represent the address of Cade Tracey. From probably the worst solution to the best.

# Solution 1 -
# Make the entire address into one Literal. However, Generally we want to separate each part of an address into their own triples. This is useful for instance if we want to find only the streets where people live.

g.add((ex.Cade_Tracey, ex.livesIn, Literal("1516_Henry_Street, Berkeley, California 94709, USA")))


# Solution 2 -
# Seperate the different pieces information into their own triples

g.add((ex.Cade_tracey, ex.street, Literal("1516_Henry_Street")))
g.add((ex.Cade_tracey, ex.city, Literal("Berkeley")))
g.add((ex.Cade_tracey, ex.state, Literal("California")))
g.add((ex.Cade_tracey, ex.zipcode, Literal("94709")))
g.add((ex.Cade_tracey, ex.country, Literal("USA")))


# Solution 3 - Some parts of the addresses can make more sense to be resources than Literals.
# Larger concepts like a city or state are typically represented as resources rather than Literals, but this is not necesarilly a requirement in the case that you don't intend to say more about them.

g.add((ex.Cade_tracey, ex.street, Literal("1516_Henry_Street")))
g.add((ex.Cade_tracey, ex.city, ex.Berkeley))
g.add((ex.Cade_tracey, ex.state, ex.California))
g.add((ex.Cade_tracey, ex.zipcode, Literal("94709")))
g.add((ex.Cade_tracey, ex.country, ex.USA))


# Solution 4
# Grouping of the information into an Address. We can Represent the address concept with its own URI OR with a Blank Node.
# One advantage of this is that we can easily remove the entire address, instead of removing each individual part of the address.
# Solution 4 or 5 is how I would recommend to make addresses. Here, ex.CadeAddress could also be called something like ex.address1 or so on, if you want to give each address a unique ID.

# Address URI - CadeAdress

g.add((ex.Cade_Tracey, ex.address, ex.CadeAddress))
g.add((ex.CadeAddress, RDF.type, ex.Address))
g.add((ex.CadeAddress, ex.street, Literal("1516 Henry Street")))
g.add((ex.CadeAddress, ex.city, ex.Berkeley))
g.add((ex.CadeAddress, ex.state, ex.California))
g.add((ex.CadeAddress, ex.postalCode, Literal("94709")))
g.add((ex.CadeAddress, ex.country, ex.USA))

# OR

# Blank node for Address.
address = BNode()
g.add((ex.Cade_Tracey, ex.address, address))
g.add((address, RDF.type, ex.Address))
g.add((address, ex.street, Literal("1516 Henry Street", datatype=XSD.string)))
g.add((address, ex.city, ex.Berkeley))
g.add((address, ex.state, ex.California))
g.add((address, ex.postalCode, Literal("94709", datatype=XSD.string)))
g.add((address, ex.country, ex.USA))


# Solution 5 using existing vocabularies for address

# (in this case https://schema.org/PostalAddress from schema.org).
# Also using existing ontology for places like California. (like http://dbpedia.org/resource/California from dbpedia.org)

schema = Namespace("https://schema.org/")
dbp = Namespace("https://dpbedia.org/resource/")

g.add((ex.Cade_Tracey, schema.address, ex.CadeAddress))
g.add((ex.CadeAddress, RDF.type, schema.PostalAddress))
g.add((ex.CadeAddress, schema.streetAddress, Literal("1516 Henry Street")))
g.add((ex.CadeAddress, schema.addresCity, dbp.Berkeley))
g.add((ex.CadeAddress, schema.addressRegion, dbp.California))
g.add((ex.CadeAddress, schema.postalCode, Literal("94709")))
g.add((ex.CadeAddress, schema.addressCountry, dbp.United_States))

print(g.serialize(format='json-ld').decode("utf-8"))