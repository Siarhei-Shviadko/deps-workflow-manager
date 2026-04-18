import random
from uuid import uuid4

import factory
from faker import Faker
from faker_enum import EnumProvider
from pytest_factoryboy import register

from deps_workflow_manager.domain.model import Document, DocumentState

fake = Faker()
fake.add_provider(EnumProvider)

__all__ = ["DocumentFactory"]


@register
class DocumentFactory(factory.Factory):
    class Meta:
        model = Document

    id_ = uuid4().hex
    type_id = uuid4().hex
    title = factory.Faker("file_name")
    state = fake.enum(DocumentState)
    files = factory.LazyFunction(lambda: list([factory.Faker("file_path") for i in range(random.randint(1, 3))]))
    error_in_state = fake.enum(DocumentState)

    language = "eng"
    engine = "TESSERACT"
