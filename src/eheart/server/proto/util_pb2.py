# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: eheart/server/proto/util.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1e\x65heart/server/proto/util.proto\x12\x06\x65heart\"M\n\x14GenericScalarOrArray\x12\x10\n\x08isscalar\x18\x01 \x01(\x08\x12#\n\x05value\x18\x02 \x03(\x0b\x32\x14.eheart.GenericValue\"L\n\x0cGenericValue\x12\x0e\n\x04real\x18\x01 \x01(\x02H\x00\x12\x11\n\x07integer\x18\x02 \x01(\x03H\x00\x12\x10\n\x06string\x18\x03 \x01(\tH\x00\x42\x07\n\x05valueb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'eheart.server.proto.util_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _GENERICSCALARORARRAY._serialized_start=42
  _GENERICSCALARORARRAY._serialized_end=119
  _GENERICVALUE._serialized_start=121
  _GENERICVALUE._serialized_end=197
# @@protoc_insertion_point(module_scope)
