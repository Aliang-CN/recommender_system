# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: AutoRecall/proto/recall_param.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from AutoRecall.proto import common_param_pb2 as AutoRecall_dot_proto_dot_common__param__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='AutoRecall/proto/recall_param.proto',
  package='proto',
  syntax='proto3',
  serialized_options=b'Z\020AutoRecall/proto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n#AutoRecall/proto/recall_param.proto\x12\x05proto\x1a#AutoRecall/proto/common_param.proto\"r\n\x0bRecallParam\x12\r\n\x05Label\x18\x01 \x01(\t\x12*\n\rResourceInfos\x18\x02 \x03(\x0b\x32\x13.proto.ResourceInfo\x12(\n\nUserPrefix\x18\x03 \x01(\x0b\x32\x14.proto.UserKeyPrefix\"8\n\x0cXRecallParam\x12(\n\x0cRecallParams\x18\x01 \x03(\x0b\x32\x12.proto.RecallParamB\x12Z\x10\x41utoRecall/protob\x06proto3'
  ,
  dependencies=[AutoRecall_dot_proto_dot_common__param__pb2.DESCRIPTOR,])




_RECALLPARAM = _descriptor.Descriptor(
  name='RecallParam',
  full_name='proto.RecallParam',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='Label', full_name='proto.RecallParam.Label', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ResourceInfos', full_name='proto.RecallParam.ResourceInfos', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='UserPrefix', full_name='proto.RecallParam.UserPrefix', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=83,
  serialized_end=197,
)


_XRECALLPARAM = _descriptor.Descriptor(
  name='XRecallParam',
  full_name='proto.XRecallParam',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='RecallParams', full_name='proto.XRecallParam.RecallParams', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=199,
  serialized_end=255,
)

_RECALLPARAM.fields_by_name['ResourceInfos'].message_type = AutoRecall_dot_proto_dot_common__param__pb2._RESOURCEINFO
_RECALLPARAM.fields_by_name['UserPrefix'].message_type = AutoRecall_dot_proto_dot_common__param__pb2._USERKEYPREFIX
_XRECALLPARAM.fields_by_name['RecallParams'].message_type = _RECALLPARAM
DESCRIPTOR.message_types_by_name['RecallParam'] = _RECALLPARAM
DESCRIPTOR.message_types_by_name['XRecallParam'] = _XRECALLPARAM
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

RecallParam = _reflection.GeneratedProtocolMessageType('RecallParam', (_message.Message,), {
  'DESCRIPTOR' : _RECALLPARAM,
  '__module__' : 'AutoRecall.proto.recall_param_pb2'
  # @@protoc_insertion_point(class_scope:proto.RecallParam)
  })
_sym_db.RegisterMessage(RecallParam)

XRecallParam = _reflection.GeneratedProtocolMessageType('XRecallParam', (_message.Message,), {
  'DESCRIPTOR' : _XRECALLPARAM,
  '__module__' : 'AutoRecall.proto.recall_param_pb2'
  # @@protoc_insertion_point(class_scope:proto.XRecallParam)
  })
_sym_db.RegisterMessage(XRecallParam)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
