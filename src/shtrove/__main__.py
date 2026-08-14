import argparse


def shtrove_argparser():
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--persist-strategy')
    _parser.add_argument('--render-strategy')
    _subparsers = _parser.add_subparsers(required=True)

    # ingest --file <file-name> 
    _ingest = _subparsers.add_parser('ingest')
    _ingest.set_defaults(command_fn=ingest_cmd)
    _ingest.add_argument('file_name', nargs='?')
    _ingest.add_argument('--focus-iri', '-i')
    _ingest.add_argument('--record-iri')
    _ingest.add_argument('--record-mediatype', '-m')
    _ingest.add_argument('--is-supplementary', action='store_true')
    _ingest.add_argument('--is-urgent', action='store_true')
    _ingest.add_argument('--restore-deleted', action='store_true')
    _ingest.add_argument('--extract-strategy')

    # delete --focus-iri <iri>
    _delete = _subparsers.add_parser('delete')
    _delete.set_defaults(command_fn=delete_cmd)
    _delete.add_argument('--focus-iri', '-i')
    _delete.add_argument('--record-iri', '-r')

    # browse <iri>
    _browse = _subparsers.add_parser('browse')
    _browse.set_defaults(command_fn=delete_cmd)
    _browse.add_argument('iri', default='')

    # search <query>
    _search = _subparsers.add_parser('search')
    _search.set_defaults(command_fn=search_cmd)
    _search.add_argument('query', nargs='*')
    _search.add_argument('--index-strategy', '-i')

    return _parser


def ingest_cmd(
    *,  # all keyword-args
    focus_iri: str,
    input_file: str | None = None,
    input_mediatype: str | None = None,
    extract_strategy: str | None = None,
    record_iri: str | None,
    persist_strategy: str | None,
    render_strategy: str | None,
    is_supplementary: bool = False,
    # TODO: expiration_date: datetime.date | None = None,  # default "never"
    restore_deleted: bool = False,
    urgent: bool = False,
) -> None:
    '''ingest: extract + derive + persist + index'''
    # TODO: input_document = ... (from input_file or stdin)
    get_shtrove_strategy(...).ingest(
        focus_iri,
        input_mediatype,
        input_document,
        record_identifier,  # default focus_iri
        is_supplementary,
        # TODO: expiration_date: datetime.date | None = None,  # default "never"
        restore_deleted,
        urgent,
    )


# TODO: delete_cmd
# TODO: browse_cmd
# TODO: search_cmd
# TODO: wire together -- parse args, call command_fn
if __name__ == '__main__':
    _args = shtrove_argparser().parse_args()
    _args.command_fn(**_args)
