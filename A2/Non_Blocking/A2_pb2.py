# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: A2.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x08\x41\x32.proto\")\n\rServerDetails\x12\n\n\x02ip\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\t\"\x1d\n\rClientDetails\x12\x0c\n\x04UUID\x18\x01 \x01(\t\"-\n\nServerList\x12\x1f\n\x07servers\x18\x01 \x03(\x0b\x32\x0e.ServerDetails\"-\n\nClientList\x12\x1f\n\x07\x63lients\x18\x01 \x03(\x0b\x32\x0e.ClientDetails\";\n\x0cWriteRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\x12\x0c\n\x04UUID\x18\x03 \x01(\t\"R\n\x12WriteRequestServer\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\x12\x0c\n\x04UUID\x18\x03 \x01(\t\x12\x0f\n\x07version\x18\x04 \x01(\t\">\n\rWriteResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0c\n\x04UUID\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t\"\x19\n\tRDRequest\x12\x0c\n\x04UUID\x18\x01 \x01(\t\"N\n\x0cReadResponse\x12\x0e\n\x06status\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\x12\x0f\n\x07version\x18\x04 \x01(\t\"4\n\x13\x44\x65leteRequestServer\x12\x0c\n\x04UUID\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\"\x1a\n\x08Response\x12\x0e\n\x06status\x18\x01 \x01(\t\"\x07\n\x05\x45mpty2l\n\x0eRegistryServer\x12\x32\n\x0eRegisterServer\x12\x0e.ServerDetails\x1a\x0e.ServerDetails\"\x00\x12&\n\rGetServerList\x12\x06.Empty\x1a\x0b.ServerList\"\x00\x32\xe6\x02\n\x06Server\x12+\n\x0fSendJoiningInfo\x12\x0e.ServerDetails\x1a\x06.Empty\"\x00\x12(\n\x05Write\x12\r.WriteRequest\x1a\x0e.WriteResponse\"\x00\x12/\n\x0cWritePrimary\x12\r.WriteRequest\x1a\x0e.WriteResponse\"\x00\x12/\n\x0bWriteServer\x12\x13.WriteRequestServer\x1a\t.Response\"\x00\x12#\n\x04Read\x12\n.RDRequest\x1a\r.ReadResponse\"\x00\x12!\n\x06\x44\x65lete\x12\n.RDRequest\x1a\t.Response\"\x00\x12(\n\rDeletePrimary\x12\n.RDRequest\x1a\t.Response\"\x00\x12\x31\n\x0c\x44\x65leteServer\x12\x14.DeleteRequestServer\x1a\t.Response\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'A2_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SERVERDETAILS._serialized_start=12
  _SERVERDETAILS._serialized_end=53
  _CLIENTDETAILS._serialized_start=55
  _CLIENTDETAILS._serialized_end=84
  _SERVERLIST._serialized_start=86
  _SERVERLIST._serialized_end=131
  _CLIENTLIST._serialized_start=133
  _CLIENTLIST._serialized_end=178
  _WRITEREQUEST._serialized_start=180
  _WRITEREQUEST._serialized_end=239
  _WRITEREQUESTSERVER._serialized_start=241
  _WRITEREQUESTSERVER._serialized_end=323
  _WRITERESPONSE._serialized_start=325
  _WRITERESPONSE._serialized_end=387
  _RDREQUEST._serialized_start=389
  _RDREQUEST._serialized_end=414
  _READRESPONSE._serialized_start=416
  _READRESPONSE._serialized_end=494
  _DELETEREQUESTSERVER._serialized_start=496
  _DELETEREQUESTSERVER._serialized_end=548
  _RESPONSE._serialized_start=550
  _RESPONSE._serialized_end=576
  _EMPTY._serialized_start=578
  _EMPTY._serialized_end=585
  _REGISTRYSERVER._serialized_start=587
  _REGISTRYSERVER._serialized_end=695
  _SERVER._serialized_start=698
  _SERVER._serialized_end=1056
# @@protoc_insertion_point(module_scope)
