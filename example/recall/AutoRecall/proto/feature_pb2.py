# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: AutoRecall/proto/feature.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='AutoRecall/proto/feature.proto',
  package='proto',
  syntax='proto3',
  serialized_options=b'Z\020AutoRecall/proto',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1e\x41utoRecall/proto/feature.proto\x12\x05proto\":\n\x0c\x46\x65\x61tureValue\x12\x0c\n\x04Vals\x18\x01 \x03(\x03\x12\r\n\x05\x44vals\x18\x02 \x03(\x01\x12\r\n\x05Svals\x18\x03 \x03(\t\"Z\n\x07\x46\x65\x61ture\x12\x0c\n\x04\x46Tag\x18\x01 \x01(\t\x12\r\n\x05\x46Type\x18\x02 \x01(\x05\x12\x0f\n\x07MulVals\x18\x03 \x01(\x05\x12!\n\x04\x46val\x18\x04 \x01(\x0b\x32\x13.proto.FeatureValue\"I\n\x0ePrefictFeature\x12\x10\n\x08num_cols\x18\x01 \x03(\t\x12\x11\n\tcate_cols\x18\x02 \x03(\t\x12\x12\n\nmulti_cols\x18\x03 \x03(\tB\x12Z\x10\x41utoRecall/protob\x06proto3'
)




_FEATUREVALUE = _descriptor.Descriptor(
  name='FeatureValue',
  full_name='proto.FeatureValue',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='Vals', full_name='proto.FeatureValue.Vals', index=0,
      number=1, type=3, cpp_type=2, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='Dvals', full_name='proto.FeatureValue.Dvals', index=1,
      number=2, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='Svals', full_name='proto.FeatureValue.Svals', index=2,
      number=3, type=9, cpp_type=9, label=3,
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
  serialized_start=41,
  serialized_end=99,
)


_FEATURE = _descriptor.Descriptor(
  name='Feature',
  full_name='proto.Feature',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='FTag', full_name='proto.Feature.FTag', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='FType', full_name='proto.Feature.FType', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='MulVals', full_name='proto.Feature.MulVals', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='Fval', full_name='proto.Feature.Fval', index=3,
      number=4, type=11, cpp_type=10, label=1,
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
  serialized_start=101,
  serialized_end=191,
)


_PREFICTFEATURE = _descriptor.Descriptor(
  name='PrefictFeature',
  full_name='proto.PrefictFeature',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='num_cols', full_name='proto.PrefictFeature.num_cols', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='cate_cols', full_name='proto.PrefictFeature.cate_cols', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='multi_cols', full_name='proto.PrefictFeature.multi_cols', index=2,
      number=3, type=9, cpp_type=9, label=3,
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
  serialized_start=193,
  serialized_end=266,
)

_FEATURE.fields_by_name['Fval'].message_type = _FEATUREVALUE
DESCRIPTOR.message_types_by_name['FeatureValue'] = _FEATUREVALUE
DESCRIPTOR.message_types_by_name['Feature'] = _FEATURE
DESCRIPTOR.message_types_by_name['PrefictFeature'] = _PREFICTFEATURE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FeatureValue = _reflection.GeneratedProtocolMessageType('FeatureValue', (_message.Message,), {
  'DESCRIPTOR' : _FEATUREVALUE,
  '__module__' : 'AutoRecall.proto.feature_pb2'
  # @@protoc_insertion_point(class_scope:proto.FeatureValue)
  })
_sym_db.RegisterMessage(FeatureValue)

Feature = _reflection.GeneratedProtocolMessageType('Feature', (_message.Message,), {
  'DESCRIPTOR' : _FEATURE,
  '__module__' : 'AutoRecall.proto.feature_pb2'
  # @@protoc_insertion_point(class_scope:proto.Feature)
  })
_sym_db.RegisterMessage(Feature)

PrefictFeature = _reflection.GeneratedProtocolMessageType('PrefictFeature', (_message.Message,), {
  'DESCRIPTOR' : _PREFICTFEATURE,
  '__module__' : 'AutoRecall.proto.feature_pb2'
  # @@protoc_insertion_point(class_scope:proto.PrefictFeature)
  })
_sym_db.RegisterMessage(PrefictFeature)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
