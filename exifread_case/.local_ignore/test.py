# import rdflib.plugins.sparql
# import contextlib
#
# graph = rdflib.Graph()
# n_controlled_dictionary = rdflib.BNode()
# test = ("http://example.name#BobSmith12", "http://xmlns.com/foaf/0.1/knows", "http://example.name#JohnDoe34")
# graph.add(test)
# print(graph)

#import rdflib
#import rdflib_jsonld

from rdflib import Graph, plugin
from rdflib.serializer import Serializer
from SPARQLWrapper import SPARQLWrapper
import pprint




def pop_iri(self, exiftool_iri):
    """
    Returns: (raw_object, printconv_object) from input graphs.

    This function has a side effect of mutating the internal variables:
    * self._kv_dict_raw
    * self._kv_dict_raw
    * self._exiftool_predicate_iris
    The exiftool_iri is removed from each of these dicts and set.
    """
    assert isinstance(exiftool_iri, str)
    v_raw = None
    v_printconv = None
    if exiftool_iri in self._exiftool_predicate_iris:
        self._exiftool_predicate_iris -= {exiftool_iri}
    if exiftool_iri in self._kv_dict_raw:
        v_raw = self._kv_dict_raw.pop(exiftool_iri)
    if exiftool_iri in self._kv_dict_printconv:
        v_printconv = self._kv_dict_printconv.pop(exiftool_iri)
    return (v_raw, v_printconv)


# create a Graph
g = Graph()

# parse in an RDF file hosted on the Internet
result = g.parse("http://www.w3.org/People/Berners-Lee/card")

#result = g.parse({"@id": "something-id", "@type": "something-type", "@value": "something-value"})



# loop through each triple in the graph (subj, pred, obj)
for subj, pred, obj in g:
    print(subj, pred, obj)
    # check if there is at least one triple in the Graph
    if (subj, pred, obj) not in g:
       raise Exception("It better be!")
exit()
# print the number of "triples" in the Graph
print("graph has {} statements.".format(len(g)))
# prints graph has 86 statements.

# print out the entire Graph in the RDF Turtle format
answer = g.serialize(format="json-ld")
s = answer.decode()
print(s)

