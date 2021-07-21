#!/usr/bin/env python3
# -*- coding: utf-8 -*
import json
import os
import hashlib
import argparse
import logging
import exifread
import rdflib
import rdflib_jsonld

import rdflib.plugins.sparql
# import mimetypes

__version__ = "0.1.0"

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


def get_file_info(filepath):
    file_information = {}
    try:
        sha256 = hashlib.sha256(open(filepath, "rb").read())
        file_stats = os.stat(filepath)
        file_information['Filename'] = filepath
        file_information['size'] = file_stats.st_size
        file_information['SHA256'] = sha256.hexdigest()
    except IOError as io_e:
        print(io_e)
    except ValueError as v_e:
        print(v_e)
    return file_information


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


def n_cyber_object_to_node(graph):
    cyber_object_facet = rdflib.BNode()
    n_raster_facets = rdflib.BNode()
    n_controlled_dictionary = rdflib.BNode()
    n_file_facets = rdflib.BNode()
    n_content_facets = rdflib.BNode()
    graph.add((
        cyber_object_facet,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.ObservableObject
    ))
    graph.add((
        cyber_object_facet,
        NS_UCO_CORE.hasFacet,
        n_controlled_dictionary
    ))
    graph.add((
        cyber_object_facet,
        NS_UCO_CORE.hasFacet,
        n_raster_facets
    ))
    return n_controlled_dictionary, n_raster_facets, n_file_facets, n_content_facets


def filecontent_object_to_node(graph, n_file_facets, file_information):
    byte_order_facet = rdflib.BNode()
    file_hash_facet = rdflib.BNode()
    graph.add((
        n_file_facets,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.ContentDataFacet
    ))
    graph.add((
        n_file_facets,
        NS_UCO_OBSERVABLE.byteOrder,
        byte_order_facet
    ))
    graph.add((
        byte_order_facet,
        NS_RDF.type,
        NS_UCO_VOCABULARY.EndiannessTypeVocab,
    ))
    graph.add((
        byte_order_facet,
        NS_UCO_VOCABULARY.value,
        rdflib.Literal("Big-endian")
    ))
    if 'mimetype' in file_information.keys():
        graph.add((
            n_file_facets,
            NS_UCO_OBSERVABLE.mimeType,
            rdflib.Literal(file_information["mimetype"])
        ))
    if 'size' in file_information.keys():
        graph.add((
            n_file_facets,
            NS_UCO_OBSERVABLE.sizeInBytes,
            rdflib.term.Literal(file_information["size"],
                                datatype=NS_XSD.integer)
        ))
    graph.add((
        n_file_facets,
        NS_UCO_OBSERVABLE.hash,
        file_hash_facet
    ))
    graph.add((
        file_hash_facet,
        NS_RDF.type,
        NS_UCO_TYPES.Hash
    ))


def raster_object_to_node(graph, controlled_dict, n_raster_facets, file_information):
    file_name, ext = os.path.splitext(file_information['Filename'])
    file_ext = ext[1:]
    graph.add((
        n_raster_facets,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.RasterPictureFacet
    ))
    graph.add((
        n_raster_facets,
        NS_UCO_OBSERVABLE.pictureType,
        rdflib.Literal(file_ext)
    ))
    if 'EXIF ExifImageLength' in controlled_dict.keys():
        graph.add((
            n_raster_facets,
            NS_UCO_OBSERVABLE.pictureHeight,
            rdflib.term.Literal(str(controlled_dict['EXIF ExifImageLength']),
                                datatype=NS_XSD.integer)
        ))
    if 'EXIF ExifImageWidth' in controlled_dict.keys():
        graph.add((
            n_raster_facets,
            NS_UCO_OBSERVABLE.pictureWidth,
            rdflib.term.Literal(str(controlled_dict['EXIF ExifImageWidth']),
                                datatype=NS_XSD.integer)
        ))
    if 'EXIF CompressedBitsPerPixel' in controlled_dict.keys():
        graph.add((
            n_raster_facets,
            NS_UCO_OBSERVABLE.bitsPerPixel,
            rdflib.term.Literal(str(controlled_dict['EXIF CompressedBitsPerPixel']),
                                datatype=NS_XSD.integer)
        ))
    graph.add((
        n_raster_facets,
        NS_RDFS.comment,
        rdflib.Literal("Information represented here from exif information not from "
                       "file system stats except for extension, which uses os python lib")
    ))


def controlled_dictionary_object_to_node(graph, controlled_dict, n_controlled_dictionary):
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


def main():
    local_file = args.file
    file_info = get_file_info(local_file)
    tags = get_exif(local_file)
    tag_dict = create_exif_dict(tags)
    out_graph = rdflib.Graph()
    out_graph.namespace_manager.bind("uco-core", NS_UCO_CORE)
    out_graph.namespace_manager.bind("uco-location", NS_UCO_LOCATION)
    out_graph.namespace_manager.bind("uco-observable", NS_UCO_OBSERVABLE)
    out_graph.namespace_manager.bind("uco-types", NS_UCO_TYPES)
    out_graph.namespace_manager.bind("uco-vocabulary", NS_UCO_VOCABULARY)
    controlled_dictionary_node, raster_facets_node, file_facets_node, content_facets \
        = n_cyber_object_to_node(out_graph)
    controlled_dictionary_object_to_node(out_graph, tag_dict, controlled_dictionary_node)
    raster_object_to_node(out_graph, tag_dict, raster_facets_node, file_info)

    context = {"kb": "http://example.org/kb/",
               "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
               "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
               "uco-core": "https://unifiedcyberontology.org/ontology/uco/core#",
               "uco-location": "https://unifiedcyberontology.org/ontology/uco/location#",
               "uco-observable": "https://unifiedcyberontology.org/ontology/uco/observable#",
               "uco-types": "https://unifiedcyberontology.org/ontology/uco/types#",
               "xsd": "http://www.w3.org/2001/XMLSchema#"}

    graphed = out_graph.serialize(format='json-ld', context=context)

    doc = json.loads(graphed.decode('utf-8'))
    case_json = json.dumps(doc, indent=4)
    print(case_json)


if __name__ == "__main__":
    main()
