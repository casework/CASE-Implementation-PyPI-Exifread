#!/usr/bin/env python3
# -*- coding: utf-8 -*
import json
import os
import hashlib
import argparse
import logging
import typing
import uuid
import warnings

import case_utils.inherent_uuid
import cdo_local_uuid
import exifread
import rdflib
import rdflib.plugins.sparql
from cdo_local_uuid import local_uuid

from case_utils.namespace import NS_RDF, \
    NS_RDFS, NS_UCO_CORE, NS_UCO_OBSERVABLE, \
    NS_UCO_TYPES, NS_UCO_VOCABULARY, NS_XSD

_logger = logging.getLogger(os.path.basename(__file__))


ns_kb = rdflib.Namespace("http://example.org/kb/")


def get_node_iri(
    ns: rdflib.Namespace,
    prefix: str,
    *args: typing.Any,
    facet_class: typing.Optional[rdflib.URIRef] = None,
    uco_object_node: typing.Optional[rdflib.URIRef] = None,
    use_deterministic_uuids: bool = False,
    **kwargs: typing.Any
) -> rdflib.URIRef:
    node_id: typing.Optional[rdflib.URIRef] = None
    if use_deterministic_uuids:
        if uco_object_node is None:
            warnings.warn("get_node_iri() called requesting deterministic UUIDs, but no UcoObject node was provided.")
        else:
            if uco_object_node is None:
                warnings.warn("get_node_iri() called requesting deterministic UUIDs, but no Facet class node was provided.")
            else:
                _node_id = case_utils.inherent_id.get_facet_uriref(uco_object_node, facet_class, namespace=ns)
                # Swap in the requested prefix value.
                _node_uuid = str(_node_id)[-36:]
                node_id = ns[f"{prefix}{_node_uuid}"]

    if node_id is None:
        node_id = ns[f"{prefix}{local_uuid()}"]
    return node_id


def get_file_info(filepath):
    """
    A function to get some basic information about the file application being run against
    :param filepath: The relative path to the image
    :return: A Dictionary with some information about the file
    """
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
    """
    Get the exif information from an image
    :param file: The image file
    :return: Dictionary with the exif from the image
    """
    with open(file, 'rb') as file:
        exif_tags = exifread.process_file(file)
    return exif_tags


def create_exif_dict(tags):
    """
    Creates a Dictionary for next steps TODO: may be possible to remove due to format not being
    required any longer
    :param tags:
    :return:
    """
    exif = {}
    for tag in tags:
        exif[tag] = tags[tag]
    return exif


def n_cyber_object_to_node(graph, *args: typing.Any, use_deterministic_uuids: bool = False, **kwargs: typing.Any):
    """
    Initial function to create nodes for each of the file's facet nodes
    :param graph: rdflib graph object for adding nodes to
    :return: The four nodes for each fo the other functions to fill
    """
    cyber_object = rdflib.URIRef(get_node_iri(ns=ns_kb, prefix="observableobject-"))

    n_raster_facet = rdflib.URIRef(get_node_iri(ns=ns_kb, prefix="rasterpicture-", facet_class=NS_UCO_OBSERVABLE.RasterPictureFacet, uco_object_node=cyber_object, use_deterministic_uuids=use_deterministic_uuids))
    n_file_facet = rdflib.URIRef(get_node_iri(ns=ns_kb, prefix="filefacet-", facet_class=NS_UCO_OBSERVABLE.FileFacet, uco_object_node=cyber_object, use_deterministic_uuids=use_deterministic_uuids))
    n_content_facet = rdflib.URIRef(get_node_iri(ns=ns_kb, prefix="contentfacet-", facet_class=NS_UCO_OBSERVABLE.ContentDataFacet, uco_object_node=cyber_object, use_deterministic_uuids=use_deterministic_uuids))
    n_exif_facet = rdflib.URIRef(get_node_iri(ns=ns_kb, prefix="exiffacet-", facet_class=NS_UCO_OBSERVABLE.EXIFFacet, uco_object_node=cyber_object, use_deterministic_uuids=use_deterministic_uuids))
    graph.add((
        cyber_object,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.ObservableObject
    ))
    graph.add((
        cyber_object,
        NS_UCO_OBSERVABLE.hasChanged,
        rdflib.Literal(False)
    ))
    graph.add((
        cyber_object,
        NS_UCO_CORE.hasFacet,
        n_exif_facet
    ))
    graph.add((
        cyber_object,
        NS_UCO_CORE.hasFacet,
        n_raster_facet
    ))
    graph.add((
        cyber_object,
        NS_UCO_CORE.hasFacet,
        n_file_facet
    ))
    return n_exif_facet, n_raster_facet, n_file_facet, n_content_facet


