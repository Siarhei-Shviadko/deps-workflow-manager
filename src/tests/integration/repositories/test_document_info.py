import pytest


@pytest.mark.pipelines
def test_save_document_processing_info__ok(document_processing_info_repo, document_processing_info):
    document_processing_info_repo.save(document_processing_info)

    saved_info = document_processing_info_repo.find(
        document_processing_info.document_id, document_processing_info.tenant_id
    )

    assert document_processing_info == saved_info


@pytest.mark.pipelines
def test_save_document_processing_info_twice__no_error_no_updates(
    document_processing_info_repo, document_processing_info
):
    document_processing_info_repo.save(document_processing_info)
    document_processing_info.needs_extraction = not (document_processing_info.needs_extraction)

    document_processing_info_repo.save(document_processing_info)
    info_from_db = document_processing_info_repo.find(
        document_processing_info.document_id, document_processing_info.tenant_id
    )

    assert info_from_db.needs_extraction != document_processing_info.needs_extraction


@pytest.mark.pipelines
def test_find_document_proccessing_info__ok(document_processing_info_repo, saved_document_processing_info):
    info = document_processing_info_repo.find(
        saved_document_processing_info.document_id, saved_document_processing_info.tenant_id
    )
    assert info is not None


@pytest.mark.pipelines
def test_find_document_proccessing_info__no_info__no_errors(document_processing_info_repo):
    document_processing_info_repo.find("1", "tenanat")


@pytest.mark.pipelines
def test_delete_document_processing_info_twice__error(document_processing_info_repo, saved_document_processing_info):
    document_processing_info_repo.delete(
        saved_document_processing_info.document_id, saved_document_processing_info.tenant_id
    )
    result = document_processing_info_repo.find(
        saved_document_processing_info.document_id, saved_document_processing_info.tenant_id
    )

    assert result is None


@pytest.mark.pipelines
def test_delete_document_proccessing_info__no_info__no_errors(document_processing_info_repo):
    document_processing_info_repo.delete("1", "tenanat")
