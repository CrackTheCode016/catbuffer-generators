type_name_mappings = {
    "UnresolvedAddress": "binary",
    "Address": "binary",
    "Hash256": "binary",
    "Hash512": "binary",
    "MosaicId": "uint64HexIdentifier",
    "UnresolvedMosaicId": "uint64HexIdentifier",
    "Key": "binary",
    "Amount": "uint64",
    "Signature": "uint64",
    "Timestamp": "uint64",
    "AccountLinkAction": "uint64"
}

schema_name_mappings = {
    "TransferTransactionBody": "transfer",
    "SecretLockTransactionBody": "lockSecret",
    "AccountLinkTransactionBodyPlugin": "accountLink",
    "HashLockTransactionBody": "lockHash",
    "NamespaceRegistrationTransactionBody": "namespace",
    "MultisigAccountModificationTransactionBody": "multisig",
    "MosaicDefinitionTransactionBody": "mosaic",
}


def set_type(entity):
    entity_type = entity['type']
    if entity_type in type_name_mappings:
        entity_type = type_name_mappings[entity['type']]
    return entity_type


def set_schema_name(schema):
    schema_type = schema
    if schema_type in schema_name_mappings:
        schema_type = schema_name_mappings[schema]
    return schema_type