def filecontent_object_to_node(graph, n_content_facet, file_information, *args: typing.Any, use_deterministic_uuids: bool = False, **kwargs: typing.Any):
    """
    Unused: Create a node that will add the file content facet node to the graph
    :param graph: rdflib graph object for adding nodes to
    :param n_content_facet: Node to contain all content facet information
    :param file_information: Dictionary containing information about file being analysed
    :return: None
    """
    graph.add((
        n_content_facet,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.ContentDataFacet
    ))
    graph.add((
        n_content_facet,
        NS_UCO_OBSERVABLE.byteOrder,
        rdflib.Literal("Big-endian", datatype=NS_UCO_VOCABULARY.EndiannessTypeVocab)
    ))
    if 'mimetype' in file_information.keys():
        graph.add((
            n_content_facet,
            NS_UCO_OBSERVABLE.mimeType,
            rdflib.Literal(file_information["mimetype"])
        ))
    if 'size' in file_information.keys():
        graph.add((
            n_content_facet,
            NS_UCO_OBSERVABLE.sizeInBytes,
            rdflib.term.Literal(file_information["size"],
                                datatype=NS_XSD.integer)
        ))

    if "SHA256" in file_information:
        hash_method = rdflib.Literal("SHA256", datatype=NS_UCO_VOCABULARY.HashNameVocab)
        hash_value = rdflib.Literal(file_information["SHA256"], datatype=NS_XSD.hexBinary)

        file_hash: rdflib.URIRef
        if use_deterministic_uuids:
            file_hash_uuid: uuid.UUID = case_utils.inherent_uuid.hash_method_value_uuid(hash_method, hash_value, namespace=ns_kb)
            file_hash = ns_kb["hash-" + str(file_hash_uuid)]
        else:
            file_hash = get_node_iri(ns=ns_kb, prefix="hash-")

        graph.add((
            n_content_facet,
            NS_UCO_OBSERVABLE.hash,
            file_hash
        ))
        graph.add((
            file_hash,
            NS_RDF.type,
            NS_UCO_TYPES.Hash
        ))
        graph.add((
            file_hash,
            NS_UCO_TYPES.hashMethod,
            hash_method
        ))
        graph.add((
            file_hash,
            NS_UCO_TYPES.hashValue,
            hash_value
        ))


def filefacets_object_to_node(graph, n_file_facet, file_information):
    """
    Adding file facet object to the graph object
    :param graph: rdflib graph object for adding nodes to
    :param n_file_facet: file facet node to add facets of file to
    :param file_information: Dictionary containing information about file being analysed
    :return: None
    """
    file_name, ext = os.path.splitext(file_information['Filename'])
    file_ext = ext[1:]
    graph.add((
        n_file_facet,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.FileFacet
    ))
    graph.add((
        n_file_facet,
        NS_UCO_OBSERVABLE.fileName,
        rdflib.Literal(os.path.basename(file_information["Filename"]))
    ))
    graph.add((
        n_file_facet,
        NS_UCO_OBSERVABLE.filePath,
        rdflib.Literal(os.path.abspath(file_information["Filename"]))
    ))
    graph.add((
        n_file_facet,
        NS_UCO_OBSERVABLE.extension,
        rdflib.Literal(file_ext)
    ))
    if 'size' in file_information.keys():
        graph.add((
            n_file_facet,
            NS_UCO_OBSERVABLE.sizeInBytes,
            rdflib.term.Literal(file_information["size"],
                                datatype=NS_XSD.integer)
        ))


