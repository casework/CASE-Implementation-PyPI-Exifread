#!/usr/bin/env python3
# -*- coding: utf-8 -*
import json
import os
import hashlib
import argparse
import logging
import exifread
import rdflib
import rdflib.plugins.sparql
import rdflib_jsonld

_logger = logging.getLogger(os.path.basename(__file__))

parser = argparse.ArgumentParser()
parser.add_argument("file", help="file to extract exif data from")
args = parser.parse_args()

NS_RDF = rdflib.RDF
NS_RDFS = rdflib.RDFS
NS_UCO_CORE = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/core#")
NS_UCO_LOCATION = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/location#")
NS_UCO_OBSERVABLE = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/observable#")
NS_UCO_TYPES = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/types#")
NS_UCO_VOCABULARY = rdflib.Namespace("https://unifiedcyberontology.org/ontology/uco/vocabulary#")
NS_XSD = rdflib.namespace.XSD


def file_information(filepath):
    try:
        md5sum = hashlib.md5(open(filepath, "rb").read())
        file_stats = os.stat(filepath)
        print(f'File_name:          {filepath}')
        print(f'Size:               {file_stats.st_size}')
        print(f'MD5:                {md5sum.hexdigest()} \n')
    except IOError as io_e:
        print(io_e)
    except ValueError as v_e:
        print(v_e)


def get_exif(file):
    file = open(file, 'rb')
    exif_tags = exifread.process_file(file)
    file.close()
    return exif_tags


def create_exif_dict(tags):
    exif = {}
    for tag in tags:
        exif[tag] = tags[tag]
    return exif


def controlled_dictionary_object_to_node(graph, controlled_dict):
    n_controlled_dictionary = rdflib.BNode()
    graph.add((
      n_controlled_dictionary,
      NS_RDF.type,
      NS_UCO_TYPES.ControlledDictionary
    ))
    for key in sorted(controlled_dict.keys()):
        v_value = controlled_dict[key]
        v_value = rdflib.Literal(v_value)
        try:
            assert isinstance(v_value, rdflib.Literal)
        except:
            _logger.info("v_value = %r." % v_value)
            raise
        n_entry = rdflib.BNode()
        graph.add((
          n_controlled_dictionary,
          NS_UCO_TYPES.entry,
          n_entry
        ))
        graph.add((
          n_entry,
          NS_RDF.type,
          NS_UCO_TYPES.ControlledDictionaryEntry
        ))
        graph.add((
          n_entry,
          NS_UCO_TYPES.key,
          rdflib.Literal(key)
        ))
        graph.add((
          n_entry,
          NS_UCO_TYPES.value,
          v_value
        ))
    return n_controlled_dictionary


if __name__ == "__main__":
    tags = get_exif(args.file)
    tag_dict = create_exif_dict(tags)
    out_graph = rdflib.Graph()
    out_graph.namespace_manager.bind("uco-core", NS_UCO_CORE)
    out_graph.namespace_manager.bind("uco-location", NS_UCO_LOCATION)
    out_graph.namespace_manager.bind("uco-observable", NS_UCO_OBSERVABLE)
    out_graph.namespace_manager.bind("uco-types", NS_UCO_TYPES)
    out_graph.namespace_manager.bind("uco-vocabulary", NS_UCO_VOCABULARY)
    controlled_dictionary_object_to_node(out_graph, tag_dict)

context = {"kb": "http://example.org/kb/",
           "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
           "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
           "uco-core": "https://unifiedcyberontology.org/ontology/uco/core#",
           "uco-location": "https://unifiedcyberontology.org/ontology/uco/location#",
           "uco-observable": "https://unifiedcyberontology.org/ontology/uco/observable#",
           "uco-types": "https://unifiedcyberontology.org/ontology/uco/types#",
           "xsd": "http://www.w3.org/2001/XMLSchema#"}

graphed = out_graph.serialize(format='json-ld', context=context, indent=4, sort_keys=True)
data = json.loads(graphed)
pretty = json.dumps(data, indent=4)
print(pretty)