def raster_object_to_node(graph, controlled_dict, n_raster_facet, file_information):
    """
    Adding file's raster facet objects to the graph object
    :param graph: rdflib graph object for adding nodes to
    :param controlled_dict: Dictionary containing the EXIF information from image
    :param n_raster_facet: raster facet node to add raster facets of file to
    :param file_information: Dictionary containing information about file being analysed
    :return: None
    """
    file_name, ext = os.path.splitext(file_information['Filename'])
    file_ext = ext[1:]
    graph.add((
        n_raster_facet,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.RasterPictureFacet
    ))
    graph.add((
        n_raster_facet,
        NS_UCO_OBSERVABLE.pictureType,
        rdflib.Literal(file_ext)
    ))
    # :TODO The below feels a bit hacky probably a better way to do it
    if 'EXIF ExifImageLength' in controlled_dict.keys():
        graph.add((
            n_raster_facet,
            NS_UCO_OBSERVABLE.pictureHeight,
            rdflib.term.Literal(int(float(str(controlled_dict['EXIF ExifImageLength']))),
                                datatype=NS_XSD.integer)
        ))
    if 'EXIF ExifImageWidth' in controlled_dict.keys():
        graph.add((
            n_raster_facet,
            NS_UCO_OBSERVABLE.pictureWidth,
            rdflib.term.Literal(int(float(str(controlled_dict['EXIF ExifImageWidth']))),
                                datatype=NS_XSD.integer)
        ))
    if 'EXIF CompressedBitsPerPixel' in controlled_dict.keys():
        graph.add((
            n_raster_facet,
            NS_UCO_OBSERVABLE.bitsPerPixel,
            rdflib.term.Literal(int(float(str(controlled_dict['EXIF CompressedBitsPerPixel']))),
                                datatype=NS_XSD.integer)
        ))
    graph.add((
        n_raster_facet,
        NS_RDFS.comment,
        rdflib.Literal("Information represented here from exif information not from "
                       "file system stats except for extension, which uses os python lib")
    ))


def controlled_dictionary_object_to_node(graph, controlled_dict, n_exif_facet):
    """
    Add controlled dictionary object to accept all Values in the extracted exif
    :param graph: rdflib graph object for adding nodes to
    :param controlled_dict: Dictionary containing the EXIF information from image
    :param n_exif_facet:
    :return: None
    """
    n_controlled_dictionary = rdflib.URIRef(get_node_iri(ns=ns_kb, prefix="controlleddict-"))
    graph.add((
        n_exif_facet,
        NS_RDF.type,
        NS_UCO_OBSERVABLE.EXIFFacet
    ))
    graph.add((
        n_exif_facet,
        NS_UCO_OBSERVABLE.exifData,
        n_controlled_dictionary
    ))
    graph.add((
        n_controlled_dictionary,
        NS_RDF.type,
        NS_UCO_TYPES.ControlledDictionary
    ))
    for key in sorted(controlled_dict.keys()):
        # :TODO stringing all values to ensure they are strings, open to input
        # here as maybe assertion or a better way to do this
        v_value = str(controlled_dict[key])
        v_value = rdflib.Literal(v_value)
        try:
            assert isinstance(v_value, rdflib.Literal)
        except AssertionError:
            _logger.info(f"v_value = {v_value}")
            raise
        n_entry = rdflib.URIRef(get_node_iri(ns=ns_kb, prefix="controlleddictionaryentry-"))
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
    """
    Main function to run the application
    :return: prints out the case file - TODO: write to file instead
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="file to extract exif data from")
    parser.add_argument(
        "--use-deterministic-uuids",
        action="store_true",
        help="Use UUIDs computed using the case_utils.inherent_uuid module.",
    )
    args = parser.parse_args()
    local_file = args.file
    file_info = get_file_info(local_file)
    tags = get_exif(local_file)
    tag_dict = create_exif_dict(tags)
    cdo_local_uuid.configure()
    out_graph = rdflib.Graph()
    exif_facet_node, raster_facet_node, file_facet_node, content_facet_node \
        = n_cyber_object_to_node(out_graph)
    controlled_dictionary_object_to_node(out_graph, tag_dict, exif_facet_node)
    filefacets_object_to_node(out_graph, file_facet_node, file_info)
    raster_object_to_node(out_graph, tag_dict, raster_facet_node, file_info)

    context = {"kb": "http://example.org/kb/",
               "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
               "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
               "uco-core": "https://ontology.unifiedcyberontology.org/uco/core/",
               "uco-observable": "https://ontology.unifiedcyberontology.org/uco/observable/",
               "uco-types": "https://ontology.unifiedcyberontology.org/uco/types/",
               "xsd": "http://www.w3.org/2001/XMLSchema#"}
    graphed = out_graph.serialize(format='json-ld', context=context)

    parsed = json.loads(graphed)
    print(json.dumps(parsed, indent=4))


if __name__ == "__main__":
    main()
